#!/usr/bin/env python3
"""Unit tests for MFR Adaptive Intelligence Core Pro"""

import unittest
from mfr_core_pro import IntelligenceRecord, Evidence, fingerprint, VERSION


class TestEvidence(unittest.TestCase):
    def test_valid_reliability(self):
        e = Evidence("claim", "src", 0.8)
        self.assertEqual(e.reliability, 0.8)

    def test_invalid_reliability(self):
        with self.assertRaises(ValueError):
            Evidence("claim", "src", 1.5)
        with self.assertRaises(ValueError):
            Evidence("claim", "src", -0.1)


class TestAnalyze(unittest.TestCase):
    def test_insufficient(self):
        rec = IntelligenceRecord(question="test")
        result = rec.analyze()
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["confidence"], 0.0)
        self.assertIsNone(result["conclusion"])

    def test_strong_agreement(self):
        rec = IntelligenceRecord(
            question="Is it true?",
            evidence=[
                Evidence("yes", "A", 0.9, independent=True),
                Evidence("yes", "B", 0.85, independent=True),
            ],
        )
        result = rec.analyze()
        self.assertEqual(result["status"], "PROVISIONAL_FINDING")
        self.assertEqual(result["conclusion"], "yes")
        self.assertGreater(result["confidence"], 0.5)
        self.assertIn("fingerprint", result)
        self.assertEqual(result["version"], VERSION)

    def test_conflict(self):
        rec = IntelligenceRecord(
            question="Safe?",
            evidence=[
                Evidence("safe", "X", 0.9, independent=True),
                Evidence("unsafe", "Y", 0.88, independent=True),
            ],
        )
        result = rec.analyze()
        self.assertEqual(result["status"], "CONFLICTING_EVIDENCE")
        self.assertIsNone(result["conclusion"])
        self.assertGreaterEqual(len(result["competing_claims"]), 2)

    def test_independence_penalty(self):
        rec = IntelligenceRecord(
            question="test",
            evidence=[
                Evidence("claim", "A", 0.9, independent=True),
                Evidence("claim", "B", 0.9, independent=False),
            ],
        )
        result = rec.analyze()
        self.assertEqual(result["status"], "PROVISIONAL_FINDING")
        self.assertIn("suggestions", result)

    def test_high_weight_does_not_break_posterior(self):
        """High weights must not produce probabilities > 1 or negative parameters."""
        rec = IntelligenceRecord(
            question="high weight test",
            evidence=[
                Evidence("yes", "A", 0.95, independent=True, weight=10.0),
                Evidence("yes", "B", 0.90, independent=True, weight=5.0),
            ],
        )
        result = rec.analyze()
        self.assertEqual(result["status"], "PROVISIONAL_FINDING")
        conf = result["confidence"]
        self.assertGreaterEqual(conf, 0.0)
        self.assertLessEqual(conf, 1.0)
        top = result["top_claim"]
        self.assertGreaterEqual(top["posterior_mean"], 0.0)
        self.assertLessEqual(top["posterior_mean"], 1.0)
        self.assertGreaterEqual(top["ci_95"][0], 0.0)
        self.assertLessEqual(top["ci_95"][1], 1.0)

    def test_fingerprint_stable(self):
        rec = IntelligenceRecord(
            question="q",
            evidence=[Evidence("c", "s", 0.8)],
        )
        r1 = rec.analyze()
        self.assertTrue(len(r1["fingerprint"]) == 64)


if __name__ == "__main__":
    unittest.main()
