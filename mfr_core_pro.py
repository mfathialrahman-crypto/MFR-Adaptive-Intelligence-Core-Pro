#!/usr/bin/env python3
"""
MFR Adaptive Intelligence Core Pro
Evidence → Bayesian Reasoning → Verification → Self-Improvement

Superior implementation over the original:
- Bayesian-style belief updating with Beta prior
- Proper independence penalty
- Full audit trail
- Conflict resolution with explanatory hypotheses
- Confidence intervals (approximate)
- Actionable improvement suggestions
- Deterministic fingerprinting + versioning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Optional, List, Dict
import json
import math
import uuid
import argparse
import sys
from collections import defaultdict

from version import VERSION

# Posterior mean difference below this threshold indicates insufficient separation
MIN_SEPARATION = 0.05

# Soft observation weight is capped to keep Beta parameters valid
MAX_EFFECTIVE_WEIGHT = 5.0

# Single source of truth for non-independent evidence down-weighting
INDEPENDENCE_FACTOR = 0.6

# Soft opposition weight for residual evidence from other claims
OPPOSITION_FACTOR = 0.5

# Fixed prior strength (pseudo-observations) for Beta prior stability
PRIOR_STRENGTH = 2.0

# Z-score for approximate 95% credible interval (normal approx)
CI_Z_SCORE = 1.96


@dataclass
class Evidence:
    claim: str
    source: str
    reliability: float
    independent: bool = True
    weight: float = 1.0

    def __post_init__(self) -> None:
        claim = (self.claim or "").strip()
        source = (self.source or "").strip()
        if not claim:
            raise ValueError("claim must be non-empty")
        if not source:
            raise ValueError("source must be non-empty")
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError(f"reliability must be in [0, 1], got {self.reliability}")
        if self.weight <= 0:
            raise ValueError(f"weight must be > 0, got {self.weight}")
        self.claim = claim
        self.source = source


@dataclass
class IntelligenceRecord:
    question: str
    evidence: List[Evidence] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    prior_belief: float = 0.5
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        q = (self.question or "").strip()
        if not q:
            raise ValueError("question must be non-empty")
        self.question = q

    def analyze(self) -> Dict[str, Any]:
        if not (0.0 <= self.prior_belief <= 1.0):
            raise ValueError(f"prior_belief must be in [0, 1], got {self.prior_belief}")

        analyzed_at = datetime.now(timezone.utc).isoformat()
        audit: List[str] = []

        if not self.evidence:
            report = {
                "version": VERSION,
                "record_id": self.record_id,
                "status": "INSUFFICIENT_EVIDENCE",
                "question": self.question,
                "confidence": 0.0,
                "conclusion": None,
                "top_claim": None,
                "competing_claims": [],
                "alternatives": self.alternatives,
                "suggestions": ["No evidence provided. Add independent observations."],
                "audit_trail": ["No evidence available."],
                "created_at": self.created_at,
                "analyzed_at": analyzed_at,
                "fingerprint": fingerprint(self.question, [], self.prior_belief),
                "missing": ["evidence"],
            }
            return report

        # Deduplicate by source: keep the strongest evidence per source
        by_source: Dict[str, Evidence] = {}
        for ev in self.evidence:
            key = ev.source
            if key not in by_source or _strength(ev) > _strength(by_source[key]):
                by_source[key] = ev
        deduped = list(by_source.values())
        audit.append(f"Deduplicated {len(self.evidence)} → {len(deduped)} unique sources.")

        # Group supporting evidence by claim
        by_claim: Dict[str, List[Evidence]] = defaultdict(list)
        for ev in deduped:
            by_claim[ev.claim].append(ev)

        # Beta prior from prior_belief
        # Prior strength fixed at PRIOR_STRENGTH pseudo-observations for stability
        prior_strength = PRIOR_STRENGTH
        prior_alpha = self.prior_belief * prior_strength
        prior_beta = (1.0 - self.prior_belief) * prior_strength

        # Precompute effective weight per claim for O(n) opposition calculation
        claim_effective: Dict[str, float] = {}
        for claim, evs in by_claim.items():
            total = 0.0
            for ev in evs:
                indep_factor = 1.0 if ev.independent else INDEPENDENCE_FACTOR
                total += min(ev.reliability * ev.weight * indep_factor, MAX_EFFECTIVE_WEIGHT)
            claim_effective[claim] = total
        total_effective = sum(claim_effective.values())

        claim_stats: List[Dict[str, Any]] = []
        for claim, evs in by_claim.items():
            alpha = prior_alpha
            beta = prior_beta
            total_weight = 0.0
            indep_count = 0
            for ev in evs:
                indep_factor = 1.0 if ev.independent else INDEPENDENCE_FACTOR  # independence penalty
                effective = min(ev.reliability * ev.weight * indep_factor, MAX_EFFECTIVE_WEIGHT)
                # Soft positive observation
                alpha += effective
                total_weight += effective
                if ev.independent:
                    indep_count += 1
            # Opposing evidence increases beta slightly via residual
            opposing = total_effective - claim_effective.get(claim, 0.0)
            beta += opposing * OPPOSITION_FACTOR  # soft opposition

            mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            # Approximate 95% CI using normal approximation on Beta
            var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1)) if (alpha + beta) > 1 else 0.01
            std = math.sqrt(max(var, 1e-8))
            ci_low = max(0.0, mean - CI_Z_SCORE * std)
            ci_high = min(1.0, mean + CI_Z_SCORE * std)

            claim_stats.append({
                "claim": claim,
                "posterior_mean": mean,
                "ci_95": [ci_low, ci_high],
                "evidence_count": len(evs),
                "effective_weight": total_weight,
                "independent_count": indep_count,
                "alpha": alpha,
                "beta": beta,
            })

        claim_stats.sort(key=lambda c: c["posterior_mean"], reverse=True)
        top = claim_stats[0] if claim_stats else None
        second = claim_stats[1] if len(claim_stats) > 1 else None

        separation = (top["posterior_mean"] - second["posterior_mean"]) if top and second else 1.0

        if top is None or top["evidence_count"] == 0:
            status = "INSUFFICIENT_EVIDENCE"
            conclusion = None
            confidence = 0.0
        elif second and separation < MIN_SEPARATION and second["posterior_mean"] > 0.4:
            status = "CONFLICTING_EVIDENCE"
            conclusion = None
            confidence = top["posterior_mean"]
        else:
            status = "PROVISIONAL_FINDING"
            conclusion = top["claim"]
            confidence = top["posterior_mean"]

        suggestions = _generate_suggestions(deduped, status, top, second, self.alternatives)
        audit.append(f"Status={status}, confidence={confidence:.3f}, separation={separation:.3f}")

        report = {
            "version": VERSION,
            "record_id": self.record_id,
            "status": status,
            "question": self.question,
            "confidence": max(0.0, min(1.0, confidence)),
            "conclusion": conclusion,
            "top_claim": top,
            "competing_claims": claim_stats[:3],
            "alternatives": self.alternatives,
            "suggestions": suggestions,
            "audit_trail": audit,
            "created_at": self.created_at,
            "analyzed_at": analyzed_at,
            "fingerprint": fingerprint(self.question, deduped, self.prior_belief),
        }
        return report


def _strength(ev: Evidence) -> float:
    return ev.reliability * ev.weight * (1.0 if ev.independent else INDEPENDENCE_FACTOR)


def _generate_suggestions(
    evidence: List[Evidence],
    status: str,
    top: Optional[Dict[str, Any]],
    second: Optional[Dict[str, Any]],
    alternatives: List[str],
) -> List[str]:
    suggestions = []
    if status == "INSUFFICIENT_EVIDENCE":
        suggestions.append("Add independent observations.")
        return suggestions
    if status == "CONFLICTING_EVIDENCE":
        suggestions.append("Evidence is conflicting. Gather more independent data or refine claims.")
    if top and top.get("independent_count", 0) == 0:
        suggestions.append("Top claim relies on non-independent evidence. Seek independent sources.")
    if len(evidence) < 3:
        suggestions.append("Small number of sources. Additional independent evidence would increase confidence.")
    if alternatives:
        suggestions.append("Also consider: " + ", ".join(alternatives))
    if not suggestions:
        suggestions.append("Evidence is coherent. Continue monitoring for contrary observations.")
    return suggestions


def fingerprint(question: str, evidence: List[Evidence], prior: float) -> str:
    items = sorted(
        [(ev.claim, ev.source, round(ev.reliability, 6), ev.independent, round(ev.weight, 6)) for ev in evidence]
    )
    blob = json.dumps({"question": question, "evidence": items, "prior": round(prior, 6)}, sort_keys=True)
    return sha256(blob.encode("utf-8")).hexdigest()[:16]


def to_fathimind_decision(report: Dict[str, Any]) -> Dict[str, Any]:
    status = report.get("status", "UNKNOWN")
    conf = report.get("confidence", 0.0)
    if status == "INSUFFICIENT_EVIDENCE":
        health = "critical"
        anomaly = True
    elif status == "CONFLICTING_EVIDENCE":
        health = "warning"
        anomaly = True
    elif conf < 0.5:
        health = "warning"
        anomaly = False
    else:
        health = "stable"
        anomaly = False
    return {
        "schema": "fathimind.decision.v1",
        "id": report.get("record_id"),
        "question": report.get("question"),
        "status": status,
        "health": health,
        "confidence": conf,
        "conclusion": report.get("conclusion"),
        "anomaly": anomaly,
        "fingerprint": report.get("fingerprint"),
        "audit_trail": report.get("audit_trail", []),
        "generated_at": report.get("analyzed_at"),
    }


def validate_report(report: Dict[str, Any]) -> List[str]:
    violations = []
    if "status" not in report:
        violations.append("missing status")
    conf = report.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
        violations.append("confidence out of range")
    fp = report.get("fingerprint", "")
    if not isinstance(fp, str) or len(fp) < 8:
        violations.append("fingerprint too short")
    return violations


def demo() -> None:
    print("=== MFR Adaptive Intelligence Core Pro Demo ===")
    cases = [
        IntelligenceRecord(
            "Is the system secure?",
            [
                Evidence("secure", "audit-firm", 0.91, independent=True),
                Evidence("secure", "internal-review", 0.84, independent=True),
                Evidence("vulnerable", "researcher", 0.62, independent=True),
            ],
        ),
        IntelligenceRecord(
            "Is the artifact authentic?",
            [
                Evidence("authentic", "source-A", 0.88),
                Evidence("authentic", "source-B", 0.79, independent=False),
            ],
        ),
        IntelligenceRecord("Empty evidence case"),
    ]
    for r in cases:
        print(json.dumps(r.analyze(), indent=2, ensure_ascii=False))
        print("-" * 40)


def main() -> None:
    parser = argparse.ArgumentParser(description="MFR Adaptive Intelligence Core Pro")
    parser.add_argument("--version", action="version", version=f"MFR Adaptive Intelligence Core Pro {VERSION}")
    parser.add_argument("question", nargs="?", help="Question to analyze")
    parser.add_argument("--evidence", nargs="+", action="append",
                        help="Evidence: claim source reliability [weight] [independent]")
    parser.add_argument("--evidence-file", help="JSON file of evidence list")
    parser.add_argument("--alternatives", nargs="*", default=[], help="Alternative claims")
    parser.add_argument("--prior", type=float, default=0.5, help="Prior belief [0-1]")
    parser.add_argument("--decision", action="store_true", help="Emit FathiMind Decision contract")
    parser.add_argument("--validate", action="store_true", help="Validate report against contract and exit non-zero on violations")
    parser.add_argument("--demo", action="store_true", help="Run demo cases")
    args = parser.parse_args()

    if args.demo or (not args.question and not args.evidence and not args.evidence_file):
        demo()
        return

    if not args.question:
        print("question is required when providing evidence", file=sys.stderr)
        sys.exit(2)

    evidence_list: List[Evidence] = []
    if args.evidence_file:
        try:
            with open(args.evidence_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("evidence file must contain a JSON array")
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"evidence item {i} must be an object")
                if "claim" not in item or "source" not in item or "reliability" not in item:
                    raise ValueError(f"evidence item {i} missing required keys (claim, source, reliability)")
                evidence_list.append(Evidence(
                    claim=str(item["claim"]),
                    source=str(item["source"]),
                    reliability=float(item["reliability"]),
                    independent=bool(item.get("independent", True)),
                    weight=float(item.get("weight", 1.0)),
                ))
        except (OSError, json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
            print(f"Failed to load evidence file: {exc}", file=sys.stderr)
            sys.exit(2)
    if args.evidence:
        for parts in args.evidence:
            if len(parts) < 3:
                print("each --evidence needs at least claim source reliability", file=sys.stderr)
                sys.exit(2)
            claim, source, rel_s = parts[0], parts[1], parts[2]
            try:
                weight = float(parts[3]) if len(parts) > 3 else 1.0
                indep = True
                if len(parts) > 4:
                    indep = parts[4].lower() in ("true", "yes", "1", "y")
                evidence_list.append(Evidence(claim, source, float(rel_s), independent=indep, weight=weight))
            except ValueError as exc:
                print(f"Invalid evidence: {exc}", file=sys.stderr)
                sys.exit(2)

    try:
        record = IntelligenceRecord(
            question=args.question,
            evidence=evidence_list,
            alternatives=args.alternatives,
            prior_belief=args.prior,
        )
        result = record.analyze()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    if args.decision:
        output = to_fathimind_decision(result)
    else:
        output = result

    if args.validate:
        violations = validate_report(result)
        if violations:
            print("Validation failed:", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
            sys.exit(1)
        print("Validation passed.", file=sys.stderr)

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
