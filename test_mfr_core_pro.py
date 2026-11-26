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


def test_from_json_invalid_question():
    with pytest.raises(ValueError, match="missing or invalid 'question' field"):
        IntelligenceRecord.from_json('{"evidence": []}')
    with pytest.raises(ValueError, match="missing or invalid 'question' field"):
        IntelligenceRecord.from_json('{"question": 123}')
    with pytest.raises(ValueError, match="missing or invalid 'question' field"):
        IntelligenceRecord.from_json('{"question": null}')


def test_from_json_alternatives_not_list():
    """Regression: alternatives must be a list of strings."""
    with pytest.raises(ValueError, match="alternatives must be a list of strings"):
        IntelligenceRecord.from_json('{"question": "q", "alternatives": "notalist"}')
    with pytest.raises(ValueError, match="alternatives must be a list of strings"):
        IntelligenceRecord.from_json('{"question": "q", "alternatives": null}')


def test_from_json_alternatives_non_string_item():
    """Regression: each alternative must be a string."""
    with pytest.raises(ValueError, match="alternatives\\[0\\] must be a string"):
        IntelligenceRecord.from_json('{"question": "q", "alternatives": [1, "ok"]}')


def test_from_json_evidence_not_list():
    """Regression: evidence must be a list (null or object rejected)."""
    with pytest.raises(ValueError, match="evidence must be a list"):
        IntelligenceRecord.from_json('{"question": "q", "evidence": null}')
    with pytest.raises(ValueError, match="evidence must be a list"):
        IntelligenceRecord.from_json('{"question": "q", "evidence": {}}')


def test_deduplication_keeps_strongest():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "same", 0.6, weight=1.0),
            Evidence("yes", "same", 0.9, weight=1.0),
        ],
    )
    report = rec.analyze()
    assert any("Deduplicated" in a for a in report["audit_trail"])
    assert report["top_claim"]["evidence_count"] == 1


def test_conflicting_evidence_status():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "a", 0.9),
            Evidence("yes", "b", 0.85),
            Evidence("no", "c", 0.88),
            Evidence("no", "d", 0.82),
        ],
    )
    report = rec.analyze()
    # Means should be close enough or CIs overlap to trigger CONFLICTING
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")
    assert len(report["competing_claims"]) >= 1


def test_insufficient_weak_single():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("maybe", "weak", 0.4)],
    )
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["stability"] == "unstable"


def test_suggestions_and_stability():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "a", 0.95, independent=True),
            Evidence("yes", "b", 0.9, independent=True),
            Evidence("yes", "c", 0.85, independent=False),
        ],
        alternatives=["alt1", "alt2"],
    )
    report = rec.analyze()
    assert report["stability"] in ("stable", "provisional")
    assert any("independent" in s.lower() or "alternatives" in s.lower() or "sample" in s.lower() for s in report["suggestions"])
    assert report["decision_confidence"] >= 0.3


def test_fingerprint_deterministic():
    rec1 = IntelligenceRecord(
        question="Same",
        evidence=[Evidence("yes", "s", 0.8)],
        prior_belief=0.5,
    )
    rec2 = IntelligenceRecord(
        question="Same",
        evidence=[Evidence("yes", "s", 0.8)],
        prior_belief=0.5,
    )
    assert fingerprint(rec1) == fingerprint(rec2)
    assert len(rec1.analyze()["fingerprint"]) == 64


def test_from_json_roundtrip_and_analyze_json():
    rec = IntelligenceRecord(
        question="Roundtrip?",
        evidence=[Evidence("ok", "src", 0.7)],
        alternatives=["a", "b"],
    )
    raw = rec.to_json()
    restored = IntelligenceRecord.from_json(raw)
    assert restored.question == rec.question
    assert len(restored.evidence) == 1
    from mfr_core_pro import analyze_json
    report = analyze_json(raw)
    assert report["status"] == "PROVISIONAL_FINDING"


def test_validate_analysis_report():
    from mfr_core_pro import validate_analysis_report
    good = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s", 0.8)]).analyze()
    assert validate_analysis_report(good) == []
    bad = {"status": "UNKNOWN"}
    assert len(validate_analysis_report(bad)) > 0
    assert len(validate_analysis_report("not a dict")) > 0


def test_cli_version_and_demo(capsys):
    with patch("sys.argv", ["mfr-core", "--version"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0
    captured = capsys.readouterr()
    assert VERSION in captured.out


def test_cli_json_stdin_and_file(tmp_path, capsys):
    rec_json = '{"question":"CLI?","evidence":[{"claim":"yes","source":"t","reliability":0.8}]}'
    # file
    p = tmp_path / "r.json"
    p.write_text(rec_json)
    with patch("sys.argv", ["mfr-core", "--json", str(p)]):
        main()
    out = capsys.readouterr().out
    assert "PROVISIONAL_FINDING" in out or "confidence" in out
    # stdin
    with patch("sys.argv", ["mfr-core", "--json", "-"]), patch("sys.stdin", StringIO(rec_json)):
        main()
    assert "status" in capsys.readouterr().out


def test_cli_errors(tmp_path, capsys):
    with patch("sys.argv", ["mfr-core", "--json", "/nonexistent.json"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
    err = capsys.readouterr().err
    assert "not found" in err
    # invalid json
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with patch("sys.argv", ["mfr-core", "--json", str(bad)]):
        with pytest.raises(SystemExit):
            main()


def test_evidence_list_exceeds_maximum():
    """Regression: evidence list length limit."""
    too_many = [Evidence("c", f"s{i}", 0.5) for i in range(1001)]
    with pytest.raises(ValueError, match="evidence list exceeds maximum"):
        IntelligenceRecord(question="Q", evidence=too_many)


def test_from_json_root_not_object():
    """Regression: JSON root must be an object."""
    with pytest.raises(ValueError, match="JSON root must be an object"):
        IntelligenceRecord.from_json("[1, 2, 3]")
    with pytest.raises(ValueError, match="JSON root must be an object"):
        IntelligenceRecord.from_json('"just a string"')


def test_from_json_evidence_item_not_object():
    """Regression: each evidence item must be an object."""
    with pytest.raises(ValueError, match="evidence\\[0\\] must be an object"):
        IntelligenceRecord.from_json('{"question": "q", "evidence": ["not-an-object"]}')


def test_from_json_invalid_json():
    """Regression: invalid JSON raises clear error."""
    with pytest.raises(ValueError, match="invalid JSON"):
        IntelligenceRecord.from_json("{not json")
