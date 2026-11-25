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
        question="Q",
        evidence=[Evidence("yes", "source1", 0.95)],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["confidence"] > 0.6
    assert report["top_claim"]["claim"] == "yes"
    assert any("single source" in s for s in report["suggestions"])


def test_multiple_independent_coherent():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("supported", "s1", 0.9),
            Evidence("supported", "s2", 0.85),
            Evidence("supported", "s3", 0.88),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["confidence"] > 0.7
    assert any("coherent" in s or "monitoring" in s for s in report["suggestions"])


def test_conflicting_evidence():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "s1", 0.9),
            Evidence("no", "s2", 0.85),
        ],
    )
    report = rec.analyze()
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING", "INSUFFICIENT_EVIDENCE")


def test_independence_penalty():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("claim", "s1", 0.9, independent=True),
            Evidence("claim", "s2", 0.9, independent=False),
        ],
    )
    report = rec.analyze()
    assert any("independence penalty" in s for s in report["suggestions"])


def test_alternatives_listed():
    rec = IntelligenceRecord(
        question="Q",
        alternatives=["alt1", "alt2"],
        evidence=[Evidence("main", "s", 0.8)],
    )
    report = rec.analyze()
    assert any("Listed alternatives" in s for s in report["suggestions"])


def test_deduplication():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("c", "same", 0.6),
            Evidence("c", "same", 0.9),  # stronger kept
        ],
    )
    report = rec.analyze()
    assert "Deduplicated" in " ".join(report["audit_trail"])
    assert report["top_claim"]["evidence_count"] == 1


def test_ci_non_overlap_suggestion():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("strong", "s1", 0.95),
            Evidence("strong", "s2", 0.95),
            Evidence("strong", "s3", 0.95),
            Evidence("weak", "s4", 0.2),
        ],
    )
    report = rec.analyze()
    assert any("CI" in s or "do not overlap" in s for s in report["suggestions"])


def test_fingerprint_deterministic():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.5)])
    r1 = rec.analyze()
    r2 = rec.analyze()
    assert r1["fingerprint"] == r2["fingerprint"]
    assert len(r1["fingerprint"]) == 64


def test_from_json_roundtrip():
    raw = '{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8, "independent": true, "weight": 1.0}], "alternatives": ["a"], "prior_belief": 0.6}'
    rec = IntelligenceRecord.from_json(raw)
    assert rec.question == "Q"
    assert len(rec.evidence) == 1
    assert rec.prior_belief == 0.6
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"


def test_version_in_report():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    report = rec.analyze()
    assert report["version"] == VERSION


def test_cli_version():
    with patch("sys.argv", ["mfr_core_pro.py", "--version"]):
        with pytest.raises(SystemExit) as ei:
            main()
    assert ei.value.code == 0


def test_cli_help():
    with patch("sys.argv", ["mfr_core_pro.py", "--help"]):
        with pytest.raises(SystemExit) as ei:
            main()
    assert ei.value.code == 0


def test_cli_json_stdin(capsys):
    raw = '{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.9}]}'
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "-"]):
        with patch("sys.stdin", StringIO(raw)):
            main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["status"] == "PROVISIONAL_FINDING"
    assert data["conclusion"] == "c"


def test_cli_json_file(tmp_path, capsys):
    raw = '{"question": "Q", "evidence": [{"claim": "yes", "source": "s", "reliability": 0.85}]}'
    p = tmp_path / "rec.json"
    p.write_text(raw)
    with patch("sys.argv", ["mfr_core_pro.py", "--json", str(p)]):
        main()
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["conclusion"] == "yes"


def test_cli_bad_json(capsys):
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "-"]):
        with patch("sys.stdin", StringIO("not json")):
            with pytest.raises(SystemExit) as ei:
                main()
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_max_evidence_limit():
    evs = [Evidence("c", f"s{i}", 0.8) for i in range(1001)]
    with pytest.raises(ValueError, match="evidence list exceeds"):
        IntelligenceRecord("Q", evidence=evs)


def test_prior_affects_mean():
    rec_low = IntelligenceRecord("Q", evidence=[Evidence("c", "s", 0.6)], prior_belief=0.2)
    rec_high = IntelligenceRecord("Q", evidence=[Evidence("c", "s", 0.6)], prior_belief=0.8)
    m_low = rec_low.analyze()["confidence"]
    m_high = rec_high.analyze()["confidence"]
    assert m_high > m_low


def test_empty_suggestions_fallback():
    # Force path that might empty suggestions then fallback
    rec = IntelligenceRecord("Q", evidence=[Evidence("c", "s", 0.95, independent=True)] * 5)
    report = rec.analyze()
    assert len(report["suggestions"]) >= 1


def test_record_id_preserved():
    rec = IntelligenceRecord("Q", evidence=[Evidence("c", "s", 0.8)], record_id="fixed-id")
    report = rec.analyze()
    assert report["record_id"] == "fixed-id"


def test_created_at_preserved():
    rec = IntelligenceRecord("Q", evidence=[Evidence("c", "s", 0.8)], created_at="2026-01-01T00:00:00+00:00")
    report = rec.analyze()
    assert report["created_at"] == "2026-01-01T00:00:00+00:00"


def test_analyze_with_many_competitors():
    evs = []
    for i in range(5):
        evs.append(Evidence(f"claim{i}", f"s{i}", 0.5 + i*0.05))
    rec = IntelligenceRecord("Q", evidence=evs)
    report = rec.analyze()
    assert len(report["competing_claims"]) <= 3


def test_fingerprint_ignores_timestamps():
    rec = IntelligenceRecord("Q", evidence=[Evidence("c", "s", 0.8)])
    fp1 = fingerprint(rec)
    # mutate timestamps shouldn't affect
    rec.created_at = "different"
    fp2 = fingerprint(rec)
    assert fp1 == fp2


def test_from_json_evidence_not_object():
    raw = '{"question": "Q", "evidence": ["not an object"]}'
    with pytest.raises(ValueError, match="must be an object"):
        IntelligenceRecord.from_json(raw)


def test_from_json_evidence_invalid_fields_typeerror():
    raw = '{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8, "extra": 1}]}'
    with pytest.raises(ValueError, match="invalid fields"):
        IntelligenceRecord.from_json(raw)


def test_from_json_evidence_value_error():
    raw = '{"question": "Q", "evidence": [{"claim": "", "source": "s", "reliability": 0.8}]}'
    with pytest.raises(ValueError, match="claim must be non-empty"):
        IntelligenceRecord.from_json(raw)


def test_from_json_prior_not_number():
    raw = '{"question": "Q", "prior_belief": "high"}'
    with pytest.raises(ValueError, match="prior_belief must be a number"):
        IntelligenceRecord.from_json(raw)


def test_from_json_root_not_object():
    raw = '[1,2,3]'
    with pytest.raises(ValueError, match="JSON root must be an object"):
        IntelligenceRecord.from_json(raw)


def test_main_permission_error(capsys):
    """Mock open to raise PermissionError (works under root and non-root)."""
    with patch("sys.argv", ["mfr_core_pro.py", "--json", "/tmp/any.json"]):
        with patch("builtins.open", side_effect=PermissionError("permission denied")):
            with pytest.raises(SystemExit) as ei:
                main()
    assert ei.value.code == 1
    err = capsys.readouterr().err
    assert "permission denied" in err.lower()


def test_fingerprint_type_guard(monkeypatch):
    """Regression: fingerprint() rejects non-str fingerprint from analyze()."""
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    original = rec.analyze

    def bad_analyze():
        r = original()
        r["fingerprint"] = 123  # non-str
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
