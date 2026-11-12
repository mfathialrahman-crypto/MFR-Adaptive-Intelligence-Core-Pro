"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION, MAX_EVIDENCE_ITEMS, validate_analysis_report, analyze_json


def test_version_present():
    assert VERSION.startswith("2.1.")
    assert VERSION.endswith("-pro")


def test_evidence_validation_rejects_empty_claim():
    with pytest.raises(ValueError, match="claim must be non-empty"):
        Evidence(claim="", source="src", reliability=0.5)


def test_evidence_validation_rejects_bad_reliability():
    with pytest.raises(ValueError, match="reliability must be in"):
        Evidence(claim="ok", source="src", reliability=1.5)


def test_evidence_validation_rejects_zero_weight():
    with pytest.raises(ValueError, match="weight must be > 0"):
        Evidence(claim="ok", source="src", reliability=0.5, weight=0.0)


def test_record_rejects_empty_question():
    with pytest.raises(ValueError, match="question must be non-empty"):
        IntelligenceRecord(question="   ", evidence=[])


def test_insufficient_evidence():
    rec = IntelligenceRecord(question="Is it true?")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert report["conclusion"] is None
    assert "evidence" in report.get("missing", [])
    assert report["version"] == VERSION


def test_provisional_finding_single_strong_source():
    rec = IntelligenceRecord(
        question="Healthy?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.95, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "yes"
    assert report["confidence"] > 0.5
    assert any("single source" in s for s in report["suggestions"])


def test_multiple_independent_sources_raise_confidence():
    rec = IntelligenceRecord(
        question="Healthy?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.9, independent=True),
            Evidence(claim="yes", source="b", reliability=0.88, independent=True),
            Evidence(claim="yes", source="c", reliability=0.85, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "yes"
    assert report["confidence"] > 0.7


def test_conflicting_evidence_detected():
    rec = IntelligenceRecord(
        question="Status?",
        evidence=[
            Evidence(claim="healthy", source="a", reliability=0.7, independent=True),
            Evidence(claim="healthy", source="b", reliability=0.65, independent=True),
            Evidence(claim="degraded", source="c", reliability=0.72, independent=True),
            Evidence(claim="degraded", source="d", reliability=0.68, independent=True),
        ],
    )
    report = rec.analyze()
    # With balanced strong evidence on both sides, expect conflict or close provisional
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")
    # competing_claims excludes the top claim (semantic contract)
    assert report["top_claim"] is not None
    top_claim = report["top_claim"]["claim"]
    competing_claims = [c["claim"] for c in report["competing_claims"]]
    assert top_claim not in competing_claims
    assert len(report["competing_claims"]) >= 1


def test_competing_claims_excludes_top():
    """competing_claims must never include the top_claim itself."""
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence(claim="alpha", source="s1", reliability=0.9, independent=True),
            Evidence(claim="beta", source="s2", reliability=0.7, independent=True),
            Evidence(claim="gamma", source="s3", reliability=0.5, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["top_claim"] is not None
    top = report["top_claim"]["claim"]
    competing = [c["claim"] for c in report["competing_claims"]]
    assert top not in competing
    assert "beta" in competing or "gamma" in competing
    # Single-claim case → empty competitors
    rec_single = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence(claim="only", source="s1", reliability=0.95)],
    )
    rep_single = rec_single.analyze()
    assert rep_single["top_claim"]["claim"] == "only"
    assert rep_single["competing_claims"] == []


def test_independence_penalty_lowers_weight():
    rec_indep = IntelligenceRecord(
        question="Claim?",
        evidence=[
            Evidence(claim="true", source="a", reliability=0.9, independent=True),
            Evidence(claim="true", source="b", reliability=0.9, independent=True),
        ],
    )
    rec_dep = IntelligenceRecord(
        question="Claim?",
        evidence=[
            Evidence(claim="true", source="a", reliability=0.9, independent=True),
            Evidence(claim="true", source="b", reliability=0.9, independent=False),
        ],
    )
    # Independence penalty should result in lower or equal confidence for dependent case
    assert rec_dep.analyze()["confidence"] <= rec_indep.analyze()["confidence"] + 1e-6


def test_fingerprint_deterministic_and_content_addressable():
    rec1 = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="c", source="s", reliability=0.8)],
    )
    rec2 = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="c", source="s", reliability=0.8)],
    )
    assert fingerprint(rec1) == fingerprint(rec2)
    assert len(fingerprint(rec1)) == 64


def test_fingerprint_includes_alternatives():
    rec_a = IntelligenceRecord(question="Q", alternatives=["a"])
    rec_b = IntelligenceRecord(question="Q", alternatives=["b"])
    assert fingerprint(rec_a) != fingerprint(rec_b)


def test_deduplication_keeps_strongest_per_source():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence(claim="weak", source="same", reliability=0.3),
            Evidence(claim="strong", source="same", reliability=0.9),
        ],
    )
    report = rec.analyze()
    assert report["top_claim"]["claim"] == "strong"


def test_max_evidence_items_enforced():
    evids = [Evidence(claim="c", source=f"s{i}", reliability=0.5) for i in range(MAX_EVIDENCE_ITEMS + 1)]
    with pytest.raises(ValueError, match="exceeds maximum"):
        IntelligenceRecord(question="Q", evidence=evids)


def test_suggestions_for_small_sample():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="c", source="s", reliability=0.8)],
    )
    report = rec.analyze()
    assert any("small" in s.lower() or "single" in s.lower() for s in report["suggestions"])


def test_alternatives_appear_in_suggestions():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="c", source="s", reliability=0.8)],
        alternatives=["alt1", "alt2"],
    )
    report = rec.analyze()
    assert any("alt1" in s for s in report["suggestions"])


def test_ci_non_overlap_signal_when_present():
    # Strong separation
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence(claim="high", source="a", reliability=0.95),
            Evidence(claim="high", source="b", reliability=0.95),
            Evidence(claim="high", source="c", reliability=0.95),
            Evidence(claim="low", source="d", reliability=0.1),
        ],
    )
    report = rec.analyze()
    assert any("do not overlap" in s for s in report["suggestions"])


def test_prior_belief_validated_on_construction():
    with pytest.raises(ValueError):
        IntelligenceRecord(question="Q", prior_belief=1.5)


def test_decision_contract_fields_present():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="yes", source="s", reliability=0.8)],
    )
    report = rec.analyze()
    for field in ["status", "confidence", "decision_confidence", "stability", "suggestions", "fingerprint"]:
        assert field in report


def test_insufficient_evidence_decision_contract():
    rec = IntelligenceRecord(question="Q")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["stability"] == "unstable"
    assert report["decision_confidence"] >= 0.3


def test_evidence_validation_rejects_empty_source():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="ok", source="", reliability=0.5)


def test_demo_runs_without_error():
    from mfr_core_pro import _demo
    _demo()  # should not raise


def test_coherent_evidence_default_suggestion():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.9),
            Evidence(claim="yes", source="b", reliability=0.9),
            Evidence(claim="yes", source="c", reliability=0.9),
        ],
    )
    report = rec.analyze()
    assert any("coherent" in s.lower() or "monitoring" in s.lower() for s in report["suggestions"])


def test_evidence_rejects_too_long_claim():
    with pytest.raises(ValueError, match="exceeds max length"):
        Evidence(claim="x" * 501, source="s", reliability=0.5)


def test_evidence_rejects_too_long_source():
    with pytest.raises(ValueError, match="exceeds max length"):
        Evidence(claim="c", source="x" * 201, reliability=0.5)


def test_evidence_accepts_max_lengths():
    Evidence(claim="x" * 500, source="s" * 200, reliability=0.5)


def test_record_rejects_too_long_question():
    with pytest.raises(ValueError, match="exceeds max length"):
        IntelligenceRecord(question="x" * 1001)


def test_record_accepts_max_question_length():
    IntelligenceRecord(question="x" * 1000)


def test_analyze_enforces_evidence_limit_after_mutation():
    rec = IntelligenceRecord(question="Q")
    # mutate after construction to bypass constructor check
    rec.evidence = [Evidence(claim="c", source=f"s{i}", reliability=0.5) for i in range(MAX_EVIDENCE_ITEMS + 1)]
    with pytest.raises(ValueError, match="exceeds maximum"):
        rec.analyze()


def test_alternatives_length_and_count_bounds():
    with pytest.raises(ValueError, match="exceeds max length"):
        IntelligenceRecord(question="Q", alternatives=["x" * 201])
    with pytest.raises(ValueError, match="exceeds maximum"):
        IntelligenceRecord(question="Q", alternatives=["a"] * 21)


def test_serialization_round_trip_preserves_fingerprint():
    rec = IntelligenceRecord(
        question="Round trip",
        evidence=[Evidence(claim="yes", source="s", reliability=0.75)],
        alternatives=["yes", "no"],
    )
    raw = rec.to_json()
    restored = IntelligenceRecord.from_json(raw)
    assert fingerprint(rec) == fingerprint(restored)


def test_version_aligned_with_pyproject():
    import re
    with open("pyproject.toml") as f:
        content = f.read()
    m = re.search(r'version\s*=\s*"([^"]+)"', content)
    assert m is not None
    assert m.group(1) == VERSION


def test_every_analyze_path_passes_validator():
    cases = [
        IntelligenceRecord(question="empty"),
        IntelligenceRecord(question="single", evidence=[Evidence(claim="a", source="s", reliability=0.9)]),
        IntelligenceRecord(
            question="multi",
            evidence=[
                Evidence(claim="a", source="s1", reliability=0.9),
                Evidence(claim="b", source="s2", reliability=0.4),
            ],
        ),
    ]
    for rec in cases:
        report = rec.analyze()
        assert not validate_analysis_report(report)


def test_validator_rejects_bad_report():
    bad = {"status": "UNKNOWN", "confidence": 2.0}
    violations = validate_analysis_report(bad)
    assert len(violations) > 0


def test_validator_rejects_non_dict():
    assert validate_analysis_report("not a dict")


def test_validator_rejects_bad_fingerprint_and_non_list():
    bad = {
        "version": "x",
        "record_id": "x",
        "status": "PROVISIONAL_FINDING",
        "question": "q",
        "confidence": 0.5,
        "decision_confidence": 0.5,
        "stability": "stable",
        "suggestions": "not a list",
        "audit_trail": [],
        "created_at": "t",
        "analyzed_at": "t",
        "fingerprint": "short",
    }
    violations = validate_analysis_report(bad)
    assert any("fingerprint must be 64-char" in v for v in violations)
    assert any("suggestions must be a list" in v for v in violations)


def test_analyze_json_roundtrip():
    record = IntelligenceRecord(
        question="CLI path",
        evidence=[Evidence(claim="works", source="test", reliability=0.8)],
    )
    raw = record.to_json()
    report = analyze_json(raw)
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["fingerprint"] == record.analyze()["fingerprint"]
    assert not validate_analysis_report(report)


def test_zero_reliability_evidence_handled():
    ev = Evidence(claim="weak", source="zero", reliability=0.0, weight=1.0)
    record = IntelligenceRecord(question="zero rel", evidence=[ev])
    report = record.analyze()
    assert report["status"] in ("PROVISIONAL_FINDING", "INSUFFICIENT_EVIDENCE")
    assert not validate_analysis_report(report)


def test_cli_json_path(tmp_path):
    """Cover the --json CLI entry point."""
    import subprocess
    import sys
    rec = IntelligenceRecord(
        question="CLI test",
        evidence=[Evidence(claim="ok", source="cli", reliability=0.85)],
    )
    json_file = tmp_path / "input.json"
    json_file.write_text(rec.to_json())
    result = subprocess.run(
        [sys.executable, "mfr_core_pro.py", "--json", str(json_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    import json
    out = json.loads(result.stdout)
    assert out["status"] == "PROVISIONAL_FINDING"
    assert out["conclusion"] == "ok"
    assert not validate_analysis_report(out)


def test_cli_usage_when_no_file():
    """Cover usage message when --json without file."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "mfr_core_pro.py", "--json"],
        capture_output=True,
        text=True,
    )
    assert "Usage:" in result.stdout
    assert result.returncode == 0


def test_default_suggestion_when_no_specific():
    """Hit the fallback suggestion path."""
    rec = IntelligenceRecord(
        question="Stable?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.6, independent=True),
            Evidence(claim="yes", source="b", reliability=0.55, independent=True),
            Evidence(claim="yes", source="c", reliability=0.5, independent=True),
        ],
    )
    report = rec.analyze()
    # With moderate reliability and 3 sources, may hit default or coherent
    assert isinstance(report["suggestions"], list)
    assert len(report["suggestions"]) >= 1
    assert not validate_analysis_report(report)

def test_from_json_rejects_invalid_json():
    with pytest.raises(ValueError, match='invalid JSON'):
        IntelligenceRecord.from_json('{bad')

def test_from_json_rejects_missing_question():
    with pytest.raises(ValueError, match='question'):
        IntelligenceRecord.from_json('{}')

def test_from_json_rejects_non_object():
    with pytest.raises(ValueError, match='object'):
        IntelligenceRecord.from_json('[]')
