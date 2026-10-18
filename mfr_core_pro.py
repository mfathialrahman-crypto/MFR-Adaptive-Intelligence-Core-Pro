#!/usr/bin/env python3
"""MFR Adaptive Intelligence Core Pro — public transparent layer of FathiMind.

Evidence → Bayesian-inspired belief updating → Verification → Self-improvement suggestions.
Zero dependencies. Content-addressable decision traces.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, TypedDict

VERSION = "2.1.14-pro"

# Named constants (from changelog)
CONFLICT_THRESHOLD = 0.18
MAX_WEIGHT = 5.0  # soft cap so extreme weights do not break Beta parameters
INDEPENDENCE_PENALTY = 0.55  # multiplier when independent=False
PRIOR_CONCENTRATION = 2.0  # weak Beta prior strength


class ClaimResult(TypedDict):
    claim: str
    posterior_mean: float
    ci_95: List[float]
    evidence_count: int
    effective_score: float
    alpha: float
    beta: float


@dataclass
class Evidence:
    claim: str
    source: str
    reliability: float
    independent: bool = True
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.claim, str) or not self.claim.strip():
            raise ValueError("claim must be a non-empty string")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError("reliability must be in [0, 1]")
        if self.weight <= 0:
            raise ValueError("weight must be positive")
        self.claim = self.claim.strip()
        self.source = self.source.strip()


@dataclass
class IntelligenceRecord:
    question: str
    evidence: List[Evidence] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    prior_belief: float = 0.5
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def analyze(self) -> Dict[str, Any]:
        if not (0.0 <= self.prior_belief <= 1.0):
            raise ValueError("prior_belief must be in [0, 1]")

        analyzed_at = datetime.now(timezone.utc).isoformat()

        if not self.evidence:
            report = self._empty_report(analyzed_at)
            report["fingerprint"] = fingerprint(report)
            return report

        # Deduplicate by (claim, source): keep highest reliability
        deduped: Dict[tuple, Evidence] = {}
        for e in self.evidence:
            key = (e.claim, e.source)
            if key not in deduped or e.reliability > deduped[key].reliability:
                deduped[key] = e
        items = list(deduped.values())

        # Group by claim
        by_claim: Dict[str, List[Evidence]] = {}
        for e in items:
            by_claim.setdefault(e.claim, []).append(e)

        # Beta prior
        prior_alpha = self.prior_belief * PRIOR_CONCENTRATION
        prior_beta = (1.0 - self.prior_belief) * PRIOR_CONCENTRATION

        claim_results: List[ClaimResult] = []
        for claim, evs in by_claim.items():
            alpha = prior_alpha
            beta = prior_beta
            for e in evs:
                w = min(e.weight, MAX_WEIGHT)
                if not e.independent:
                    w *= INDEPENDENCE_PENALTY
                # Soft observation: reliability contributes to alpha, (1-rel) to beta
                alpha += e.reliability * w
                beta += (1.0 - e.reliability) * w
            total = alpha + beta
            mean = alpha / total if total > 0 else 0.5
            # Approximate 95% CI via normal approx on Beta (or simple variance)
            var = (alpha * beta) / ((total ** 2) * (total + 1)) if total > 1 else 0.01
            std = var ** 0.5
            ci_low = max(0.0, mean - 1.96 * std)
            ci_high = min(1.0, mean + 1.96 * std)
            effective = mean * (len(evs) ** 0.5)  # simple effective score
            claim_results.append(
                ClaimResult(
                    claim=claim,
                    posterior_mean=mean,
                    ci_95=[ci_low, ci_high],
                    evidence_count=len(evs),
                    effective_score=effective,
                    alpha=alpha,
                    beta=beta,
                )
            )

        claim_results.sort(key=lambda c: c["effective_score"], reverse=True)
        top = claim_results[0] if claim_results else None

        status = "INSUFFICIENT_EVIDENCE"
        conclusion = None
        confidence = 0.0
        competing: List[Dict[str, Any]] = []

        if top and top["evidence_count"] >= 1:
            confidence = top["posterior_mean"]
            # Conflict: second claim close in score
            if len(claim_results) >= 2:
                second = claim_results[1]
                if abs(top["effective_score"] - second["effective_score"]) < CONFLICT_THRESHOLD * top["effective_score"] or abs(top["posterior_mean"] - second["posterior_mean"]) < CONFLICT_THRESHOLD:
                    status = "CONFLICTING_EVIDENCE"
                    conclusion = None
                    competing = [dict(c) for c in claim_results[:3]]
                else:
                    status = "PROVISIONAL_FINDING"
                    conclusion = top["claim"]
            else:
                status = "PROVISIONAL_FINDING"
                conclusion = top["claim"]

        suggestions = self._suggestions(status, claim_results, items)

        report: Dict[str, Any] = {
            "version": VERSION,
            "record_id": self.record_id,
            "status": status,
            "question": self.question,
            "confidence": confidence,
            "conclusion": conclusion,
            "top_claim": dict(top) if top else None,
            "competing_claims": competing,
            "alternatives": self.alternatives,
            "suggestions": suggestions,
            "audit_trail": [
                {"step": "prior", "alpha": prior_alpha, "beta": prior_beta, "belief": self.prior_belief},
                {"step": "deduped_evidence_count", "count": len(items)},
                {"step": "claims_analyzed", "count": len(claim_results)},
            ],
            "created_at": self.created_at,
            "analyzed_at": analyzed_at,
            "missing": [],
        }
        report["fingerprint"] = fingerprint(report)
        return report

    def _empty_report(self, analyzed_at: str) -> Dict[str, Any]:
        return {
            "version": VERSION,
            "record_id": self.record_id,
            "status": "INSUFFICIENT_EVIDENCE",
            "question": self.question,
            "confidence": 0.0,
            "conclusion": None,
            "top_claim": None,
            "competing_claims": [],
            "alternatives": self.alternatives,
            "suggestions": ["Collect at least one piece of evidence before forming a finding."],
            "audit_trail": [{"step": "no_evidence"}],
            "created_at": self.created_at,
            "analyzed_at": analyzed_at,
            "missing": ["evidence"],
        }

    def _suggestions(self, status: str, claims: List[ClaimResult], items: List[Evidence]) -> List[str]:
        s = []
        if status == "INSUFFICIENT_EVIDENCE":
            s.append("Add independent evidence from distinct sources.")
        elif status == "CONFLICTING_EVIDENCE":
            s.append("Resolve conflict by seeking higher-reliability independent sources.")
            s.append("Consider whether sources share a common bias.")
        else:
            if any(not e.independent for e in items):
                s.append("Some evidence is non-independent; seek additional independent corroboration.")
            if claims and claims[0]["evidence_count"] < 3:
                s.append("Increase evidence count for stronger credible interval.")
            s.append("Record the decision and schedule a review against new evidence.")
        return s


def fingerprint(report: Dict[str, Any]) -> str:
    """Content-addressable SHA-256 of the stable decision content.

    Excludes volatile fields (record_id, created_at, analyzed_at, fingerprint, version).
    """
    stable = {
        "question": report.get("question"),
        "status": report.get("status"),
        "confidence": round(float(report.get("confidence", 0)), 6),
        "conclusion": report.get("conclusion"),
        "top_claim": report.get("top_claim"),
        "competing_claims": report.get("competing_claims"),
        "alternatives": report.get("alternatives"),
        "suggestions": report.get("suggestions"),
        "prior_used": report.get("audit_trail"),
    }
    # Remove nested volatile if any
    blob = json.dumps(stable, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def to_fathimind_decision(report: Dict[str, Any]) -> Dict[str, Any]:
    """Map an analysis report to a FathiMind Decision contract (RFC-0001)."""
    status_map = {
        "PROVISIONAL_FINDING": "stable" if report.get("confidence", 0) >= 0.75 else "warning",
        "CONFLICTING_EVIDENCE": "warning",
        "INSUFFICIENT_EVIDENCE": "critical",
    }
    fm_status = status_map.get(report.get("status", ""), "warning")
    conf = float(report.get("confidence", 0.0))
    conf = max(0.3, min(0.98, conf))

    anomalies = []
    if report.get("status") == "INSUFFICIENT_EVIDENCE":
        anomalies.append("insufficient evidence")
    elif report.get("status") == "CONFLICTING_EVIDENCE":
        anomalies.append("conflicting evidence detected")

    evidence_list = []
    top = report.get("top_claim") or {}
    if top:
        evidence_list.append({
            "claim": top.get("claim"),
            "posterior_mean": top.get("posterior_mean"),
            "count": top.get("evidence_count"),
        })

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": fm_status,
        "confidence": conf,
        "evidence": evidence_list,
        "anomalies": anomalies,
        "input": {"question": report.get("question")},
        "_original_status": report.get("status"),
        "conclusion": report.get("conclusion"),
        "fingerprint": report.get("fingerprint"),
    }


def _run_demo() -> None:
    print("=== MFR Adaptive Intelligence Core Pro Demo ===")
    demos = [
        IntelligenceRecord(
            question="Is the system secure?",
            evidence=[
                Evidence("secure", "audit-firm", 0.91, independent=True),
                Evidence("secure", "internal-review", 0.84, independent=True),
                Evidence("vulnerable", "researcher", 0.72, independent=False, weight=0.8),
            ],
        ),
        IntelligenceRecord(
            question="Should we ship?",
            evidence=[
                Evidence("yes", "A", 0.95),
                Evidence("yes", "B", 0.90),
            ],
        ),
        IntelligenceRecord(question="Unknown topic"),
    ]
    for rec in demos:
        result = rec.analyze()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("---")


def main() -> None:
    parser = argparse.ArgumentParser(description="MFR Adaptive Intelligence Core Pro")
    parser.add_argument("question", nargs="?", help="Question to analyze")
    parser.add_argument("--evidence", action="append", nargs="+", help="CLAIM SOURCE RELIABILITY [WEIGHT] [true|false]")
    parser.add_argument("--evidence-file", help="JSON file with evidence array")
    parser.add_argument("--alternatives", action="append", help="Alternative hypotheses")
    parser.add_argument("--prior", type=float, default=0.5, help="Prior belief [0,1]")
    parser.add_argument("--decision", action="store_true", help="Emit FathiMind Decision contract")
    parser.add_argument("--demo", action="store_true", help="Run built-in demos")
    args = parser.parse_args()

    if args.demo or (not args.question and not args.evidence and not args.evidence_file):
        _run_demo()
        return

    if not args.question:
        print("Error: question is required when supplying evidence", file=sys.stderr)
        sys.exit(2)

    evidence_list: List[Evidence] = []
    if args.evidence_file:
        with open(args.evidence_file, encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            evidence_list.append(
                Evidence(
                    claim=item["claim"],
                    source=item["source"],
                    reliability=float(item["reliability"]),
                    independent=item.get("independent", True),
                    weight=float(item.get("weight", 1.0)),
                )
            )
    if args.evidence:
        for parts in args.evidence:
            if len(parts) < 3:
                print(f"Malformed evidence: {parts}", file=sys.stderr)
                sys.exit(2)
            claim, source, rel_s = parts[0], parts[1], parts[2]
            weight = float(parts[3]) if len(parts) > 3 else 1.0
            indep = True
            if len(parts) > 4:
                indep = parts[4].lower() in ("true", "yes", "1", "y")
            evidence_list.append(Evidence(claim, source, float(rel_s), independent=indep, weight=weight))

    rec = IntelligenceRecord(
        question=args.question,
        evidence=evidence_list,
        alternatives=args.alternatives or [],
        prior_belief=args.prior,
    )
    result = rec.analyze()
    if args.decision:
        out = to_fathimind_decision(result)
    else:
        out = result
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
