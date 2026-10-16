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

    def test_dedup_keeps_stronger(self):
        rec = IntelligenceRecord(
            question="q",
            evidence=[
                Evidence("yes", "same", 0.5),
                Evidence("yes", "same", 0.9),
            ],
        )
        result = rec.analyze()
        self.assertEqual(result["top_claim"]["evidence_count"], 1)

    def test_independence_penalty(self):
        rec_ind = IntelligenceRecord(
            question="q",
            evidence=[Evidence("yes", "A", 0.9, independent=True)],
        )
        rec_dep = IntelligenceRecord(
            question="q",
            evidence=[Evidence("yes", "A", 0.9, independent=False)],
        )
        self.assertGreater(rec_ind.analyze()["confidence"], rec_dep.analyze()["confidence"])

    def test_high_weight_does_not_break_posterior(self):
        rec = IntelligenceRecord(
            question="q",
            evidence=[Evidence("yes", "A", 0.9, weight=100.0)],
        )
        result = rec.analyze()
        self.assertLessEqual(result["confidence"], 1.0)
        self.assertGreaterEqual(result["confidence"], 0.0)

    def test_fingerprint_stable(self):
        rec = IntelligenceRecord(
            question="q",
            evidence=[Evidence("yes", "A", 0.8)],
        )
        r1 = rec.analyze()
        r2 = rec.analyze()
        self.assertEqual(r1["fingerprint"], r2["fingerprint"])

    def test_fingerprint_content_addressable_across_instances(self):
        e = Evidence("yes", "A", 0.8)
        r1 = IntelligenceRecord(question="q", evidence=[e]).analyze()
        r2 = IntelligenceRecord(question="q", evidence=[e]).analyze()
        self.assertEqual(r1["fingerprint"], r2["fingerprint"])

    def test_empty_claim_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("", "src", 0.5)

    def test_empty_source_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("claim", "", 0.5)

    def test_zero_or_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("c", "s", 0.5, weight=0)
        with self.assertRaises(ValueError):
            Evidence("c", "s", 0.5, weight=-1)

    def test_prior_belief_affects_posterior(self):
        rec_neutral = IntelligenceRecord(
            question="q", prior_belief=0.5,
            evidence=[Evidence("yes", "A", 0.6)],
        )
        rec_high = IntelligenceRecord(
            question="q", prior_belief=0.9,
            evidence=[Evidence("yes", "A", 0.6)],
        )
        r_neutral = rec_neutral.analyze()
        r_high = rec_high.analyze()
        self.assertGreater(r_high["confidence"], r_neutral["confidence"])
        self.assertEqual(r_neutral["status"], "PROVISIONAL_FINDING")

    def test_invalid_prior_rejected(self):
        rec = IntelligenceRecord(question="q", prior_belief=1.5)
        with self.assertRaises(ValueError):
            rec.analyze()


class TestVersion(unittest.TestCase):
    def test_version_single_source(self):
        from version import VERSION as v_from_file
        from mfr_core_pro import VERSION as v_from_module
        self.assertEqual(v_from_file, v_from_module)
        self.assertEqual(v_from_module, "2.1.8-pro")
        self.assertTrue(v_from_module.endswith("-pro"))


if __name__ == "__main__":
    unittest.main()
