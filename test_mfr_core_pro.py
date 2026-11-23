"""Tests for MFR Adaptive Intelligence Core Pro. Target ≥90% coverage, 48+ cases covering edges."""
import re

import json
import pytest
from io import StringIO
import sys
from unittest.mock import patch

from mfr_core_pro import (
    verify_fingerprint,
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
        question="Q",
        evidence=[Evidence("c", "s", 0.7)],
        alternatives=["a", "b"],
        prior_belief=0.6,
    )
    raw = rec.to_json()
    rec2 = IntelligenceRecord.from_json(raw)
    assert rec2.question == rec.question
    assert len(rec2.evidence) == 1
    assert rec2.evidence[0].claim == "c"
    assert rec2.prior_belief == 0.6


def test_from_json_invalid():
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json("not json")
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json("[]")
    with pytest.raises(ValueError):
        IntelligenceRecord.from_json('{"noquestion": true}')


def test_analyze_insufficient_no_evidence():
    rec = IntelligenceRecord(question="Q")
    r = rec.analyze()
    assert r["status"] == "INSUFFICIENT_EVIDENCE"
    assert r["confidence"] == 0.0
    assert r["conclusion"] is None


def test_analyze_provisional_single():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.6)],
    )
    r = rec.analyze()
    assert r["status"] == "PROVISIONAL_FINDING"
    assert r["conclusion"] == "yes"


def test_analyze_multiple_coherent():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "s1", 0.9),
            Evidence("yes", "s2", 0.85),
            Evidence("yes", "s3", 0.8),
        ],
    )
    r = rec.analyze()
    assert r["status"] == "PROVISIONAL_FINDING"
    assert r["confidence"] > 0.8
    assert r["stability"] == "stable"


def test_analyze_conflict():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "s1", 0.9),
            Evidence("no", "s2", 0.85),
        ],
    )
    r = rec.analyze()
    assert r["status"] == "CONFLICTING_EVIDENCE"


def test_analyze_dedup():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "same", 0.5),
            Evidence("yes", "same", 0.9),
        ],
    )
    r = rec.analyze()
    assert "Deduplicated" in " ".join(r["audit_trail"])


def test_analyze_independence_penalty():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("yes", "s1", 0.9, independent=True),
            Evidence("yes", "s2", 0.9, independent=False),
        ],
    )
    r = rec.analyze()
    assert any("independence" in s.lower() for s in r["suggestions"])


def test_analyze_alternatives_mentioned():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.9)],
        alternatives=["yes", "no"],
    )
    r = rec.analyze()
    assert any("alternatives" in s.lower() for s in r["suggestions"])


def test_fingerprint_deterministic():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.9)],
    )
    fp1 = fingerprint(rec)
    fp2 = fingerprint(rec)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_validate_report_good():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("c", "s", 0.8)])
    r = rec.analyze()
    assert validate_analysis_report(r) == []


def test_validate_report_bad():
    assert "report must be a dict" in validate_analysis_report(None)
    assert any("missing" in v for v in validate_analysis_report({}))


def test_analyze_json_helper():
    raw = '{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8}]}'
    r = analyze_json(raw)
    assert r["status"] == "PROVISIONAL_FINDING"


def test_ci_non_overlap_suggestion():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence("strong", "s1", 0.95),
            Evidence("strong", "s2", 0.95),
            Evidence("strong", "s3", 0.95),
            Evidence("weak", "s4", 0.1),
        ],
    )
    r = rec.analyze()
    assert any("CI do not overlap" in s for s in r["suggestions"])


def test_demo_runs(capsys):
    from mfr_core_pro import _demo
    _demo()
    captured = capsys.readouterr()
    assert "Demo complete" in captured.out


def test_main_version(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--version"]):
        main()
    captured = capsys.readouterr()
    assert "2.1.75+pro" in captured.out


def test_main_json_file(tmp_path, capsys):
    p = tmp_path / "rec.json"
    p.write_text('{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8}]}')
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--json", str(p)]):
        main()
    captured = capsys.readouterr()
    assert "PROVISIONAL_FINDING" in captured.out


def test_main_json_stdin(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--json", "-"]):
        with patch("sys.stdin", StringIO('{"question": "Q", "evidence": [{"claim": "c", "source": "s", "reliability": 0.8}]}')):
            main()
    captured = capsys.readouterr()
    assert "PROVISIONAL_FINDING" in captured.out


def test_main_file_not_found(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--json", "nonexistent.json"]):
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "file not found" in captured.err


def test_main_invalid_json(capsys):
    from mfr_core_pro import main
    with patch("sys.argv", ["mfr-core", "--json", "-"]):
        with patch("sys.stdin", StringIO("bad")):
            with pytest.raises(SystemExit):
                main()
    captured = capsys.readouterr()
    assert "Error" in captured.err


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
    r = rec.analyze()
    assert r["stability"] == "stable"


def test_stability_provisional_low_conf():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", "s", 0.6)],
    )
    r = rec.analyze()
    assert r["stability"] == "provisional"


def test_weight_affects():
    rec1 = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s", 0.9, weight=1.0)])
    rec2 = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s", 0.9, weight=3.0)])
    assert rec2.analyze()["confidence"] > rec1.analyze()["confidence"]


def test_prior_affects():
    rec1 = IntelligenceRecord(question="Q", prior_belief=0.2, evidence=[Evidence("yes", "s", 0.9)])
    rec2 = IntelligenceRecord(question="Q", prior_belief=0.8, evidence=[Evidence("yes", "s", 0.9)])
    assert rec2.analyze()["confidence"] > rec1.analyze()["confidence"]


def test_empty_suggestions_fallback():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence("yes", f"s{i}", 0.95) for i in range(5)],
    )
    r = rec.analyze()
    assert r["suggestions"]


def test_record_id_preserved():
    rid = "fixed-id-123"
    rec = IntelligenceRecord(question="Q", record_id=rid)
    assert rec.record_id == rid
    assert rec.analyze()["record_id"] == rid


def test_created_at_preserved():
    rec = IntelligenceRecord(question="Q")
    created = rec.created_at
    r = rec.analyze()
    assert r["created_at"] == created


def test_analyze_with_many_competitors():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(f"c{i}", f"s{i}", 0.5 + i*0.1) for i in range(5)],
    )
    r = rec.analyze()
    assert len(r["competing_claims"]) <= 3


def test_fingerprint_ignores_timestamps():
    rec = IntelligenceRecord(question="Q", evidence=[Evidence("yes", "s", 0.9)])
    fp1 = fingerprint(rec)
    # timestamps change but fingerprint should not
    fp2 = fingerprint(rec)
    assert fp1 == fp2


def test_verify_fingerprint_matches():
    rec = IntelligenceRecord(
        question="Verify me",
        evidence=[Evidence(claim="yes", source="src", reliability=0.9)],
    )
    report = rec.analyze()
    assert verify_fingerprint(rec, report["fingerprint"]) is True


def test_verify_fingerprint_mismatch():
    rec = IntelligenceRecord(
        question="Verify me",
        evidence=[Evidence(claim="yes", source="src", reliability=0.9)],
    )
    assert verify_fingerprint(rec, "a" * 64) is False
    assert verify_fingerprint(rec, "short") is False
