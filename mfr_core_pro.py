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

# z-score for approximate 95% credible interval (normal approximation on Beta)
CI_Z_SCORE = 1.96

# Floor for variance in CI calculation to avoid zero/near-zero under extreme Beta parameters
VARIANCE_FLOOR = 1e-8

# Fallback variance when total observations are too few for the Beta variance formula
FALLBACK_VARIANCE = 0.01

# Minimum posterior mean for a second claim to trigger conflict status
CONFLICT_SECOND_THRESHOLD = 0.4

# Confidence threshold above which a provisional finding maps to "stable"
STABLE_CONFIDENCE_THRESHOLD = 0.75

# Clamps for the FathiMind decision contract confidence field
MIN_DECISION_CONFIDENCE = 0.3
MAX_DECISION_CONFIDENCE = 0.98

# Maximum evidence items accepted to bound memory and CPU (reliability / DoS hardening)
MAX_EVIDENCE_ITEMS = 1000

# Maximum length for claim, source, question, and alternative strings (reliability / DoS hardening)
MAX_STRING_LENGTH = 4096


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
        if len(claim) > MAX_STRING_LENGTH:
            raise ValueError(f"claim exceeds maximum length of {MAX_STRING_LENGTH} characters")
        if len(source) > MAX_STRING_LENGTH:
            raise ValueError(f"source exceeds maximum length of {MAX_STRING_LENGTH} characters")
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
        if len(q) > MAX_STRING_LENGTH:
            raise ValueError(f"question exceeds maximum length of {MAX_STRING_LENGTH} characters")
        self.question = q
        if len(self.evidence) > MAX_EVIDENCE_ITEMS:
            raise ValueError(f"evidence list exceeds maximum of {MAX_EVIDENCE_ITEMS} items (got {len(self.evidence)})")
        # Also bound alternatives
        cleaned_alts = []
        for alt in self.alternatives:
            a = (alt or "").strip()
            if a and len(a) <= MAX_STRING_LENGTH:
                cleaned_alts.append(a)
        self.alternatives = cleaned_alts

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
            var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1)) if (alpha + beta) > 1 else FALLBACK_VARIANCE
            std = math.sqrt(max(var, VARIANCE_FLOOR))
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
        elif second and separation < MIN_SEPARATION and second["posterior_mean"] > CONFLICT_SECOND_THRESHOLD:
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
    alternatives: Optional[List[str]] = None,
) -> List[str]:
    suggestions: List[str] = []
    if len(evidence) < 3:
        suggestions.append("Sample size is small. Collect more independent observations.")
    non_indep = [e for e in evidence if not e.independent]
    if non_indep:
        suggestions.append(
            f"Detected {len(non_indep)} non-independent source(s). Prefer independent corroboration."
        )
    if status == "CONFLICTING_EVIDENCE":
        suggestions.append(
            "Conflicting evidence detected. Investigate sources or gather higher-reliability independent data."
        )
    if top and top.get("evidence_count", 0) == 1:
        suggestions.append("Top claim rests on a single source. Seek additional confirmation.")
    if alternatives:
        alts = ", ".join(a.strip() for a in alternatives if a and a.strip())
        if alts:
            suggestions.append(f"Listed alternatives: {alts}. Consider gathering evidence that distinguishes among them.")
    if not suggestions:
        suggestions.append("Evidence is reasonably coherent. Monitor for new observations.")
    return suggestions


def fingerprint(question: str, evidence: List[Evidence], prior: float) -> str:
    """Content-addressable SHA-256 fingerprint. Independent of timestamps and record_id."""
    canonical = {
        "question": question.strip(),
        "prior_belief": round(prior, 6),
        "evidence": sorted(
            [
                {
                    "claim": e.claim,
                    "source": e.source,
                    "reliability": round(e.reliability, 6),
                    "weight": round(e.weight, 6),
                    "independent": e.independent,
                }
                for e in evidence
            ],
            key=lambda x: (x["source"], x["claim"]),
        ),
    }
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(raw).hexdigest()


def to_fathimind_decision(report: Dict[str, Any]) -> Dict[str, Any]:
    """Map analysis report to FathiMind Decision contract (RFC-0001 style)."""
    status_map = {
        "PROVISIONAL_FINDING": "stable" if report.get("confidence", 0) >= STABLE_CONFIDENCE_THRESHOLD else "warning",
        "CONFLICTING_EVIDENCE": "warning",
        "INSUFFICIENT_EVIDENCE": "critical",
    }
    mapped_status = status_map.get(report.get("status", ""), "warning")
    conf = max(MIN_DECISION_CONFIDENCE, min(MAX_DECISION_CONFIDENCE, report.get("confidence", MIN_DECISION_CONFIDENCE)))
    anomalies: List[str] = []
    if report.get("status") == "INSUFFICIENT_EVIDENCE":
        anomalies.append("insufficient evidence")
    if report.get("status") == "CONFLICTING_EVIDENCE":
        anomalies.append("conflicting evidence detected")
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": mapped_status,
        "confidence": conf,
        "evidence": report.get("competing_claims", [])[:2],
        "anomalies": anomalies,
        "input": {"question": report.get("question", "")},
        "_original_status": report.get("status"),
        "fingerprint": report.get("fingerprint"),
    }


def validate_report(report: Dict[str, Any]) -> List[str]:
    """Pure-Python contract checker against analysis.schema.json required fields."""
    violations: List[str] = []
    required = [
        "version", "status", "question", "confidence", "suggestions",
        "audit_trail", "created_at", "analyzed_at", "fingerprint",
    ]
    for key in required:
        if key not in report:
            violations.append(f"missing required field: {key}")
    fp = report.get("fingerprint", "")
    if not isinstance(fp, str) or len(fp) != 64:
        violations.append("fingerprint must be a 64-character hex string")
    status = report.get("status")
    if status not in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE"):
        violations.append(f"invalid status: {status}")
    conf = report.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
        violations.append(f"confidence out of range or not numeric: {conf}")
    return violations



def demo() -> None:
    """Run three illustrative demo cases."""
    print("=== MFR Adaptive Intelligence Core Pro Demo ===")
    cases = [
        IntelligenceRecord(
            question="Is the system secure?",
            evidence=[
                Evidence("secure", "audit-firm", 0.91, independent=True),
                Evidence("secure", "internal-review", 0.84, independent=True),
                Evidence("vulnerable", "researcher", 0.62, independent=True),
            ],
        ),
        IntelligenceRecord(
            question="Is the document authentic?",
            evidence=[
                Evidence("authentic", "source-A", 0.88),
                Evidence("authentic", "source-B", 0.79, independent=False),
            ],
        ),
        IntelligenceRecord(question="Unknown topic with no evidence"),
    ]
    for rec in cases:
        result = rec.analyze()
        print(json.dumps({
            "question": result["question"],
            "status": result["status"],
            "confidence": round(result["confidence"], 3),
            "conclusion": result["conclusion"],
            "fingerprint": result["fingerprint"][:16] + "...",
        }, indent=2, ensure_ascii=False))
        print("---")


def main() -> None:
    parser = argparse.ArgumentParser(description="MFR Adaptive Intelligence Core Pro")
    parser.add_argument("--version", action="version", version=f"MFR Adaptive Intelligence Core Pro {VERSION}")
    parser.add_argument("question", nargs="?", help="Question to analyze")
    parser.add_argument("--evidence", nargs="+", action="append",
                        help="Evidence: claim source reliability [weight] [independent]")
    parser.add_argument("--evidence-file", help="JSON file of evidence list")
    parser.add_argument("--alternatives", nargs="*", default=[], help="Alternative claims")
    parser.add_argument("--prior", type=float, default=None, help="Prior belief [0-1] (overrides evidence-file if present)")
    parser.add_argument("--decision", action="store_true", help="Emit FathiMind Decision contract")
    parser.add_argument("--validate", action="store_true", help="Validate report against contract and exit non-zero on violations")
    parser.add_argument("--demo", action="store_true", help="Run demo cases")
    args = parser.parse_args()

    if args.demo or (not args.question and not args.evidence and not args.evidence_file):
        demo()
        return

    evidence_list: List[Evidence] = []
    file_question = None
    file_prior = None
    file_alternatives = None
    if args.evidence_file:
        try:
            with open(args.evidence_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = None
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "evidence" in data and isinstance(data["evidence"], list):
                items = data["evidence"]
                file_question = data.get("question")
                file_prior = data.get("prior_belief")
                file_alternatives = data.get("alternatives")
            else:
                raise ValueError("evidence file must be a JSON array or an object containing an 'evidence' array")
            for i, item in enumerate(items):
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

    # Prefer explicit CLI, then file values, then error
    effective_question = args.question or file_question
    effective_prior = args.prior if args.prior is not None else (float(file_prior) if file_prior is not None else 0.5)
    effective_alternatives = list(args.alternatives) if args.alternatives else (file_alternatives or [])
    if not effective_question:
        print("question is required when providing evidence", file=sys.stderr)
        sys.exit(2)

    try:
        record = IntelligenceRecord(
            question=effective_question,
            evidence=evidence_list,
            alternatives=effective_alternatives,
            prior_belief=effective_prior,
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
