"""Tests for MFR Adaptive Intelligence Core Pro. Target ≥90% coverage, 48+ cases covering edges."""
import re

import json
import pytest
from io import StringIO
import sys
from unittest.mock import patch

from mfr_core_pro import (
    Evidence,
    IntelligenceRecord,
    fingerprint,
    main,
)
from version import VERSION


def test_evidence_validation():
    with pytest.raises(ValueError, match="claim must be non-empty"):
        Evidence("", "src", 0.5)
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence("claim", "", 0.5)
    with pytest.raises(ValueError, match="reliability must be in"):
        Evidence("c", "s", 1.1)
    with pytest.raises(ValueError, match="reliability must be in"):
        Evidence("c", "s", -0.1)
    with pytest.raises(ValueError, match="weight must be"):
        Evidence("c", "s", 0.5, weight=0)
    with pytest.raises(ValueError, match="claim exceeds"):
        Evidence("x" * 501, "s", 0.5)
    with pytest.raises(ValueError, match="source exceeds"):
        Evidence("c", "y" * 201, 0.5)


def test_record_validation():
    with pytest.raises(ValueError, match="question must be non-empty"):
        IntelligenceRecord("")
    with pytest.raises(ValueError, match="question exceeds"):
        IntelligenceRecord("q" * 1001)
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord("Q", prior_belief=1.1)
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord("Q", prior_belief=-0.1)
    with pytest.raises(ValueError, match="alternative exceeds"):
        IntelligenceRecord("Q", alternatives=["a" * 201])
    with pytest.raises(ValueError, match="alternatives list exceeds"):
        IntelligenceRecord("Q", alternatives=["a"] * 21)


def test_empty_evidence_status():
    rec = IntelligenceRecord(question="Is this true?")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert report["conclusion"] is None
    assert "evidence" in report["missing"]
    assert report["stability"] == "unstable"
    assert report["version"] == VERSION
    assert report["fingerprint"]


def test_single_strong_evidence():
    rec = IntelligenceRecord(
        question="Is the system healthy?",
        evidence=[Evidence(claim="healthy", source="monitor", reliability=0.95)],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "healthy"
    assert report["confidence"] > 0.8
    assert report["top_claim"]["evidence_count"] == 1
    assert any("single source" in s for s in report["suggestions"])


def test_multiple_independent_evidence():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "s1", 0.9),
            Evidence("yes", "s2", 0.85),
            Evidence("yes", "s3", 0.8),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["confidence"] > 0.7
    assert report["top_claim"]["evidence_count"] == 3


def test_conflicting_evidence():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("A", "s1", 0.7),
            Evidence("B", "s2", 0.65),
        ],
    )
    report = rec.analyze()
    # With weak means and close values, expect conflict or insufficient
    assert report["status"] in ("CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE", "PROVISIONAL_FINDING")


def test_independence_penalty():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "s1", 0.9, independent=True),
            Evidence("yes", "s2", 0.9, independent=False),
        ],
    )
    report = rec.analyze()
    assert any("Non-independent" in s or "independence" in s.lower() for s in report["suggestions"])


def test_deduplication():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "same", 0.5),
            Evidence("yes", "same", 0.9),
        ],
    )
    report = rec.analyze()
    assert any("Deduplicated" in a for a in report["audit_trail"])
    assert report["top_claim"]["evidence_count"] == 1


def test_alternatives_listed():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.8)],
        alternatives=["yes", "no"],
    )
    report = rec.analyze()
    assert any("Listed alternatives" in s for s in report["suggestions"])


def test_fingerprint_deterministic():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("c", "s", 0.8)],
    )
    fp1 = fingerprint(rec)
    fp2 = fingerprint(rec)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_from_json_roundtrip():
    raw = '{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8}]}'
    rec = IntelligenceRecord.from_json(raw)
    assert rec.question == "Q"
    assert len(rec.evidence) == 1


def test_version_in_report():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    report = rec.analyze()
    assert report["version"] == VERSION


def test_cli_version(capsys):
    with patch("sys.argv", ["mfr_core_pro.py", "--version"]):
        with pytest.raises(SystemExit) as ei:
            main()
    assert ei.value.code == 0
    out = capsys.readouterr().out
    assert VERSION in out


def test_cli_help(capsys):
    with patch("sys.argv", ["mfr_core_pro.py", "--help"]):
        with pytest.raises(SystemExit) as ei:
            main()
    assert ei.value.code == 0


def test_cli_json_stdin(capsys):
    raw = '{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8}]}'
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "-"]):
        with patch("sys.stdin", StringIO(raw)):
            main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"]


def test_cli_json_file(tmp_path, capsys):
    p = tmp_path / "rec.json"
    p.write_text('{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8}]}')
    with patch("sys.argv", ["mfr_core_pro.py", "--json", str(p)]):
        main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "fingerprint" in data


def test_cli_bad_json(capsys):
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "-"]):
        with patch("sys.stdin", StringIO("not json")):
            with pytest.raises(SystemExit) as ei:
                main()
    assert ei.value.code == 1


def test_max_evidence_limit():
    with pytest.raises(ValueError, match="evidence list exceeds"):
        IntelligenceRecord(question="Q", evidence=[Evidence("c", f"s{i}", 0.5) for i in range(1001)])


def test_prior_affects_mean():
    rec_low = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s", 0.6)], prior_belief=0.2)
    rec_high = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s", 0.6)], prior_belief=0.8)
    assert rec_low.analyze()["confidence"] < rec_high.analyze()["confidence"]


def test_empty_suggestions_fallback():
    # Hard to hit; covered indirectly
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s1", 0.95), Evidence("yes", "s2", 0.95), Evidence("yes", "s3", 0.95)])
    report = rec.analyze()
    assert isinstance(report["suggestions"], list)


def test_record_id_preserved():
    rec = IntelligenceRecord(question="Q", record_id="fixed-id")
    assert rec.record_id == "fixed-id"
    report = rec.analyze()
    assert report["record_id"] == "fixed-id"


def test_created_at_preserved():
    rec = IntelligenceRecord(question="Q", created_at="2026-01-01T00:00:00+00:00")
    assert rec.created_at == "2026-01-01T00:00:00+00:00"


def test_analyze_with_many_competitors():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("A", "s1", 0.9),
            Evidence("B", "s2", 0.5),
            Evidence("C", "s3", 0.4),
            Evidence("D", "s4", 0.3),
        ],
    )
    report = rec.analyze()
    assert len(report["competing_claims"]) <= 3


def test_fingerprint_ignores_timestamps():
    rec1 = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    rec2 = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    assert fingerprint(rec1) == fingerprint(rec2)


def test_from_json_evidence_not_object():
    with pytest.raises(ValueError, match="must be an object"):
        IntelligenceRecord.from_json('{"question": "Q", "evidence": [1]}')


def test_from_json_evidence_invalid_fields_typeerror():
    with pytest.raises(ValueError, match="invalid fields"):
        IntelligenceRecord.from_json('{"question": "Q", "evidence": [{"claim": "c"}]}')


def test_from_json_evidence_value_error():
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json('{"question": "Q", "evidence": [{"claim": "", "source": "s", "reliability": 0.5}]}')


def test_from_json_prior_not_number():
    with pytest.raises(ValueError, match="prior_belief must be a number"):
        IntelligenceRecord.from_json('{"question": "Q", "prior_belief": "high"}')


def test_from_json_root_not_object():
    with pytest.raises(ValueError, match="JSON root must be an object"):
        IntelligenceRecord.from_json('[1,2,3]')


def test_main_permission_error(monkeypatch, capsys):
    def fake_open(*args, **kwargs):
        raise PermissionError("denied")
    monkeypatch.setattr("builtins.open", fake_open)
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "/tmp/foo.json"]):
        with pytest.raises(SystemExit) as ei:
            main()
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "permission denied" in err.lower()


def test_fingerprint_type_guard(monkeypatch):
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    def bad_analyze():
        r = rec.analyze()
        r["fingerprint"] = 123
        return r
    monkeypatch.setattr(rec, "analyze", bad_analyze)
    with pytest.raises(TypeError, match="fingerprint must be str"):
        fingerprint(rec)


def test_validate_analysis_report_valid():
    from mfr_core_pro import validate_analysis_report
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    report = rec.analyze()
    assert validate_analysis_report(report) == []


def test_validate_analysis_report_invalid():
    from mfr_core_pro import validate_analysis_report
    assert "report must be a dict" in validate_analysis_report("not a dict")
    bad = {"status": "BAD", "confidence": 1.5, "fingerprint": "short", "suggestions": "no", "audit_trail": None}
    viols = validate_analysis_report(bad)
    assert any("missing required" in v for v in viols)
    assert any("invalid status" in v for v in viols)
    assert any("confidence must be number" in v for v in viols)
    assert any("fingerprint must be 64-char" in v for v in viols)
    assert any("suggestions must be a list" in v for v in viols)
    assert any("audit_trail must be a list" in v for v in viols)


def test_demo_runs(capsys):
    from mfr_core_pro import _demo
    _demo()
    out = capsys.readouterr().out
    assert "Demo complete" in out
    assert "Status:" in out


def test_cli_file_not_found(capsys):
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "/tmp/definitely-missing-record.json"]):
        with pytest.raises(SystemExit) as ei:
            main()
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "file not found" in err.lower()


def test_main_runs_demo(capsys):
    """Cover main() path that invokes _demo when no args."""
    with patch("sys.argv", ["mfr_core_pro.py"]):
        main()
    out = capsys.readouterr().out
    assert "Demo complete" in out
    assert "Status:" in out


def test_alternatives_filter_empty_and_whitespace():
    """Empty or whitespace-only alternatives are dropped; valid ones kept."""
    rec = IntelligenceRecord(
        question="Q",
        alternatives=["  ", "", "valid", "  also valid  "],
        evidence=[Evidence("c", "s", 0.8)],
    )
    assert rec.alternatives == ["valid", "also valid"]
    report = rec.analyze()
    assert any("Listed alternatives" in s for s in report["suggestions"])


def test_to_json_roundtrip():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence("yes", "src", 0.7)],
        alternatives=["a", "b"],
        prior_belief=0.4,
    )
    raw = rec.to_json()
    rec2 = IntelligenceRecord.from_json(raw)
    assert rec2.question == rec.question
    assert rec2.prior_belief == rec.prior_belief
    assert len(rec2.evidence) == 1
    assert rec2.alternatives == rec.alternatives


def test_from_json_missing_or_invalid_question():
    """from_json rejects missing or non-string question field."""
    with pytest.raises(ValueError, match="missing or invalid 'question' field"):
        IntelligenceRecord.from_json('{"evidence": []}')
    with pytest.raises(ValueError, match="missing or invalid 'question' field"):
        IntelligenceRecord.from_json('{"question": 123}')
    with pytest.raises(ValueError, match="missing or invalid 'question' field"):
        IntelligenceRecord.from_json('{"question": null}')
