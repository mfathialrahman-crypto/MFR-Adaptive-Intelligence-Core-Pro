#!/usr/bin/env python3
"""Unit tests for MFR Adaptive Intelligence Core Pro"""

import unittest
import json
import tempfile
import os
import subprocess
import sys
from mfr_core_pro import IntelligenceRecord, Evidence, fingerprint, VERSION, to_fathimind_decision


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

    def test_empty_claim_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("", "src", 0.8)
        with self.assertRaises(ValueError):
            Evidence("   ", "src", 0.8)

    def test_empty_source_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("claim", "", 0.8)
        with self.assertRaises(ValueError):
            Evidence("claim", "   ", 0.8)

    def test_zero_or_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            Evidence("claim", "src", 0.8, weight=0)
        with self.assertRaises(ValueError):
            Evidence("claim", "src", 0.8, weight=-1)

    def test_fingerprint_content_addressable_across_instances(self):
        """Same content must produce the same fingerprint regardless of instance metadata."""
        ev = [Evidence("yes", "A", 0.9, independent=True), Evidence("yes", "B", 0.85)]
        rec1 = IntelligenceRecord(question="Is it true?", evidence=ev)
        rec2 = IntelligenceRecord(question="Is it true?", evidence=ev)
        r1 = rec1.analyze()
        r2 = rec2.analyze()
        self.assertEqual(r1["fingerprint"], r2["fingerprint"])
        self.assertEqual(len(r1["fingerprint"]), 64)
        rec3 = IntelligenceRecord(question="Different?", evidence=ev)
        r3 = rec3.analyze()
        self.assertNotEqual(r1["fingerprint"], r3["fingerprint"])

    def test_dedup_keeps_stronger(self):
        rec = IntelligenceRecord(
            question="q",
            evidence=[
                Evidence("claim", "same", 0.6, weight=1.0),
                Evidence("claim", "same", 0.9, weight=1.0),
            ],
        )
        result = rec.analyze()
        self.assertEqual(result["status"], "PROVISIONAL_FINDING")
        self.assertEqual(result["top_claim"]["evidence_count"], 1)

    def test_prior_belief_affects_posterior(self):
        """prior_belief should influence the posterior when evidence is limited."""
        ev = [Evidence("yes", "A", 0.6)]
        rec_neutral = IntelligenceRecord(question="q", evidence=ev, prior_belief=0.5)
        rec_high = IntelligenceRecord(question="q", evidence=ev, prior_belief=0.8)
        r_neutral = rec_neutral.analyze()
        r_high = rec_high.analyze()
        self.assertGreater(r_high["confidence"], r_neutral["confidence"])
        self.assertEqual(r_neutral["status"], "PROVISIONAL_FINDING")

    def test_invalid_prior_rejected(self):
        rec = IntelligenceRecord(question="q", prior_belief=1.5)
        with self.assertRaises(ValueError):
            rec.analyze()



    def test_claim_result_includes_alpha_beta(self):
        """Analysis must expose posterior parameters for full auditability."""
        rec = IntelligenceRecord(
            question="audit",
            evidence=[Evidence("yes", "A", 0.9, independent=True)],
        )
        result = rec.analyze()
        top = result["top_claim"]
        self.assertIn("alpha", top)
        self.assertIn("beta", top)
        self.assertGreater(top["alpha"], 0)
        self.assertGreater(top["beta"], 0)
        # Mean must match alpha / (alpha + beta) within rounding
        computed = top["alpha"] / (top["alpha"] + top["beta"])
        self.assertAlmostEqual(computed, top["posterior_mean"], places=3)

class TestDecisionMapping(unittest.TestCase):
    def test_to_fathimind_decision_strong(self):
        rec = IntelligenceRecord(
            question="Is it true?",
            evidence=[
                Evidence("yes", "A", 0.95, independent=True),
                Evidence("yes", "B", 0.90, independent=True),
            ],
        )
        result = rec.analyze()
        decision = to_fathimind_decision(result)
        self.assertIn("timestamp", decision)
        self.assertIn(decision["status"], ("stable", "warning"))
        self.assertGreaterEqual(decision["confidence"], 0.3)
        self.assertLessEqual(decision["confidence"], 0.98)
        self.assertIsInstance(decision["evidence"], list)
        self.assertIsInstance(decision["anomalies"], list)
        self.assertIn("input", decision)
        self.assertEqual(decision["input"]["question"], "Is it true?")
        self.assertEqual(decision["_original_status"], result["status"])

    def test_to_fathimind_decision_insufficient(self):
        rec = IntelligenceRecord(question="unknown")
        result = rec.analyze()
        decision = to_fathimind_decision(result)
        self.assertEqual(decision["status"], "critical")
        self.assertIn("insufficient evidence", decision["anomalies"])
        self.assertGreaterEqual(decision["confidence"], 0.3)

    def test_to_fathimind_decision_conflict(self):
        rec = IntelligenceRecord(
            question="Safe?",
            evidence=[
                Evidence("safe", "X", 0.9, independent=True),
                Evidence("unsafe", "Y", 0.88, independent=True),
            ],
        )
        result = rec.analyze()
        decision = to_fathimind_decision(result)
        self.assertEqual(decision["status"], "warning")
        self.assertIn("conflicting evidence detected", decision["anomalies"])


class TestCLI(unittest.TestCase):
    def test_evidence_file_cli(self):
        evidence_data = [
            {"claim": "yes", "source": "A", "reliability": 0.9, "independent": True},
            {"claim": "yes", "source": "B", "reliability": 0.8}
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(evidence_data, f)
            path = f.name
        try:
            result = subprocess.run(
                [sys.executable, "mfr_core_pro.py", "Is it true?", "--evidence-file", path],
                capture_output=True, text=True, check=True, cwd=os.path.dirname(__file__) or "."
            )
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "PROVISIONAL_FINDING")
            self.assertEqual(data["conclusion"], "yes")
            self.assertIn("fingerprint", data)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
