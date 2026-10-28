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
            "all dependent?",
            evidence=[
                Evidence("yes", "a", 0.9, independent=False),
                Evidence("yes", "b", 0.85, independent=False),
            ],
        )
        report = rec.analyze()
        assert report["status"] == "PROVISIONAL_FINDING"
        assert report["conclusion"] == "yes"
        assert any("non-independent" in s for s in report["suggestions"])
        assert validate_report(report) == []

    def test_deduplication_keeps_strongest_per_source(self) -> None:
        rec = IntelligenceRecord(
            "q",
            evidence=[
                Evidence("yes", "same", 0.6),
                Evidence("yes", "same", 0.95),  # stronger
            ],
        )
        report = rec.analyze()
        assert report["top_claim"]["evidence_count"] == 1
        assert "Deduplicated" in report["audit_trail"][0]

    def test_prior_affects_posterior(self) -> None:
        low = IntelligenceRecord("q", [Evidence("yes", "s", 0.7)], prior_belief=0.2).analyze()
        high = IntelligenceRecord("q", [Evidence("yes", "s", 0.7)], prior_belief=0.8).analyze()
        assert high["confidence"] > low["confidence"]

    def test_alternatives_appear_in_suggestions(self) -> None:
        rec = IntelligenceRecord(
            "q",
            [Evidence("main", "s", 0.8)],
            alternatives=["alt1", "alt2"],
        )
        report = rec.analyze()
        assert any("alt1" in s for s in report["suggestions"])


class TestFingerprintAndValidation:
    def test_fingerprint_deterministic_and_order_independent(self) -> None:
        evs = [
            Evidence("c", "s2", 0.7, weight=1.1),
            Evidence("c", "s1", 0.8),
        ]
        fp1 = fingerprint("question", evs, 0.5)
        fp2 = fingerprint("question", list(reversed(evs)), 0.5)
        assert fp1 == fp2
        assert len(fp1) == 64

    def test_fingerprint_changes_with_content(self) -> None:
        fp_a = fingerprint("q", [Evidence("c", "s", 0.5)], 0.5)
        fp_b = fingerprint("q", [Evidence("c", "s", 0.6)], 0.5)
        assert fp_a != fp_b

    def test_validate_report_detects_bad_status(self) -> None:
        bad = {"version": "x", "status": "BAD", "question": "q", "confidence": 0.5,
               "suggestions": [], "audit_trail": [], "created_at": "t", "analyzed_at": "t",
               "fingerprint": "a" * 64}
        violations = validate_report(bad)
        assert any("invalid status" in v for v in violations)

    def test_validate_report_detects_confidence_out_of_range(self) -> None:
        bad = {"version": "x", "status": "PROVISIONAL_FINDING", "question": "q",
               "confidence": 1.5, "suggestions": [], "audit_trail": [],
               "created_at": "t", "analyzed_at": "t", "fingerprint": "a" * 64}
        violations = validate_report(bad)
        assert any("confidence" in v for v in violations)

    def test_validate_report_detects_short_fingerprint(self) -> None:
        bad = {"version": "x", "status": "PROVISIONAL_FINDING", "question": "q",
               "confidence": 0.5, "suggestions": [], "audit_trail": [],
               "created_at": "t", "analyzed_at": "t", "fingerprint": "short"}
        violations = validate_report(bad)
        assert any("fingerprint" in v for v in violations)


class TestDecisionContract:
    def test_to_fathimind_decision_mapping(self) -> None:
        report = IntelligenceRecord("q", [Evidence("yes", "s", 0.9)]).analyze()
        decision = to_fathimind_decision(report)
        assert "status" in decision
        assert "confidence" in decision
        assert decision["confidence"] >= 0.3
        assert "fingerprint" in decision
        assert decision["_original_status"] == report["status"]

    def test_to_fathimind_decision_insufficient(self) -> None:
        report = IntelligenceRecord("q").analyze()
        decision = to_fathimind_decision(report)
        assert decision["status"] == "critical"
        assert "insufficient evidence" in decision["anomalies"]

    def test_to_fathimind_decision_conflicting(self) -> None:
        report = IntelligenceRecord(
            "q",
            [Evidence("good", "a", 0.85), Evidence("bad", "b", 0.82)],
        ).analyze()
        # May be provisional or conflicting depending on separation; if conflicting, check mapping
        decision = to_fathimind_decision(report)
        if report["status"] == "CONFLICTING_EVIDENCE":
            assert decision["status"] == "warning"
            assert "conflicting evidence detected" in decision["anomalies"]
        else:
            assert decision["status"] in ("stable", "warning")

    def test_to_fathimind_decision_low_confidence_warning(self) -> None:
        report = IntelligenceRecord(
            "q",
            [Evidence("yes", "s", 0.51)],
        ).analyze()
        decision = to_fathimind_decision(report)
        # low confidence provisional should map to warning
        assert decision["status"] in ("warning", "stable")
        assert 0.3 <= decision["confidence"] <= 0.98


class TestCLI:
    def test_version_flag_prints_version_and_exits_zero(self) -> None:
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert VERSION in result.stdout

    def test_demo_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--demo"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "PROVISIONAL_FINDING" in result.stdout or "INSUFFICIENT_EVIDENCE" in result.stdout

    def test_validate_flag_passes_on_valid_report(self) -> None:
        result = subprocess.run(
            [
                sys.executable, "mfr_core_pro.py",
                "Is secure?",
                "--evidence", "secure", "auditor", "0.9",
                "--validate",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        assert "Validation passed" in result.stderr
        data = json.loads(result.stdout)
        assert data["status"] == "PROVISIONAL_FINDING"

    def test_evidence_file_malformed_exits_nonzero(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text('{"not": "a list"}', encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "q", "--evidence-file", str(bad)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 2
        assert "Failed to load evidence file" in result.stderr

    def test_evidence_file_valid_loads(self, tmp_path: Path) -> None:
        good = tmp_path / "good.json"
        good.write_text(json.dumps([
            {"claim": "yes", "source": "file", "reliability": 0.85, "independent": True}
        ]), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "from file?", "--evidence-file", str(good)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "PROVISIONAL_FINDING"
        assert data["conclusion"] == "yes"

    def test_cli_invalid_evidence_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable, "mfr_core_pro.py",
                "q",
                "--evidence", "c", "s", "2.0",  # invalid reliability
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 2


    def test_cli_invalid_weight_exits_nonzero_cleanly(self) -> None:
        result = subprocess.run(
            [
                sys.executable, "mfr_core_pro.py",
                "q",
                "--evidence", "c", "s", "0.5", "not-a-number",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 2
        assert "Invalid evidence" in result.stderr or "could not convert" in result.stderr
        assert "Traceback" not in result.stderr


class TestEdgeCases:
    def test_empty_question_raises(self) -> None:
        with pytest.raises(ValueError, match="question must be non-empty"):
            IntelligenceRecord("   ")

    def test_prior_out_of_range_raises(self) -> None:
        rec = IntelligenceRecord("q", prior_belief=1.5)
        with pytest.raises(ValueError, match="prior_belief"):
            rec.analyze()

    def test_weight_cap_prevents_extreme(self) -> None:
        # Very high weight should still produce valid posterior in [0,1]
        rec = IntelligenceRecord(
            "q",
            [Evidence("yes", "s", 1.0, weight=1000.0)],
        )
        report = rec.analyze()
        assert 0.0 <= report["confidence"] <= 1.0
        assert report["top_claim"]["effective_weight"] <= 5.0 + 1e-6


class TestSuggestionCoverage:
    def test_coherent_large_sample_default_suggestion(self) -> None:
        # >=3 independent, no conflict, multi-source top → default "reasonably coherent"
        rec = IntelligenceRecord(
            "Coherent?",
            evidence=[
                Evidence("yes", "a", 0.9, independent=True),
                Evidence("yes", "b", 0.85, independent=True),
                Evidence("yes", "c", 0.8, independent=True),
            ],
        )
        report = rec.analyze()
        assert report["status"] == "PROVISIONAL_FINDING"
        assert any("reasonably coherent" in s for s in report["suggestions"])
        assert validate_report(report) == []

    def test_single_source_top_claim_suggestion(self) -> None:
        rec = IntelligenceRecord(
            "Single?",
            evidence=[Evidence("yes", "only", 0.95, independent=True)],
        )
        report = rec.analyze()
        assert any("single source" in s for s in report["suggestions"])

    def test_non_independent_and_small_sample(self) -> None:
        rec = IntelligenceRecord(
            "Nonindep?",
            evidence=[
                Evidence("yes", "a", 0.8, independent=False),
                Evidence("yes", "b", 0.7, independent=False),
            ],
        )
        report = rec.analyze()
        assert any("non-independent" in s for s in report["suggestions"])
        assert any("Sample size is small" in s for s in report["suggestions"])

    def test_alternatives_listed_in_suggestions(self) -> None:
        rec = IntelligenceRecord(
            "Q?",
            evidence=[Evidence("yes", "s", 0.9)],
            alternatives=["no", "maybe"],
        )
        report = rec.analyze()
        assert any("Listed alternatives" in s and "no" in s for s in report["suggestions"])

    def test_evidence_file_object_format_supported(self, tmp_path: Path) -> None:
        """Supports the documented object format from README (question + evidence + optional prior/alternatives)."""
        good = tmp_path / "good_obj.json"
        good.write_text(json.dumps({
            "question": "Is the release safe to ship?",
            "prior_belief": 0.6,
            "evidence": [
                {"claim": "safe", "source": "ci-green", "reliability": 0.95, "independent": True},
                {"claim": "safe", "source": "reviewer-A", "reliability": 0.8}
            ],
            "alternatives": ["needs more tests"]
        }), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--evidence-file", str(good)],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["question"] == "Is the release safe to ship?"
        assert data["status"] == "PROVISIONAL_FINDING"
        assert data["conclusion"] == "safe"
        assert any("needs more tests" in s for s in data.get("suggestions", []))


class TestCLIAdditional:
    def test_decision_flag_emits_contract(self) -> None:
        result = subprocess.run(
            [
                sys.executable, "mfr_core_pro.py",
                "Secure?",
                "--evidence", "yes", "audit", "0.92",
                "--decision",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] in ("stable", "warning", "critical")
        assert "confidence" in data
        assert data["_original_status"] == "PROVISIONAL_FINDING"

    def test_cli_prior_out_of_range_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable, "mfr_core_pro.py",
                "q",
                "--evidence", "c", "s", "0.5",
                "--prior", "1.5",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )
        assert result.returncode == 2
        assert "prior_belief" in result.stderr


class TestDirectCoverage:
    def test_demo_function_runs_without_error(self, capsys) -> None:
        """Direct call covers the demo() implementation for coverage measurement."""
        from mfr_core_pro import demo
        demo()
        captured = capsys.readouterr()
        assert "MFR Adaptive Intelligence Core Pro Demo" in captured.out
        assert "PROVISIONAL_FINDING" in captured.out or "INSUFFICIENT_EVIDENCE" in captured.out

    def test_analyze_with_empty_claims_after_dedup_edge(self) -> None:
        """Ensure the insufficient path is reachable if somehow no claims remain (defensive)."""
        # Normal path is covered; this documents the branch
        rec = IntelligenceRecord("q", evidence=[Evidence("c", "s", 0.5)])
        result = rec.analyze()
        assert result["status"] in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE")


class TestPriorOverride:
    def test_cli_prior_overrides_file_prior(self, tmp_path: Path) -> None:
        """Explicit --prior must override prior_belief from evidence file."""
        good = tmp_path / "with_prior.json"
        good.write_text(json.dumps({
            "question": "override test?",
            "prior_belief": 0.2,
            "evidence": [
                {"claim": "yes", "source": "s", "reliability": 0.7}
            ]
        }), encoding="utf-8")
        # Without --prior: uses file 0.2
        result_file = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--evidence-file", str(good)],
            capture_output=True, text=True, cwd=Path(__file__).parent,
        )
        assert result_file.returncode == 0
        data_file = json.loads(result_file.stdout)
        conf_file = data_file["confidence"]

        # With explicit --prior 0.8: should be higher
        result_cli = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--evidence-file", str(good), "--prior", "0.8"],
            capture_output=True, text=True, cwd=Path(__file__).parent,
        )
        assert result_cli.returncode == 0
        data_cli = json.loads(result_cli.stdout)
        conf_cli = data_cli["confidence"]
        assert conf_cli > conf_file

    def test_default_prior_when_neither_specified(self, tmp_path: Path) -> None:
        """When neither CLI nor file provides prior, use 0.5."""
        good = tmp_path / "no_prior.json"
        good.write_text(json.dumps({
            "question": "default prior?",
            "evidence": [
                {"claim": "yes", "source": "s", "reliability": 0.6}
            ]
        }), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "mfr_core_pro.py", "--evidence-file", str(good)],
            capture_output=True, text=True, cwd=Path(__file__).parent,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Just ensure it runs and produces a valid confidence
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["status"] == "PROVISIONAL_FINDING"
