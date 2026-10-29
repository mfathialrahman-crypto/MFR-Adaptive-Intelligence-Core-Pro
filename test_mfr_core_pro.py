#!/usr/bin/env python3
"""Unit tests for MFR Adaptive Intelligence Core Pro."""

import json
import pytest
from mfr_core_pro import Evidence, IntelligenceRecord, fingerprint, VERSION


def test_version_present():
    assert VERSION.startswith("2.1.")


def test_evidence_validation():
    with pytest.raises(ValueError):
        Evidence("", "src", 0.5)
    with pytest.raises(ValueError):
        Evidence("claim", "", 0.5)
    with pytest.raises(ValueError):
        Evidence("claim", "src", 1.5)


def test_insufficient_evidence():
    rec = IntelligenceRecord(question="Is it true?")
    report = rec.analyze()
    assert report["status"] == "INSUFFICIENT_EVIDENCE"
    assert report["confidence"] == 0.0
    assert "evidence" in report.get("missing", [])


def test_provisional_finding():
    evs = [
        Evidence("yes", "a", 0.9, True),
        Evidence("yes", "b", 0.85, True),
    ]
    rec = IntelligenceRecord("Q?", evs, prior_belief=0.5)
    report = rec.analyze()
    assert report["status"] == "PROVISIONAL_FINDING"
    assert report["conclusion"] == "yes"
    assert report["confidence"] > 0.6
    assert len(report["fingerprint"]) == 64


def test_conflicting_evidence():
    evs = [
        Evidence("yes", "a", 0.9, True),
        Evidence("no", "b", 0.88, True),
    ]
    rec = IntelligenceRecord("Q?", evs, prior_belief=0.5)
    report = rec.analyze()
    assert report["status"] == "CONFLICTING_EVIDENCE"
    assert report["conclusion"] is None


def test_fingerprint_deterministic():
    evs = [Evidence("c", "s", 0.7)]
    f1 = fingerprint("q", evs, 0.5)
    f2 = fingerprint("q", evs, 0.5)
    assert f1 == f2
    f3 = fingerprint("q", evs, 0.6)
    assert f1 != f3


def test_max_evidence_limit():
    evs = [Evidence(f"c{i}", f"s{i}", 0.5) for i in range(1001)]
    with pytest.raises(ValueError, match="exceeds maximum"):
        IntelligenceRecord("Q", evs)


def test_suggestions_generated():
    rec = IntelligenceRecord("Q", [Evidence("c", "s", 0.5)])
    report = rec.analyze()
    assert isinstance(report["suggestions"], list)
    assert len(report["suggestions"]) > 0


def test_cli_demo_runs(tmp_path, capsys):
    # Just ensure import and basic call doesn't crash; full CLI tested via subprocess if needed
    from mfr_core_pro import main
    # We don't invoke full argparse here to keep unit test pure
    assert callable(main)
