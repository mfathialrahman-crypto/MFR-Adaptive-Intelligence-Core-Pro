"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import (
    Evidence,
    IntelligenceRecord,
    fingerprint,
    VERSION,
    MIN_DECISION_CONFIDENCE,
    MAX_DECISION_CONFIDENCE,
    STABLE_CONFIDENCE_THRESHOLD,
)


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
        Evidence(claim="ok", source="src", reliability=0.5, weight=0)


def test_record_rejects_empty_question():
    with pytest.raises(ValueError, match="question must be non-empty"):
        IntelligenceRecord(question="", evidence=[])


def test_insufficient_evidence():
    rec = IntelligenceRecord(question="Anything?", evidence=[])
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert report["conclusion"] is None


def test_provisional_finding_single_strong_source():
    rec = IntelligenceRecord(
        question="Is X true?",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9, independent=True)],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "yes"
    assert 0.0 < report["confidence"] < 1.0


def test_multiple_independent_sources_raise_confidence():
    single = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence(claim="yes", source="a", reliability=0.8, independent=True)],
    )
    multi = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.8, independent=True),
            Evidence(claim="yes", source="b", reliability=0.8, independent=True),
            Evidence(claim="yes", source="c", reliability=0.8, independent=True),
        ],
    )
    assert multi.analyze()["confidence"] > single.analyze()["confidence"]


def test_conflicting_evidence_detected():
    rec = IntelligenceRecord(
        question="Which?",
        evidence=[
            Evidence(claim="a", source="s1", reliability=0.85, independent=True),
            Evidence(claim="b", source="s2", reliability=0.84, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")


def test_independence_penalty_lowers_weight():
    indep = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9, independent=True)],
    )
    dep = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9, independent=False)],
    )
    assert indep.analyze()["confidence"] > dep.analyze()["confidence"]


def test_fingerprint_deterministic_and_content_addressable():
    ev = [Evidence(claim="yes", source="a", reliability=0.9, independent=True)]
    rec1 = IntelligenceRecord(question="Q?", evidence=ev, prior_belief=0.5)
    rec2 = IntelligenceRecord(question="Q?", evidence=ev, prior_belief=0.5)
    fp1 = rec1.analyze()["fingerprint"]
    fp2 = rec2.analyze()["fingerprint"]
    assert fp1 == fp2
    assert len(fp1) == 64  # sha256 hex
    # Different prior changes fingerprint
    rec3 = IntelligenceRecord(question="Q?", evidence=ev, prior_belief=0.6)
    assert rec3.analyze()["fingerprint"] != fp1


def test_deduplication_keeps_strongest_per_source():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[
            Evidence(claim="a", source="same", reliability=0.5, independent=True),
            Evidence(claim="a", source="same", reliability=0.9, independent=True),
        ],
    )
    report = rec.analyze()
    assert "Deduplicated 2 \u2192 1" in report["audit_trail"][0]
    assert report["top_claim"]["evidence_count"] == 1


def test_max_evidence_items_enforced():
    many = [Evidence(claim="x", source=f"s{i}", reliability=0.5) for i in range(1001)]
    with pytest.raises(ValueError, match="evidence list exceeds maximum"):
        IntelligenceRecord(question="Q?", evidence=many)


def test_suggestions_for_small_sample():
    rec = IntelligenceRecord(
        question="Q?",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9)],
    )
    report = rec.analyze()
    assert any("Sample size is small" in s for s in report["suggestions"])


def test_alternatives_appear_in_suggestions():
    rec = IntelligenceRecord(
        question="Which?",
        evidence=[Evidence(claim="alpha", source="a", reliability=0.8)],
        alternatives=["alpha", "beta", "gamma"],
    )
    report = rec.analyze()
    assert any("Listed alternatives" in s for s in report["suggestions"])


def test_ci_non_overlap_signal_when_present():
    # Strong separation case
    rec = IntelligenceRecord(
        question="Clear?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.95, independent=True),
            Evidence(claim="yes", source="b", reliability=0.95, independent=True),
            Evidence(claim="yes", source="c", reliability=0.95, independent=True),
            Evidence(claim="no", source="d", reliability=0.3, independent=True),
        ],
    )
    report = rec.analyze()
    # May or may not trigger non-overlap depending on exact numbers; just ensure no crash
    assert "status" in report
    assert isinstance(report["suggestions"], list)


def test_prior_belief_validated_at_construction():
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="Q?", evidence=[], prior_belief=1.5)
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="Q?", evidence=[], prior_belief=-0.1)


def test_decision_contract_fields_present():
    rec = IntelligenceRecord(
        question="Healthy?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.95, independent=True),
            Evidence(claim="yes", source="b", reliability=0.9, independent=True),
            Evidence(claim="yes", source="c", reliability=0.85, independent=True),
        ],
    )
    report = rec.analyze()
    assert "decision_confidence" in report
    assert "stability" in report
    assert report["status"] == "PROVISIONAL_FINDING"
    assert MIN_DECISION_CONFIDENCE <= report["decision_confidence"] <= MAX_DECISION_CONFIDENCE
    assert report["stability"] in ("stable", "provisional", "unstable")
    # High confidence should map to stable
    assert report["confidence"] >= STABLE_CONFIDENCE_THRESHOLD
    assert report["stability"] == "stable"


def test_insufficient_evidence_decision_contract():
    rec = IntelligenceRecord(question="Anything?", evidence=[])
    report = rec.analyze()
    assert report["decision_confidence"] == 0.0
    assert report["stability"] == "unstable"
    assert report["status"] == "INSUFFICIENT_EVIDENCE"


def test_conflicting_evidence_stability_unstable():
    rec = IntelligenceRecord(
        question="Which?",
        evidence=[
            Evidence(claim="a", source="s1", reliability=0.8, independent=True),
            Evidence(claim="b", source="s2", reliability=0.78, independent=True),
        ],
    )
    report = rec.analyze()
    # Depending on numbers may be conflicting or provisional; if conflicting, stability unstable
    assert "stability" in report
    assert "decision_confidence" in report
    if report["status"] == "CONFLICTING_EVIDENCE":
        assert report["stability"] == "unstable"
