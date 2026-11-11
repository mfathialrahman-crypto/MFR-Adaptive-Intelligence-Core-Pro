"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION, MAX_EVIDENCE_ITEMS, validate_analysis_report, analyze_json


def test_version_present():
    assert VERSION.startswith("2.1.")
    assert VERSION.endswith("+pro")


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


def test_fingerprint_includes_alternatives():
    """Alternatives affect suggestions; fingerprint must change when they change."""
    ev = [Evidence(claim="yes", source="a", reliability=0.8, independent=True)]
    rec_no = IntelligenceRecord(question="Q?", evidence=ev, alternatives=[])
    rec_with = IntelligenceRecord(question="Q?", evidence=ev, alternatives=["option-a", "option-b"])
    fp_no = rec_no.analyze()["fingerprint"]
    fp_with = rec_with.analyze()["fingerprint"]
    assert fp_no != fp_with
    # Order and whitespace normalized
    rec_reordered = IntelligenceRecord(
        question="Q?", evidence=ev, alternatives=["  option-b  ", "option-a", ""]
    )
    assert rec_reordered.analyze()["fingerprint"] == fp_with


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


def test_alternatives_length_and_count_bounds():
    from mfr_core_pro import MAX_ALTERNATIVES, MAX_ALTERNATIVE_LENGTH
    # Too many alternatives
    with pytest.raises(ValueError, match="alternatives list exceeds maximum"):
        IntelligenceRecord(
            question="Q?",
            alternatives=["a"] * (MAX_ALTERNATIVES + 1),
        )
    # Single alternative too long
    with pytest.raises(ValueError, match="alternative exceeds max length"):
        IntelligenceRecord(
            question="Q?",
            alternatives=["x" * (MAX_ALTERNATIVE_LENGTH + 1)],
        )
    # Empty / whitespace alternatives are stripped
    rec = IntelligenceRecord(
        question="Q?",
        alternatives=["  ", "", "valid", "  another  "],
    )
    assert rec.alternatives == ["valid", "another"]
    # Max length accepted
    rec2 = IntelligenceRecord(
        question="Q?",
        alternatives=["y" * MAX_ALTERNATIVE_LENGTH],
    )
    assert len(rec2.alternatives[0]) == MAX_ALTERNATIVE_LENGTH


def test_serialization_round_trip_preserves_fingerprint():
    """JSON round-trip of inputs must preserve the analysis fingerprint."""
    original = IntelligenceRecord(
        question="Round-trip?",
        evidence=[
            Evidence(claim="yes", source="a", reliability=0.9, independent=True, weight=1.2),
            Evidence(claim="no", source="b", reliability=0.4, independent=False),
        ],
        alternatives=["yes", "no", "maybe"],
        prior_belief=0.6,
    )
    fp_before = original.analyze()["fingerprint"]
    restored = IntelligenceRecord.from_json(original.to_json())
    fp_after = restored.analyze()["fingerprint"]
    assert fp_before == fp_after
    assert restored.question == original.question
    assert len(restored.evidence) == len(original.evidence)
    assert restored.prior_belief == original.prior_belief
    # Evidence fields match
    assert restored.evidence[0].claim == original.evidence[0].claim
    assert restored.evidence[0].weight == original.evidence[0].weight


def test_version_aligned_with_pyproject():
    """Ensure version.py VERSION matches pyproject.toml (CI gate)."""
    import re
    from version import VERSION
    with open("pyproject.toml") as f:
        content = f.read()
    m = re.search(r'version\s*=\s*"([^"]+)"', content)
    assert m is not None, "version not found in pyproject.toml"
    assert VERSION == m.group(1), f"Mismatch: version.py={VERSION} vs pyproject={m.group(1)}"


def test_every_analyze_path_passes_validator():
    """Every analyze() result must satisfy the public contract validator."""
    cases = [
        IntelligenceRecord(question="No evidence?"),
        IntelligenceRecord(
            question="Single?",
            evidence=[Evidence(claim="yes", source="a", reliability=0.9)],
        ),
        IntelligenceRecord(
            question="Conflict?",
            evidence=[
                Evidence(claim="a", source="s1", reliability=0.7),
                Evidence(claim="b", source="s2", reliability=0.72),
            ],
        ),
        IntelligenceRecord(
            question="Strong?",
            evidence=[
                Evidence(claim="yes", source="a", reliability=0.95, independent=True),
                Evidence(claim="yes", source="b", reliability=0.93, independent=True),
                Evidence(claim="yes", source="c", reliability=0.91, independent=True),
            ],
            alternatives=["yes", "no"],
        ),
    ]
    for rec in cases:
        report = rec.analyze()
        violations = validate_analysis_report(report)
        assert violations == [], f"violations for {rec.question}: {violations}"


def test_validator_rejects_bad_report():
    bad = {"status": "UNKNOWN", "confidence": 1.5}
    violations = validate_analysis_report(bad)
    assert len(violations) > 0
    assert any("missing required" in v for v in violations)
    assert any("invalid status" in v for v in violations)


def test_validator_rejects_non_dict():
    violations = validate_analysis_report(None)
    assert violations == ["report must be a dict"]
    violations2 = validate_analysis_report("not a dict")
    assert "report must be a dict" in violations2


def test_validator_rejects_bad_fingerprint_and_non_list():
    bad = {
        "version": "2.1.52-pro",
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
    assert report["status"] in ("INSUFFICIENT_EVIDENCE", "PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE")
    assert report["confidence"] >= 0.0
