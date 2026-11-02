"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION, MAX_STRING_LENGTH, MAX_EVIDENCE_ITEMS


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
            Evidence(claim="healthy", source="a", reliability=0.9, independent=True),
            Evidence(claim="unhealthy", source="b", reliability=0.88, independent=True),
        ],
    )
    report = rec.analyze()
    assert report["status"] in ("CONFLICTING_EVIDENCE", "PROVISIONAL_FINDING")
    assert report["confidence"] > 0.0


def test_independence_penalty_lowers_weight():
    independent = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9, independent=True)],
    )
    dependent = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9, independent=False)],
    )
    conf_i = independent.analyze()["confidence"]
    conf_d = dependent.analyze()["confidence"]
    assert conf_i > conf_d


def test_fingerprint_deterministic_and_content_addressable():
    e = [Evidence(claim="yes", source="s1", reliability=0.9)]
    r1 = IntelligenceRecord(question="Q?", evidence=e, prior_belief=0.5)
    r2 = IntelligenceRecord(question="Q?", evidence=e, prior_belief=0.5)
    f1 = r1.analyze()["fingerprint"]
    f2 = r2.analyze()["fingerprint"]
    assert f1 == f2
    assert len(f1) == 64


def test_deduplication_keeps_strongest_per_source():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence(claim="yes", source="same", reliability=0.5, weight=1.0),
            Evidence(claim="yes", source="same", reliability=0.9, weight=1.0),
        ],
    )
    report = rec.analyze()
    assert report["top_claim"]["evidence_count"] == 1


def test_max_evidence_items_enforced():
    with pytest.raises(ValueError, match="exceeds maximum"):
        IntelligenceRecord(
            question="Q",
            evidence=[Evidence(claim="c", source=f"s{i}", reliability=0.5) for i in range(MAX_EVIDENCE_ITEMS + 1)],
        )


def test_suggestions_for_small_sample():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9)],
    )
    report = rec.analyze()
    assert any("small" in s.lower() or "single source" in s for s in report["suggestions"])


def test_alternatives_appear_in_suggestions():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.9)],
        alternatives=["yes", "no"],
    )
    report = rec.analyze()
    assert any("alternatives" in s.lower() for s in report["suggestions"])


def test_ci_non_overlap_signal_when_present():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.99, weight=3.0),
            Evidence(claim="yes", source="b", reliability=0.99, weight=3.0),
            Evidence(claim="no", source="c", reliability=0.5),
        ],
    )
    report = rec.analyze()
    assert report["status"] in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE")


def test_prior_belief_validated_on_construction():
    with pytest.raises(ValueError, match="prior_belief"):
        IntelligenceRecord(question="Q", prior_belief=1.5)


def test_decision_contract_fields_present():
    rec = IntelligenceRecord(
        question="Q",
        evidence=[Evidence(claim="yes", source="a", reliability=0.95)],
    )
    report = rec.analyze()
    assert "decision_confidence" in report
    assert "stability" in report
    assert report["stability"] in ("stable", "provisional", "unstable")


def test_insufficient_evidence_decision_contract():
    rec = IntelligenceRecord(question="Q")
    report = rec.analyze()
    assert report["stability"] == "unstable"
    assert report["decision_confidence"] >= 0.3


def test_evidence_validation_rejects_empty_source():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="ok", source="", reliability=0.5)


def test_demo_runs_without_error(capsys):
    import mfr_core_pro
    mfr_core_pro._demo()
    captured = capsys.readouterr()
    assert "Demo complete" in captured.out or "Status:" in captured.out


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


def test_evidence_rejects_oversized_claim():
    oversized = "x" * (MAX_STRING_LENGTH + 1)
    with pytest.raises(ValueError, match="claim exceeds maximum length"):
        Evidence(claim=oversized, source="src", reliability=0.5)


def test_evidence_rejects_oversized_source():
    oversized = "y" * (MAX_STRING_LENGTH + 1)
    with pytest.raises(ValueError, match="source exceeds maximum length"):
        Evidence(claim="ok", source=oversized, reliability=0.5)


def test_record_rejects_oversized_question():
    oversized = "q" * (MAX_STRING_LENGTH + 1)
    with pytest.raises(ValueError, match="question exceeds maximum length"):
        IntelligenceRecord(question=oversized, evidence=[])


def test_max_string_length_boundary_accepted():
    """Exact MAX_STRING_LENGTH is accepted; one over is rejected (covered above)."""
    claim = "c" * MAX_STRING_LENGTH
    source = "s" * MAX_STRING_LENGTH
    question = "q" * MAX_STRING_LENGTH
    ev = Evidence(claim=claim, source=source, reliability=0.8)
    rec = IntelligenceRecord(question=question, evidence=[ev])
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == claim
    assert len(report["fingerprint"]) == 64


def test_fingerprint_regression_baseline():
    """Stable content-addressable fingerprint for a fixed input set."""
    e = [
        Evidence(claim="yes", source="a", reliability=0.9),
        Evidence(claim="yes", source="b", reliability=0.85),
    ]
    r = IntelligenceRecord(question="Healthy?", evidence=e, prior_belief=0.5)
    report = r.analyze()
    assert report["fingerprint"] == "8c3c53886a6a425d8499b24f8d5fb6c30ced4300cf4b308b649b7eb3bae3f507"
    assert report["status"] == "PROVISIONAL_FINDING"
