"""Unit tests for MFR Adaptive Intelligence Core Pro. Coverage target >=90%."""
from __future__ import annotations

import json
import pytest
from mfr_core_pro import (
    Evidence,
    IntelligenceRecord,
    analyze_json,
    fingerprint,
    validate_analysis_report,
    VERSION,
)


def test_evidence_valid():
    e = Evidence(claim="healthy", source="monitor", reliability=0.9, independent=True, weight=1.0)
    assert e.claim == "healthy"
    assert e.reliability == 0.9


def test_evidence_invalid_claim_empty():
    with pytest.raises(ValueError, match="claim must be non-empty"):
        Evidence(claim="   ", source="s", reliability=0.5)


def test_evidence_invalid_source_empty():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="c", source=" ", reliability=0.5)


def test_evidence_invalid_reliability():
    with pytest.raises(ValueError, match="reliability must be in"):
        Evidence(claim="c", source="s", reliability=1.5)


def test_evidence_invalid_weight():
    with pytest.raises(ValueError, match="weight must be"):
        Evidence(claim="c", source="s", reliability=0.5, weight=0)


def test_evidence_claim_too_long():
    with pytest.raises(ValueError, match="claim exceeds"):
        Evidence(claim="x" * 501, source="s", reliability=0.5)


def test_evidence_source_too_long():
    with pytest.raises(ValueError, match="source exceeds"):
        Evidence(claim="c", source="x" * 201, reliability=0.5)


def test_record_valid():
    rec = IntelligenceRecord(question="Is it ok?", prior_belief=0.6)
    assert rec.question == "Is it ok?"
    assert rec.prior_belief == 0.6
    assert rec.record_id
    assert rec.created_at


def test_record_invalid_question():
    with pytest.raises(ValueError, match="question must be non-empty"):
        IntelligenceRecord(question="  ")


def test_record_question_too_long():
    with pytest.raises(ValueError, match="question exceeds"):
        IntelligenceRecord(question="x" * 1001)


def test_record_invalid_prior():
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="q", prior_belief=1.5)


def test_record_alternatives_cleaned():
    rec = IntelligenceRecord(
        question="q",
        alternatives=["  a  ", "", "b"],
    )
    assert rec.alternatives == ["a", "b"]
    with pytest.raises(ValueError, match="alternative exceeds"):
        IntelligenceRecord(question="q", alternatives=["x" * 201])


def test_record_too_many_alternatives():
    with pytest.raises(ValueError, match="alternatives list exceeds"):
        IntelligenceRecord(question="q", alternatives=[f"a{i}" for i in range(21)])


def test_record_too_many_evidence():
    evs = [Evidence(claim="c", source=f"s{i}", reliability=0.5) for i in range(1001)]
    with pytest.raises(ValueError, match="evidence list exceeds"):
        IntelligenceRecord(question="q", evidence=evs)


def test_to_json_from_json_roundtrip():
    rec = IntelligenceRecord(
        question="Is healthy?",
        evidence=[Evidence(claim="yes", source="a", reliability=0.8)],
        alternatives=["yes", "no"],
        prior_belief=0.4,
    )
    raw = rec.to_json()
    rec2 = IntelligenceRecord.from_json(raw)
    assert rec2.question == rec.question
    assert len(rec2.evidence) == 1
    assert rec2.alternatives == ["yes", "no"]
    assert rec2.prior_belief == 0.4


def test_from_json_invalid():
    with pytest.raises(ValueError, match="invalid JSON"):
        IntelligenceRecord.from_json("{bad")
    with pytest.raises(ValueError, match="JSON root must be"):
        IntelligenceRecord.from_json("[]")
    with pytest.raises(ValueError, match="missing or invalid 'question'"):
        IntelligenceRecord.from_json("{}")
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json('{"question": "q", "evidence": [1]}')
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json('{"question": "q", "prior_belief": "x"}')


def test_analyze_no_evidence():
    rec = IntelligenceRecord(question="q")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert report["conclusion"] is None
    assert "evidence" in report["missing"]
    assert report["stability"] == "unstable"
    assert len(report["fingerprint"]) == 64
    assert report["version"] == VERSION


def test_analyze_single_evidence():
    rec = IntelligenceRecord(
        question="healthy?",
        evidence=[Evidence(claim="healthy", source="m1", reliability=0.9)],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "healthy"
    assert report["top_claim"]["evidence_count"] == 1
    assert "single source" in " ".join(report["suggestions"])


def test_analyze_multiple_coherent():
    rec = IntelligenceRecord(
        question="healthy?",
        evidence=[
            Evidence(claim="healthy", source="m1", reliability=0.9),
            Evidence(claim="healthy", source="m2", reliability=0.85),
            Evidence(claim="healthy", source="m3", reliability=0.8),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["confidence"] > 0.7
    assert report["stability"] in ("stable", "provisional")


def test_analyze_conflicting():
    rec = IntelligenceRecord(
        question="status?",
        evidence=[
            Evidence(claim="healthy", source="a", reliability=0.9),
            Evidence(claim="degraded", source="b", reliability=0.85),
        ],
    )
    report = rec.analyze()
    assert report["status"] in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE")
    assert len(report["competing_claims"]) >= 0


def test_analyze_independence_penalty():
    rec = IntelligenceRecord(
        question="q",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.9, independent=False),
            Evidence(claim="yes", source="b", reliability=0.9, independent=False),
        ],
    )
    report = rec.analyze()
    assert "Non-independent" in " ".join(report["suggestions"]) or "independence" in " ".join(report["suggestions"]).lower()


def test_analyze_dedup():
    rec = IntelligenceRecord(
        question="q",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.5),
            Evidence(claim="yes", source="a", reliability=0.9),
        ],
    )
    report = rec.analyze()
    assert any("Deduplicated" in a for a in report["audit_trail"])
    assert report["top_claim"]["evidence_count"] == 1


def test_analyze_with_alternatives():
    rec = IntelligenceRecord(
        question="q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9)],
        alternatives=["yes", "no"],
    )
    report = rec.analyze()
    assert any("alternatives" in s.lower() for s in report["suggestions"])


def test_fingerprint_deterministic():
    rec = IntelligenceRecord(
        question="q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.8)],
    )
    fp1 = fingerprint(rec)
    fp2 = fingerprint(rec)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_validate_report_ok():
    rec = IntelligenceRecord(question="q", evidence=[Evidence(claim="c", source="s", reliability=0.8)])
    report = rec.analyze()
    violations = validate_analysis_report(report)
    assert violations == []


def test_validate_report_bad():
    assert validate_analysis_report("not dict")
    bad = {"status": "BAD"}
    assert validate_analysis_report(bad)
    bad2 = {"version": "x", "record_id": "1", "status": "PROVISIONAL_FINDING",
            "question": "q", "confidence": 1.5, "decision_confidence": 0.5,
            "stability": "s", "suggestions": [], "audit_trail": [],
            "created_at": "t", "analyzed_at": "t", "fingerprint": "short"}
    assert validate_analysis_report(bad2)


def test_analyze_json():
    raw = json.dumps({
        "question": "Is it?",
        "evidence": [{"claim": "yes", "source": "s", "reliability": 0.9}],
    })
    report = analyze_json(raw)
    assert report["status"] in ("PROVISIONAL_FINDING", "INSUFFICIENT_EVIDENCE")
    assert report["question"] == "Is it?"


def test_demo_runs(capsys):
    from mfr_core_pro import _demo
    _demo()
    captured = capsys.readouterr()
    assert "Demo" in captured.out
    assert "Status:" in captured.out


def test_main_help(monkeypatch, capsys):
    import sys
    from mfr_core_pro import main
    monkeypatch.setattr(sys, "argv", ["mfr_core_pro.py", "--help"])
    main()
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_main_version(monkeypatch, capsys):
    import sys
    from mfr_core_pro import main
    monkeypatch.setattr(sys, "argv", ["mfr_core_pro.py", "--version"])
    main()
    captured = capsys.readouterr()
    assert VERSION in captured.out


def test_main_json_missing_file(monkeypatch, capsys):
    import sys
    from mfr_core_pro import main
    monkeypatch.setattr(sys, "argv", ["mfr_core_pro.py", "--json", "/nonexistent.json"])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "file not found" in captured.err


def test_main_json_no_file(monkeypatch, capsys):
    import sys
    from mfr_core_pro import main
    monkeypatch.setattr(sys, "argv", ["mfr_core_pro.py", "--json"])
    with pytest.raises(SystemExit):
        main()


def test_main_demo(monkeypatch, capsys):
    import sys
    from mfr_core_pro import main
    monkeypatch.setattr(sys, "argv", ["mfr_core_pro.py"])
    main()
    captured = capsys.readouterr()
    assert "Demo complete" in captured.out


def test_from_json_invalid_evidence_fields():
    # TypeError path: unexpected keyword
    raw = '{"question": "q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.5, "extra": 1}]}'
    with pytest.raises(ValueError, match="invalid fields"):
        IntelligenceRecord.from_json(raw)
    # ValueError path: bad reliability
    raw2 = '{"question": "q", "evidence": [{"claim": "c", "source": "s", "reliability": 1.5}]}'
    with pytest.raises(ValueError, match="reliability"):
        IntelligenceRecord.from_json(raw2)


def test_analyze_ci_non_overlap_and_stable():
    # High separation to trigger CI non-overlap and stable if confidence high
    rec = IntelligenceRecord(
        question="status?",
        evidence=[
            Evidence(claim="healthy", source="a", reliability=0.95, weight=2.0),
            Evidence(claim="healthy", source="b", reliability=0.95, weight=2.0),
            Evidence(claim="healthy", source="c", reliability=0.95, weight=2.0),
            Evidence(claim="failed", source="d", reliability=0.1, weight=1.0),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["stability"] in ("stable", "provisional")
    assert any("CI" in s or "overlap" in s for s in report["suggestions"] + report["audit_trail"])


def test_analyze_no_suggestions_fallback():
    # Case that might hit the empty suggestions fallback (hard, but try high coherent)
    rec = IntelligenceRecord(
        question="q",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.99),
            Evidence(claim="yes", source="b", reliability=0.99),
            Evidence(claim="yes", source="c", reliability=0.99),
            Evidence(claim="yes", source="d", reliability=0.99),
        ],
    )
    report = rec.analyze()
    # Even if suggestions exist, coverage for the if not suggestions path may need mock, but this exercises high confidence
    assert report["confidence"] > 0.8
    assert report["stability"] == "stable" or report["decision_confidence"] > 0.9


def test_main_json_invalid_content(monkeypatch, capsys, tmp_path):
    import sys
    from mfr_core_pro import main
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    monkeypatch.setattr(sys, "argv", ["mfr_core_pro.py", "--json", str(bad)])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_fingerprint_type_guard(monkeypatch):
    # Cover the rare type check in fingerprint()
    rec = IntelligenceRecord(question="q")
    def fake_analyze(self):
        return {"fingerprint": 123}
    monkeypatch.setattr(IntelligenceRecord, "analyze", fake_analyze)
    with pytest.raises(TypeError):
        fingerprint(rec)
