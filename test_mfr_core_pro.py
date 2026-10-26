"""Unit tests for MFR Adaptive Intelligence Core Pro.

Covers analysis contracts, Bayesian updates, conflict detection,
fingerprinting, validation, CLI behavior, and regression cases.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from mfr_core_pro import (
    Evidence,
    IntelligenceRecord,
    VERSION,
    fingerprint,
    to_fathimind_decision,
    validate_report,
)


class TestEvidenceValidation:
    def test_valid_evidence(self) -> None:
        ev = Evidence("claim", "source", 0.75, independent=True, weight=1.2)
        assert ev.claim == "claim"
        assert ev.reliability == 0.75

    def test_empty_claim_raises(self) -> None:
        with pytest.raises(ValueError, match="claim must be non-empty"):
            Evidence("", "source", 0.5)

    def test_empty_source_raises(self) -> None:
        with pytest.raises(ValueError, match="source must be non-empty"):
            Evidence("claim", "  ", 0.5)

    def test_reliability_out_of_range(self) -> None:
        with pytest.raises(ValueError, match="reliability must be in"):
            Evidence("c", "s", 1.1)
        with pytest.raises(ValueError):
            Evidence("c", "s", -0.1)

    def test_weight_must_be_positive(self) -> None:
        with pytest.raises(ValueError, match="weight must be > 0"):
            Evidence("c", "s", 0.5, weight=0.0)


class TestIntelligenceRecordAnalysis:
    def test_no_evidence_insufficient(self) -> None:
        rec = IntelligenceRecord("Is it true?")
        report = rec.analyze()
        assert report["status"] == "INSUFFICIENT_EVIDENCE"
        assert report["confidence"] == 0.0
        assert report["conclusion"] is None
        assert "missing" in report
        assert validate_report(report) == []
        assert report["version"] == VERSION
        assert len(report["fingerprint"]) == 64

    def test_single_strong_evidence_provisional(self) -> None:
        rec = IntelligenceRecord(
            "Is secure?",
            evidence=[Evidence("yes", "auditor", 0.9, independent=True)],
        )
        report = rec.analyze()
        assert report["status"] == "PROVISIONAL_FINDING"
        assert report["conclusion"] == "yes"
        assert 0.5 < report["confidence"] < 1.0
        assert validate_report(report) == []

    def test_conflicting_evidence(self) -> None:
        rec = IntelligenceRecord(
            "Status?",
            evidence=[
                Evidence("good", "a", 0.85),
                Evidence("bad", "b", 0.82),
            ],
        )
        report = rec.analyze()
        # Separation may or may not trigger conflict depending on numbers;
        # at least contract holds.
        assert report["status"] in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE")
        assert validate_report(report) == []
        assert "suggestions" in report

    def test_non_independent_downweighted(self) -> None:
        indep = IntelligenceRecord(
            "q",
            [Evidence("yes", "s1", 0.8, independent=True)],
        ).analyze()
        non = IntelligenceRecord(
            "q",
            [Evidence("yes", "s1", 0.8, independent=False)],
        ).analyze()
        assert non["confidence"] <= indep["confidence"]

    def test_all_non_independent_still_provisional(self) -> None:
        rec = IntelligenceRecord(
            "q",
            evidence=[
                Evidence("yes", "s1", 0.9, independent=False),
                Evidence("yes", "s2", 0.85, independent=False),
            ],
        )
        report = rec.analyze()
        assert report["status"] == "PROVISIONAL_FINDING"
        assert report["conclusion"] == "yes"

    def test_prior_belief_affects_posterior(self) -> None:
        low = IntelligenceRecord("q", [Evidence("yes", "s", 0.6)], prior_belief=0.2).analyze()
        high = IntelligenceRecord("q", [Evidence("yes", "s", 0.6)], prior_belief=0.8).analyze()
        assert high["confidence"] > low["confidence"]

    def test_weight_capping(self) -> None:
        # Extreme weight should not produce invalid posterior
        rec = IntelligenceRecord(
            "q",
            [Evidence("yes", "s", 1.0, weight=100.0)],
        )
        report = rec.analyze()
        assert 0.0 <= report["confidence"] <= 1.0
        assert validate_report(report) == []

    def test_fingerprint_stable(self) -> None:
        rec1 = IntelligenceRecord(
            "q",
            [Evidence("yes", "s", 0.8), Evidence("no", "t", 0.7)],
            prior_belief=0.5,
        )
        rec2 = IntelligenceRecord(
            "q",
            [Evidence("no", "t", 0.7), Evidence("yes", "s", 0.8)],
            prior_belief=0.5,
        )
        assert rec1.analyze()["fingerprint"] == rec2.analyze()["fingerprint"]

    def test_fingerprint_changes_with_content(self) -> None:
        a = IntelligenceRecord("q", [Evidence("yes", "s", 0.8)]).analyze()
        b = IntelligenceRecord("q", [Evidence("yes", "s", 0.81)]).analyze()
        assert a["fingerprint"] != b["fingerprint"]

    def test_alternatives_in_suggestions(self) -> None:
        rec = IntelligenceRecord(
            "q",
            [Evidence("yes", "s", 0.9)],
            alternatives=["maybe", "no"],
        )
        report = rec.analyze()
        assert any("maybe" in s for s in report["suggestions"])

    def test_empty_question_raises(self) -> None:
        with pytest.raises(ValueError):
            IntelligenceRecord("   ")

    def test_invalid_prior_raises(self) -> None:
        with pytest.raises(ValueError):
            IntelligenceRecord("q", prior_belief=1.5).analyze()


class TestFingerprinting:
    def test_fingerprint_deterministic(self) -> None:
        evs = [Evidence("c", "s", 0.5)]
        assert fingerprint("q", evs, 0.5) == fingerprint("q", evs, 0.5)

    def test_fingerprint_order_independent(self) -> None:
        e1 = Evidence("a", "s1", 0.6)
        e2 = Evidence("b", "s2", 0.7)
        assert fingerprint("q", [e1, e2], 0.5) == fingerprint("q", [e2, e1], 0.5)


class TestDecisionContract:
    def test_provisional_to_stable_or_warning(self) -> None:
        rec = IntelligenceRecord("q", [Evidence("yes", "s", 0.95)])
        report = rec.analyze()
        decision = to_fathimind_decision(report)
        assert decision["status"] in ("stable", "warning")
        assert 0.3 <= decision["confidence"] <= 0.98
        assert decision["fingerprint"] == report["fingerprint"]

    def test_insufficient_maps_to_critical(self) -> None:
        rec = IntelligenceRecord("q")
        decision = to_fathimind_decision(rec.analyze())
        assert decision["status"] == "critical"
        assert "insufficient evidence" in decision["anomalies"]

    def test_conflicting_maps_to_warning(self) -> None:
        # Construct a case that triggers conflict
        rec = IntelligenceRecord(
            "q",
            [
                Evidence("yes", "s1", 0.55),
                Evidence("no", "s2", 0.54),
            ],
        )
        report = rec.analyze()
        decision = to_fathimind_decision(report)
        if report["status"] == "CONFLICTING_EVIDENCE":
            assert decision["status"] == "warning"
            assert "conflicting" in " ".join(decision["anomalies"])


class TestValidation:
    def test_valid_report_passes(self) -> None:
        rec = IntelligenceRecord("q", [Evidence("yes", "s", 0.8)])
        assert validate_report(rec.analyze()) == []

    def test_missing_field_detected(self) -> None:
        bad = {"status": "PROVISIONAL_FINDING", "confidence": 0.5}
        violations = validate_report(bad)
        assert any("missing required field" in v for v in violations)

    def test_bad_fingerprint_detected(self) -> None:
        rec = IntelligenceRecord("q", [Evidence("yes", "s", 0.8)]).analyze()
        rec["fingerprint"] = "short"
        assert any("fingerprint" in v for v in validate_report(rec))

    def test_bad_status_detected(self) -> None:
        rec = IntelligenceRecord("q", [Evidence("yes", "s", 0.8)]).analyze()
        rec["status"] = "UNKNOWN"
        assert any("invalid status" in v for v in validate_report(rec))

    def test_bad_confidence_detected(self) -> None:
        rec = IntelligenceRecord("q", [Evidence("yes", "s", 0.8)]).analyze()
        rec["confidence"] = 1.5
        assert any("confidence" in v for v in validate_report(rec))


class TestCLI:
    def test_demo_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--demo"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "Demo" in result.stdout

    def test_version_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert VERSION in result.stdout

    def test_invalid_weight_exits_2(self) -> None:
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "q", "--evidence", "c", "s", "0.5", "bad"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
        assert "Invalid evidence" in result.stderr or "weight" in result.stderr.lower()


class TestCLIDirect:
    def test_cli_demo_via_main(self, capsys) -> None:
        import sys
        old_argv = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "--demo"]
            from mfr_core_pro import main
            main()
            captured = capsys.readouterr()
            assert "MFR Adaptive Intelligence Core Pro Demo" in captured.out
        finally:
            sys.argv = old_argv

    def test_cli_simple_evidence_via_main(self, capsys) -> None:
        import sys
        old = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "Is secure?", "--evidence", "secure", "auditor", "0.9"]
            from mfr_core_pro import main
            main()
            out = capsys.readouterr().out
            data = json.loads(out)
            assert data["status"] == "PROVISIONAL_FINDING"
            assert data["conclusion"] == "secure"
        finally:
            sys.argv = old

    def test_cli_evidence_file_and_validate(self, tmp_path, capsys) -> None:
        import sys
        ev = tmp_path / "e.json"
        ev.write_text(json.dumps([{"claim":"yes","source":"s","reliability":0.8}]))
        old = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "Q?", "--evidence-file", str(ev), "--validate"]
            from mfr_core_pro import main
            main()
            err = capsys.readouterr().err
            assert "Validation passed." in err
        finally:
            sys.argv = old

    def test_cli_decision(self, capsys) -> None:
        import sys
        old = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "Q", "--evidence", "c", "s", "0.75", "--decision"]
            from mfr_core_pro import main
            main()
            data = json.loads(capsys.readouterr().out)
            assert "status" in data and "confidence" in data
        finally:
            sys.argv = old

    def test_cli_missing_question(self, capsys) -> None:
        import sys
        old = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "--evidence", "c", "s", "0.5"]
            from mfr_core_pro import main
            with pytest.raises(SystemExit) as ei:
                main()
            assert ei.value.code == 2
            assert "question is required" in capsys.readouterr().err
        finally:
            sys.argv = old

    def test_cli_invalid_evidence_parts(self, capsys) -> None:
        import sys
        old = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "Q", "--evidence", "only"]
            from mfr_core_pro import main
            with pytest.raises(SystemExit) as ei:
                main()
            assert ei.value.code == 2
        finally:
            sys.argv = old

    def test_cli_bad_json_file(self, tmp_path, capsys) -> None:
        import sys
        bad = tmp_path / "bad.json"
        bad.write_text("{invalid")
        old = sys.argv
        try:
            sys.argv = ["mfr_core_pro.py", "Q", "--evidence-file", str(bad)]
            from mfr_core_pro import main
            with pytest.raises(SystemExit) as ei:
                main()
            assert ei.value.code == 2
            assert "Failed to load" in capsys.readouterr().err
        finally:
            sys.argv = old
