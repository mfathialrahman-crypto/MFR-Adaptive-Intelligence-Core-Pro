"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION, MAX_EVIDENCE_ITEMS, validate_analysis_report, analyze_json


def test_version_present():
    assert VERSION.startswith("2.1.")
    assert "pro" in VERSION


def test_evidence_validation_rejects_empty_claim():
    with pytest.raises(ValueError, match="claim must be non-empty"):
        Evidence(claim="", source="src", reliability=0.5)
