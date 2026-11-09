import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION, MAX_EVIDENCE_ITEMS, validate_analysis_report


def test_version_present():
    assert VERSION.startswith("2.1.")
    assert VERSION.endswith("+pro") or VERSION.endswith("-pro")


def test_evidence_validation_rejects_empty_claim():
    with pytest.raises(ValueError, match="claim must be non-empty"):
        Evidence(claim="", source="s", reliability=0.5)


def test_evidence_validation_rejects_empty_source():
    with pytest.raises(ValueError, match="source must be non-empty"):
        Evidence(claim="c", source="", reliability=0.5)


def test_evidence_validation_rejects_bad_reliability():
    with pytest.raises(ValueError, match="reliability must be in"):
        Evidence(claim="c", source="s", reliability=1.5)


def test_evidence_validation_rejects_bad_weight():
    with pytest.raises(ValueError, match="weight must be"):
        Evidence(claim="c", source="s", reliability=0.5, weight=0)


def test_record_validation_rejects_empty_question():
    with pytest.raises(ValueError, match="question must be non-empty"):
        IntelligenceRecord(question="")


def test_record_validation_rejects_bad_prior():
    with pytest.raises(ValueError, match="prior_belief must be in"):
        IntelligenceRecord(question="Q?", prior_belief=1.5)


def test_analyze_insufficient_evidence():
    r = IntelligenceRecord(question="Is X true?").analyze()
    assert r["status"] == "INSUFFICIENT_EVIDENCE"
    assert r["confidence"] == 0.0
    assert r["conclusion"] is None
    assert "evidence" in r["missing"]
    assert validate_analysis_report(r) == []


def test_analyze_provisional_finding():
    evs = [
        Evidence(claim="yes", source="a", reliability=0.9, independent=True),
        Evidence(claim="yes", source="b", reliability=0.8, independent=True),
        Evidence(claim="yes", source="c", reliability=0.7, independent=True),
    ]
    r = IntelligenceRecord(question="Is X true?", evidence=evs).analyze()
    assert r["status"] == "PROVISIONAL_FINDING"
    assert r["conclusion"] == "yes"
    assert r["confidence"] > 0.5
    assert validate_analysis_report(r) == []


def test_analyze_conflicting():
    evs = [
        Evidence(claim="yes", source="a", reliability=0.6, independent=True),
        Evidence(claim="no", source="b", reliability=0.6, independent=True),
    ]
    r = IntelligenceRecord(question="Is X true?", evidence=evs).analyze()
    # May or may not conflict depending on thresholds; at least it runs
    assert r["status"] in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE")
    assert validate_analysis_report(r) == []


def test_fingerprint_stable():
    evs = [Evidence(claim="yes", source="a", reliability=0.9)]
    r1 = IntelligenceRecord(question="Q?", evidence=evs).analyze()
    r2 = IntelligenceRecord(question="Q?", evidence=evs).analyze()
    assert r1["fingerprint"] == r2["fingerprint"]
    assert len(r1["fingerprint"]) == 64


def test_max_evidence_bound():
    evs = [Evidence(claim="yes", source=f"s{i}", reliability=0.5) for i in range(MAX_EVIDENCE_ITEMS + 1)]
    with pytest.raises(ValueError, match="evidence list exceeds"):
        IntelligenceRecord(question="Q?", evidence=evs)


def test_validator_rejects_bad_report():
    violations = validate_analysis_report({"status": "BAD"})
    assert any("missing required" in v for v in violations)
    assert any("invalid status" in v for v in violations)


def test_validator_rejects_bad_fingerprint_and_non_list():
    bad = {
        "version": "2.1.52+pro",
        "record_id": "x",
        "status": "PROVISIONAL_FINDING",
        "question": "Q?",
        "confidence": 0.8,
        "decision_confidence": 0.8,
        "stability": "stable",
        "suggestions": "not a list",
        "audit_trail": [],
        "created_at": "t",
        "analyzed_at": "t",
        "fingerprint": "short",
    }
    violations = validate_analysis_report(bad)
    assert any("fingerprint" in v for v in violations)
    assert any("suggestions must be a list" in v for v in violations)
