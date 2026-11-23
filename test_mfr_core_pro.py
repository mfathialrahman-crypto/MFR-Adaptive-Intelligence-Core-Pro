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
    analyze_json,
    fingerprint,
    validate_analysis_report,
    VERSION,
)
from version import VERSION as V2


def test_version_aligned():
    assert VERSION == V2
    assert VERSION == "2.1.75+pro"


def test_evidence_valid():
    e = Evidence(claim="ok", source="src", reliability=0.8)
    assert e.claim == "ok"
    assert e.independent is True
    assert e.weight == 1.0


def test_evidence_strips():
    e = Evidence(claim="  ok  ", source="  src  ", reliability=0.5)
    assert e.claim == "ok"
    assert e.source == "src"


@pytest.mark.parametrize("claim,source,rel,err", [
    ("", "s", 0.5, "claim must be non-empty"),
    ("c", "", 0.5, "source must be non-empty"),
    ("c", "s", -0.1, "reliability must be in [0.0, 1.0]"),
    ("c", "s", 1.1, "reliability must be in [0.0, 1.0]"),
    ("c", "s", 0.5, "weight must be > 0"),  # will set weight below
])
def test_evidence_validation_errors(claim, source, rel, err):
    with pytest.raises(ValueError, match=re.escape(err)):
        if "weight" in err:
            Evidence(claim=claim, source=source, reliability=rel, weight=0)
        else:
            Evidence(claim=claim, source=source, reliability=rel)


def test_evidence_max_lengths():
    with pytest.raises(ValueError, match="claim exceeds"):
        Evidence(claim="x" * 501, source="s", reliability=0.5)
    with pytest.raises(ValueError, match="source exceeds"):
        Evidence(claim="c", source="x" * 201, reliability=0.5)


def test_record_basic():
    rec = IntelligenceRecord(question="Q?")
    assert rec.question == "Q?"
    assert rec.prior_belief == 0.5
    assert len(rec.evidence) == 0
    assert rec.record_id
    assert rec.created_at


def test_record_strips_question():
    rec = IntelligenceRecord(question="  Q?  ")
    assert rec.question == "Q?"


@pytest.mark.parametrize("q,prior,err", [
    ("", 0.5, "question must be non-empty"),
    ("x" * 1001, 0.5, "question exceeds max length"),
    ("Q", -0.1, "prior_belief must be in [0.0, 1.0]"),
    ("Q", 1.1, "prior_belief must be in [0.0, 1.0]"),
])
def test_record_validation(q, prior, err):
    with pytest.raises(ValueError, match=re.escape(err)):
        IntelligenceRecord(question=q, prior_belief=prior)


def test_record_alternatives_normalize():
    rec = IntelligenceRecord(question="Q", alternatives=["  a  ", "", "b", "  "])
    assert rec.alternatives == ["a", "b"]


def test_record_alt_max():
    with pytest.raises(ValueError, match="alternative exceeds"):
        IntelligenceRecord(question="Q", alternatives=["x" * 201])
    with pytest.raises(ValueError, match="alternatives list exceeds"):
        IntelligenceRecord(question="Q", alternatives=["a"] * 21)


def test_record_evidence_max():
    evs = [Evidence("c", f"s{i}", 0.5) for i in range(1001)]
    with pytest.raises(ValueError, match="evidence list exceeds"):
        IntelligenceRecord(question="Q", evidence=evs)


def test_to_json_from_json_roundtrip():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence("claim1", "src1", 0.8, True, 1.2)],
        alternatives=["alt1", "alt2"],
        prior_belief=0.6,
    )
    raw = rec.to_json()
    rec2 = IntelligenceRecord.from_json(raw)
    assert rec2.question == rec.question
    assert rec2.prior_belief == rec.prior_belief
    assert len(rec2.evidence) == 1
    assert rec2.evidence[0].claim == "claim1"
    assert rec2.alternatives == ["alt1", "alt2"]


def test_from_json_invalid():
    with pytest.raises(ValueError, match="invalid JSON"):
        IntelligenceRecord.from_json("not json")
    with pytest.raises(ValueError, match="JSON root must be an object"):
        IntelligenceRecord.from_json("[]")
    with pytest.raises(ValueError, match="missing or invalid 'question'"):
        IntelligenceRecord.from_json("{}")
    with pytest.raises(ValueError, match="evidence\\[0\\] must be an object"):
        IntelligenceRecord.from_json('{"question":"Q","evidence":[1]}')
    with pytest.raises(ValueError, match="prior_belief must be a number"):
        IntelligenceRecord.from_json('{"question":"Q","prior_belief":"bad"}')


def test_analyze_insufficient_no_evidence():
    rec = IntelligenceRecord(question="Q?")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert report["conclusion"] is None
    assert report["stability"] == "unstable"
    assert report["decision_confidence"] == 0.3
    assert "evidence" in report.get("missing", [])
    assert len(report["fingerprint"]) == 64
    assert validate_analysis_report(report) == []


def test_analyze_provisional_single():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence("yes", "s1", 0.9)],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "yes"
    assert report["top_claim"]["evidence_count"] == 1
    assert any("single source" in s for s in report["suggestions"])
    assert validate_analysis_report(report) == []


def test_analyze_multiple_coherent():
    rec = IntelligenceRecord(
        question="Healthy?",
        evidence=[
            Evidence("healthy", "m1", 0.9),
            Evidence("healthy", "m2", 0.85),
            Evidence("healthy", "m3", 0.8),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["confidence"] > 0.7
    assert report["stability"] in ("stable", "provisional")
    assert any("coherent" in s or "monitoring" in s for s in report["suggestions"])
    fp1 = report["fingerprint"]
    # deterministic
    assert rec.analyze()["fingerprint"] == fp1


def test_analyze_conflict():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence("A", "s1", 0.8),
            Evidence("B", "s2", 0.75),
        ],
    )
    report = rec.analyze()
    # Means close, CIs likely overlap
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")
    assert len(report["competing_claims"]) >= 1


def test_analyze_dedup():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence("claim", "same", 0.6),
            Evidence("claim", "same", 0.9),  # stronger kept
        ],
    )
    report = rec.analyze()
    assert "Deduplicated" in " ".join(report["audit_trail"])
    assert report["top_claim"]["evidence_count"] == 1


def test_analyze_independence_penalty():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence("yes", "s1", 0.9, independent=False),
            Evidence("yes", "s2", 0.9, independent=True),
        ],
    )
    report = rec.analyze()
    assert any("independence penalty" in s for s in report["suggestions"])


def test_analyze_alternatives_mentioned():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence("yes", "s1", 0.9)],
        alternatives=["no", "maybe"],
    )
    report = rec.analyze()
    assert any("Listed alternatives" in s for s in report["suggestions"])


def test_fingerprint_deterministic():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("c", "s", 0.5)],
    )
    fp1 = fingerprint(rec)
    fp2 = fingerprint(rec)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_validate_report_good():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    report = rec.analyze()
    assert validate_analysis_report(report) == []


def test_validate_report_bad():
    assert "report must be a dict" in validate_analysis_report([])
    bad = {"status": "BAD"}
    viols = validate_analysis_report(bad)
    assert any("missing required" in v for v in viols)
    assert any("invalid status" in v for v in viols)


def test_analyze_json_helper():
    raw = json.dumps({
        "question": "Test?",
        "evidence": [{"claim": "yes", "source": "t", "reliability": 0.8}],
    })
    report = analyze_json(raw)
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "yes"


def test_ci_non_overlap_suggestion():
    # Strong separation
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence("strong", "s1", 0.99),
            Evidence("strong", "s2", 0.99),
            Evidence("strong", "s3", 0.99),
            Evidence("weak", "s4", 0.1),
        ],
    )
    report = rec.analyze()
    assert any("CI" in s or "do not overlap" in s for s in report["suggestions"])


def test_demo_runs(capsys):
    from mfr_core_pro import _demo
    _demo()
    captured = capsys.readouterr()
    assert "Demo" in captured.out
    assert "Fingerprint" in captured.out


def test_main_version(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--version"]):
        main()
    captured = capsys.readouterr()
    assert "2.1.75+pro" in captured.out


def test_main_json_file(tmp_path, capsys):
    from mfr_core_pro import main
    p = tmp_path / "rec.json"
    p.write_text(json.dumps({
        "question": "File test?",
        "evidence": [{"claim": "ok", "source": "f", "reliability": 0.7}],
    }))
    with patch("sys.argv", ["mfr-core", "--json", str(p)]):
        main()
    captured = capsys.readouterr()
    assert "ok" in captured.out
    assert "PROVISIONAL" in captured.out


def test_main_json_stdin(capsys):
    from mfr_core_pro import main
    raw = json.dumps({
        "question": "Stdin?",
        "evidence": [{"claim": "yes", "source": "in", "reliability": 0.8}],
    })
    with patch("sys.argv", ["mfr-core", "--json", "-"]), \
         patch("sys.stdin", StringIO(raw)):
        main()
    captured = capsys.readouterr()
    assert "yes" in captured.out


def test_main_file_not_found(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--json", "/nonexistent/file.json"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "file not found" in captured.err


def test_main_invalid_json(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--json", "-"]), \
         patch("sys.stdin", StringIO("bad")):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_main_no_args_runs_demo(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core"]):
        main()
    captured = capsys.readouterr()
    assert "Demo complete" in captured.out


def test_stability_stable():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", f"s{i}", 0.95) for i in range(5)],
    )
    report = rec.analyze()
    assert report["stability"] == "stable"
    assert report["confidence"] > 0.75


def test_stability_provisional_low_conf():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s1", 0.55)],
    )
    report = rec.analyze()
    assert report["stability"] in ("provisional", "unstable")


def test_weight_affects():
    rec_high = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.9, weight=5.0)],
    )
    rec_low = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.9, weight=0.1)],
    )
    assert rec_high.analyze()["confidence"] > rec_low.analyze()["confidence"]


def test_prior_affects():
    rec_high_prior = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.6)],
        prior_belief=0.8,
    )
    rec_low_prior = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.6)],
        prior_belief=0.2,
    )
    assert rec_high_prior.analyze()["confidence"] > rec_low_prior.analyze()["confidence"]


def test_empty_suggestions_fallback():
    # Force no suggestions by crafting high evidence coherent no alts no non-indep
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", f"s{i}", 0.9) for i in range(4)],
    )
    report = rec.analyze()
    # Should have coherent suggestion or fallback
    assert len(report["suggestions"]) >= 1


def test_record_id_preserved():
    raw = json.dumps({
        "question": "Q",
        "record_id": "fixed-id-123",
        "evidence": [],
    })
    rec = IntelligenceRecord.from_json(raw)
    assert rec.record_id == "fixed-id-123"


def test_created_at_preserved():
    raw = json.dumps({
        "question": "Q",
        "created_at": "2020-01-01T00:00:00+00:00",
        "evidence": [],
    })
    rec = IntelligenceRecord.from_json(raw)
    assert rec.created_at == "2020-01-01T00:00:00+00:00"


# Additional edge to push coverage
def test_analyze_with_many_competitors():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("A", "s1", 0.9),
            Evidence("B", "s2", 0.8),
            Evidence("C", "s3", 0.7),
            Evidence("D", "s4", 0.6),
            Evidence("E", "s5", 0.5),
        ],
    )
    report = rec.analyze()
    assert len(report["competing_claims"]) == 3  # capped at 3


def test_fingerprint_ignores_timestamps():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.5)])
    fp1 = fingerprint(rec)
    # mutate created_at shouldn't change if we re-analyze (fingerprint excludes it)
    rec.created_at = "changed"
    fp2 = fingerprint(rec)
    assert fp1 == fp2


print("Test module loaded with comprehensive cases")


def test_conflict_score_present():
    rec = IntelligenceRecord(question="Q", evidence=[
        Evidence("A", "s1", 0.8),
        Evidence("B", "s2", 0.75),
    ])
    report = rec.analyze()
    assert "conflict_score" in report
    assert 0.0 <= report["conflict_score"] <= 1.0
    assert report["status"] == "CONFLICTING_EVIDENCE"
    assert any("conflict score" in s.lower() for s in report["suggestions"])

def test_conflict_score_no_evidence():
    rec = IntelligenceRecord(question="Q")
    report = rec.analyze()
    assert report["conflict_score"] == 0.0
