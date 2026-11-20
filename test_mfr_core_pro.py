"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import json
import os
import sys
import tempfile
from io import StringIO
from unittest.mock import patch

import pytest

from mfr_core_pro import (
    Evidence,
    IntelligenceRecord,
    VERSION,
    analyze_json,
    fingerprint,
    validate_analysis_report,
    MAX_EVIDENCE_ITEMS,
)


def test_version_present():
    assert VERSION.startswith("2.1.")
    assert "pro" in VERSION


def test_evidence_validation_rejects_empty_claim():
    with pytest.raises(ValueError, match="claim must be non-empty"):
        Evidence(claim="", source="src", reliability=0.5)


def test_evidence_validation_rejects_empty_source():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="ok", source="  ", reliability=0.5)


def test_evidence_validation_rejects_bad_reliability():
    with pytest.raises(ValueError, match="reliability must be in"):
        Evidence(claim="ok", source="src", reliability=1.5)


def test_evidence_validation_rejects_zero_weight():
    with pytest.raises(ValueError, match="weight must be > 0"):
        Evidence(claim="ok", source="src", reliability=0.5, weight=0.0)


def test_evidence_validation_rejects_long_claim():
    with pytest.raises(ValueError, match="claim exceeds max length"):
        Evidence(claim="x" * 501, source="src", reliability=0.5)


def test_record_rejects_empty_question():
    with pytest.raises(ValueError, match="question must be non-empty"):
        IntelligenceRecord(question="   ", evidence=[])


def test_record_rejects_bad_prior():
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="q?", prior_belief=1.5)


def test_insufficient_evidence():
    rec = IntelligenceRecord(question="Is it true?")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert report["conclusion"] is None
    assert "evidence" in report.get("missing", [])
    assert report["version"] == VERSION
    assert len(report["fingerprint"]) == 64


def test_single_evidence_provisional():
    ev = Evidence(claim="yes", source="a", reliability=0.8)
    rec = IntelligenceRecord(question="q?", evidence=[ev])
    report = rec.analyze()
    assert report["status"] in ("PROVISIONAL_FINDING", "INSUFFICIENT_EVIDENCE")
    assert report["top_claim"]["claim"] == "yes"
    assert 0.0 < report["confidence"] <= 1.0


def test_multiple_independent_evidence():
    evids = [
        Evidence(claim="healthy", source="m1", reliability=0.9, independent=True),
        Evidence(claim="healthy", source="m2", reliability=0.85, independent=True),
    ]
    rec = IntelligenceRecord(question="healthy?", evidence=evids)
    report = rec.analyze()
    assert report["conclusion"] == "healthy"
    assert report["confidence"] > 0.6
    assert validate_analysis_report(report) == []


def test_conflicting_evidence():
    evids = [
        Evidence(claim="yes", source="a", reliability=0.9),
        Evidence(claim="no", source="b", reliability=0.9),
    ]
    rec = IntelligenceRecord(question="conflict?", evidence=evids)
    report = rec.analyze()
    # May be conflicting or provisional depending on CI
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")


def test_deduplication():
    evids = [
        Evidence(claim="yes", source="same", reliability=0.5, weight=1.0),
        Evidence(claim="yes", source="same", reliability=0.9, weight=2.0),
    ]
    rec = IntelligenceRecord(question="dedup?", evidence=evids)
    report = rec.analyze()
    assert "Deduplicated" in " ".join(report.get("audit_trail", []))


def test_fingerprint_deterministic():
    rec = IntelligenceRecord(
        question="fp?",
        evidence=[Evidence(claim="c", source="s", reliability=0.7)],
    )
    fp1 = fingerprint(rec)
    fp2 = fingerprint(rec)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_from_json_and_analyze_json():
    raw = json.dumps({
        "question": "json?",
        "evidence": [{"claim": "ok", "source": "src", "reliability": 0.75}],
        "prior_belief": 0.5,
    })
    report = analyze_json(raw)
    assert report["question"] == "json?"
    assert validate_analysis_report(report) == []


def test_from_json_invalid():
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json("not json")


def test_validate_report_missing_fields():
    bad = {"status": "bad"}
    viols = validate_analysis_report(bad)
    assert len(viols) > 0


def test_cli_version(capsys):
    with patch.object(sys, "argv", ["mfr_core_pro.py", "--version"]):
        from mfr_core_pro import main
        main()
    captured = capsys.readouterr()
    assert VERSION in captured.out


def test_cli_help(capsys):
    with patch.object(sys, "argv", ["mfr_core_pro.py", "--help"]):
        from mfr_core_pro import main
        main()
    captured = capsys.readouterr()
    assert "Usage" in captured.out


def test_cli_json_missing_file(capsys):
    with patch.object(sys, "argv", ["mfr_core_pro.py", "--json", "/nonexistent/file.json"]):
        from mfr_core_pro import main
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "file not found" in captured.err


def test_cli_json_no_arg(capsys):
    with patch.object(sys, "argv", ["mfr_core_pro.py", "--json"]):
        from mfr_core_pro import main
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "Usage" in captured.err


def test_cli_json_invalid_content(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("not-json")
    with patch.object(sys, "argv", ["mfr_core_pro.py", "--json", str(bad)]):
        from mfr_core_pro import main
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_demo_runs(capsys):
    with patch.object(sys, "argv", ["mfr_core_pro.py"]):
        from mfr_core_pro import main
        main()
    captured = capsys.readouterr()
    assert "Demo complete" in captured.out


def test_evidence_validation_rejects_long_source():
    with pytest.raises(ValueError, match="source exceeds max length"):
        Evidence(claim="ok", source="x" * 201, reliability=0.5)


def test_record_rejects_long_question():
    with pytest.raises(ValueError, match="question exceeds max length"):
        IntelligenceRecord(question="x" * 1001)


def test_record_rejects_too_many_evidence():
    evids = [Evidence(claim="c", source=f"s{i}", reliability=0.5) for i in range(MAX_EVIDENCE_ITEMS + 1)]
    with pytest.raises(ValueError, match="evidence list exceeds maximum"):
        IntelligenceRecord(question="q?", evidence=evids)


def test_record_rejects_long_alternative():
    with pytest.raises(ValueError, match="alternative exceeds max length"):
        IntelligenceRecord(question="q?", alternatives=["x" * 201])


def test_record_rejects_too_many_alternatives():
    alts = [f"a{i}" for i in range(21)]
    with pytest.raises(ValueError, match="alternatives list exceeds maximum"):
        IntelligenceRecord(question="q?", alternatives=alts)


def test_independence_penalty_applied():
    evids = [
        Evidence(claim="yes", source="a", reliability=0.9, independent=True),
        Evidence(claim="yes", source="b", reliability=0.9, independent=False),
    ]
    rec = IntelligenceRecord(question="indep?", evidence=evids)
    report = rec.analyze()
    assert any("Non-independent" in s for s in report["suggestions"])
    assert validate_analysis_report(report) == []


def test_from_json_incomplete_evidence_raises_valueerror():
    raw = json.dumps({"question": "q?", "evidence": [{"claim": "only-claim"}]})
    with pytest.raises(ValueError, match="evidence\\[0\\] invalid fields"):
        IntelligenceRecord.from_json(raw)


def test_from_json_non_object_evidence_item():
    raw = json.dumps({"question": "q?", "evidence": ["not-a-dict"]})
    with pytest.raises(ValueError, match="evidence\\[0\\] must be an object"):
        IntelligenceRecord.from_json(raw)


def test_from_json_bad_prior_type():
    raw = json.dumps({"question": "q?", "prior_belief": "high"})
    with pytest.raises(ValueError, match="prior_belief must be a number"):
        IntelligenceRecord.from_json(raw)


def test_from_json_evidence_value_error_propagates():
    raw = json.dumps({
        "question": "q?",
        "evidence": [{"claim": "ok", "source": "s", "reliability": 2.0}],
    })
    with pytest.raises(ValueError, match="evidence\\[0\\]"):
        IntelligenceRecord.from_json(raw)


def test_ci_uses_pure_beta_posterior_std():
    """Regression: CI must not double-count sample size via extra /sqrt(n)."""
    evids = [
        Evidence(claim="yes", source=f"s{i}", reliability=0.9, independent=True, weight=1.0)
        for i in range(5)
    ]
    rec = IntelligenceRecord(question="ci-width?", evidence=evids, prior_belief=0.5)
    report = rec.analyze()
    top = report["top_claim"]
    # Pure Beta: alpha=5.5, beta=1.5, var≈0.02105, std≈0.145, 1.96*std≈0.284
    # Upper side clamps at 1.0, so observed width ≈ 0.50
    width = top["ci_high"] - top["ci_low"]
    assert 0.45 < width < 0.55, f"expected ~0.50 pure-Beta clamped width, got {width}"
    assert top["ci_low"] < 0.55  # lower bound reflects the std, not the old narrow CI
    assert validate_analysis_report(report) == []
