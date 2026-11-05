"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION, MAX_EVIDENCE_ITEMS


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
    # Strong separation case engineered to produce non-overlapping 95% CIs
    rec = IntelligenceRecord(
        question="Clear?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.99, weight=2.0, independent=True),
            Evidence(claim="yes", source="b", reliability=0.99, weight=2.0, independent=True),
            Evidence(claim="yes", source="c", reliability=0.99, weight=2.0, independent=True),
            Evidence(claim="no", source="d", reliability=0.05, weight=0.1, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert any("do not overlap" in s for s in report["suggestions"])
    assert any("does not overlap second-claim CI" in a for a in report["audit_trail"])


def test_prior_belief_validated_on_construction():
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="Q?", prior_belief=1.5)
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="Q?", prior_belief=-0.1)
    # Valid extremes succeed
    IntelligenceRecord(question="Q?", prior_belief=0.0)
    IntelligenceRecord(question="Q?", prior_belief=1.0)


def test_decision_contract_fields_present():
    rec = IntelligenceRecord(
        question="Healthy?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.95, independent=True),
            Evidence(claim="yes", source="b", reliability=0.92, independent=True),
        ],
    )
    report = rec.analyze()
    assert "decision_confidence" in report
    assert "stability" in report
    assert 0.3 <= report["decision_confidence"] <= 0.98
    assert report["stability"] in ("stable", "provisional", "unstable")
    # High confidence provisional should be stable
    if report["status"] == "PROVISIONAL_FINDING" and report["confidence"] >= 0.75:
        assert report["stability"] == "stable"
    # decision_confidence is clamped version of confidence
    assert abs(report["decision_confidence"] - max(0.3, min(0.98, report["confidence"]))) < 1e-9


def test_insufficient_evidence_decision_contract():
    rec = IntelligenceRecord(question="Unknown?")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["stability"] == "unstable"
    assert report["decision_confidence"] == 0.3  # clamped floor
    assert report["confidence"] == 0.0


def test_evidence_validation_rejects_empty_source():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="ok", source="   ", reliability=0.5)
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="ok", source="", reliability=0.5)


def test_demo_runs_without_error(capsys):
    """Cover the built-in demo path used by CI and local verification."""
    from mfr_core_pro import _demo
    _demo()
    captured = capsys.readouterr()
    assert "MFR Adaptive Intelligence Core Pro — Demo" in captured.out
    assert "Demo complete." in captured.out
    assert "Status:" in captured.out


def test_coherent_evidence_default_suggestion():
    """When evidence is sufficient and coherent, the default monitoring suggestion appears."""
    rec = IntelligenceRecord(
        question="Stable?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.95, independent=True),
            Evidence(claim="yes", source="b", reliability=0.92, independent=True),
            Evidence(claim="yes", source="c", reliability=0.90, independent=True),
            Evidence(claim="yes", source="d", reliability=0.88, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert any("reasonably coherent" in s for s in report["suggestions"])


def test_evidence_rejects_too_long_claim():
    with pytest.raises(ValueError, match="claim exceeds max length"):
        Evidence(claim="a" * 501, source="ok", reliability=0.5)


def test_evidence_rejects_too_long_source():
    with pytest.raises(ValueError, match="source exceeds max length"):
        Evidence(claim="ok", source="b" * 201, reliability=0.5)


def test_evidence_accepts_max_lengths():
    e = Evidence(claim="a" * 500, source="b" * 200, reliability=0.5)
    assert len(e.claim) == 500
    assert len(e.source) == 200


def test_record_rejects_too_long_question():
    with pytest.raises(ValueError, match="question exceeds max length"):
        IntelligenceRecord(question="q" * 1001)


def test_record_accepts_max_question_length():
    rec = IntelligenceRecord(question="q" * 1000)
    assert len(rec.question) == 1000


def test_analyze_enforces_evidence_limit_after_mutation():
    """Evidence bound is re-checked in analyze() to protect against post-construction mutation."""
    rec = IntelligenceRecord(question="Q?", evidence=[Evidence(claim="x", source="s0", reliability=0.5)])
    # Mutate beyond limit
    rec.evidence = [Evidence(claim="x", source=f"s{i}", reliability=0.5) for i in range(MAX_EVIDENCE_ITEMS + 1)]
    with pytest.raises(ValueError, match="evidence list exceeds maximum"):
        rec.analyze()


def test_evidence_serialization_roundtrip():
    e = Evidence(claim="healthy", source="monitor", reliability=0.85, independent=False, weight=1.5)
    d = e.to_dict()
    e2 = Evidence.from_dict(d)
    assert e2.claim == e.claim
    assert e2.source == e.source
    assert e2.reliability == e.reliability
    assert e2.independent == e.independent
    assert e2.weight == e.weight


def test_evidence_from_dict_rejects_invalid():
    with pytest.raises(ValueError):
        Evidence.from_dict({"claim": "", "source": "s", "reliability": 0.5})


def test_record_serialization_roundtrip():
    ev = [Evidence(claim="yes", source="a", reliability=0.9), Evidence(claim="no", source="b", reliability=0.4, independent=False)]
    rec = IntelligenceRecord(question="Status?", evidence=ev, alternatives=["yes", "no"], prior_belief=0.6)
    d = rec.to_dict()
    rec2 = IntelligenceRecord.from_dict(d)
    assert rec2.question == rec.question
    assert rec2.prior_belief == rec.prior_belief
    assert rec2.record_id == rec.record_id
    assert len(rec2.evidence) == len(rec.evidence)
    assert rec2.evidence[0].claim == "yes"
    # Fingerprint of content should match after roundtrip (timestamps preserved)
    assert rec.analyze()["fingerprint"] == rec2.analyze()["fingerprint"]


def test_wide_ci_suggestion_present():
    # Single weak evidence produces wide CI
    rec = IntelligenceRecord(
        question="Uncertain?",
        evidence=[Evidence(claim="maybe", source="weak", reliability=0.3, independent=True)],
    )
    report = rec.analyze()
    assert any("wide" in s.lower() or "narrow" in s.lower() for s in report["suggestions"])
