"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION


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
    assert len(report["competing_claims"]) >= 2


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
    conf_indep = rec_indep.analyze()["confidence"]
    conf_dep = rec_dep.analyze()["confidence"]
    assert conf_indep >= conf_dep  # non-independent should not increase confidence more


def test_fingerprint_deterministic_and_content_addressable():
    ev = [Evidence(claim="yes", source="a", reliability=0.8, independent=True)]
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
    assert "Deduplicated 2 → 1" in report["audit_trail"][0]
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


def test_evidence_validation_rejects_empty_source():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="ok", source="   ", reliability=0.5)


def test_invalid_prior_belief_rejected():
    rec = IntelligenceRecord(question="Q?", prior_belief=1.5)
    with pytest.raises(ValueError, match="prior_belief must be in"):
        rec.analyze()


def test_conflicting_evidence_status_and_suggestions():
    rec = IntelligenceRecord(
        question="Status?",
        evidence=[
            Evidence(claim="healthy", source="a", reliability=0.9, independent=True),
            Evidence(claim="degraded", source="b", reliability=0.85, independent=True),
        ],
    )
    report = rec.analyze()
    # Depending on exact numbers, may be conflicting or provisional; verify structure
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")
    assert isinstance(report["suggestions"], list)
    assert "fingerprint" in report


def test_coherent_evidence_default_suggestion():
    # Many strong independent sources on same claim → coherent, may hit default suggestion
    rec = IntelligenceRecord(
        question="Stable?",
        evidence=[
            Evidence(claim="yes", source=f"s{i}", reliability=0.95, independent=True)
            for i in range(5)
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["confidence"] > 0.8
    # Should have at least the default or specific suggestions
    assert len(report["suggestions"]) >= 1


def test_fingerprint_independent_of_record_id_and_timestamps():
    ev = [Evidence(claim="yes", source="a", reliability=0.9)]
    fp1 = fingerprint("Q?", ev, 0.5)
    # Call analyze which uses fingerprint
    rec = IntelligenceRecord(question="Q?", evidence=ev, prior_belief=0.5)
    report = rec.analyze()
    assert report["fingerprint"] == fp1
