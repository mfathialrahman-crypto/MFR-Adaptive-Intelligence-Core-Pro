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

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Optional, TypedDict
import json
import math
import uuid


VERSION = "2.1.15-pro"

# Posterior mean difference below this threshold indicates insufficient separation
# between top claims and is treated as conflicting evidence (see analyze()).
CONFLICT_THRESHOLD = 0.18


@dataclass
class Evidence:
    claim: str
    source: str
    reliability: float  # 0.0 – 1.0
    independent: bool = True
    weight: float = 1.0  # extra multiplier (e.g. sample size / recency)
    notes: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.claim, str) or not self.claim.strip():
            raise ValueError("claim must be a non-empty string")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError(f"reliability must be in [0,1], got {self.reliability}")
        if not isinstance(self.weight, (int, float)) or self.weight <= 0:
            raise ValueError("weight must be a positive number")


class ClaimResult(TypedDict):
    claim: str
    posterior_mean: float
    ci_95: list[float]
    support_mass: float
    evidence_count: int
    independent_count: int
    effective_score: float


@dataclass
class IntelligenceRecord:
    question: str
    evidence: list[Evidence] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    prior_belief: float = 0.5  # neutral prior
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def add_evidence(self, *items: Evidence) -> None:
        self.evidence.extend(items)

    def analyze(self, alpha_prior: float | None = None, beta_prior: float | None = None) -> dict[str, Any]:
        """
        Bayesian-inspired analysis.
        Uses a simple Beta-Binomial style update on support vs opposition,
        with independence penalty and source deduplication.
        Prior is derived from self.prior_belief unless overridden.
        """
        if not 0.0 <= self.prior_belief <= 1.0:
            raise ValueError(f"prior_belief must be in [0,1], got {self.prior_belief}")

        # Derive weak Beta prior from prior_belief (concentration ~2)
        if alpha_prior is None or beta_prior is None:
            concentration = 2.0
            alpha_prior = max(self.prior_belief * concentration, 1e-6)
            beta_prior = max((1.0 - self.prior_belief) * concentration, 1e-6)

        audit: list[dict[str, Any]] = []
        audit.append({
            "step": "start",
            "question": self.question,
            "n_evidence": len(self.evidence),
            "prior_belief": self.prior_belief,
            "alpha_prior": round(alpha_prior, 4),
            "beta_prior": round(beta_prior, 4),
        })

        if not self.evidence:
            return self._insufficient("No evidence provided", audit)

        # 1. Deduplicate by source while respecting independence flag
        unique_sources: dict[str, Evidence] = {}
        for ev in self.evidence:
            key = ev.source
            if key in unique_sources:
                # Keep the higher reliability / weight combination
                existing = unique_sources[key]
                if (ev.reliability * ev.weight) > (existing.reliability * existing.weight):
                    unique_sources[key] = ev
                    audit.append({"step": "dedup", "source": key, "action": "replaced_with_stronger"})
            else:
                unique_sources[key] = ev

        evidence = list(unique_sources.values())
        audit.append({"step": "after_dedup", "unique_sources": len(evidence)})

        if not evidence:
            return self._insufficient("No independent evidence after deduplication", audit)

        # 2. Group by claim and compute effective support (capped to prevent invalid posteriors)
        claims: dict[str, list[tuple[float, bool]]] = {}  # claim -> list of (capped_effective, independent)
        for ev in evidence:
            # Independence penalty: non-independent evidence contributes less
            ind_factor = 1.0 if ev.independent else 0.55
            # Cap weight influence so each evidence contributes at most 1.0 effective unit
            # This keeps Beta parameters valid (alpha, beta > 0) even with high weights
            raw_effective = ev.reliability * min(ev.weight, 3.0) * ind_factor
            effective = min(1.0, raw_effective)
            claims.setdefault(ev.claim, []).append((effective, ev.independent))

        # 3. Bayesian-style scoring (Beta prior + soft observations)
        results: list[ClaimResult] = []
        for claim, scores in claims.items():
            support_mass = sum(s for s, _ in scores)
            n_obs = len(scores)
            n_independent = sum(1 for _, ind in scores if ind)

            # Pseudo-count update: each evidence is a soft observation in [0, 1]
            # opposition mass = n_obs - support_mass  (always >= 0)
            alpha = alpha_prior + support_mass
            beta = beta_prior + (n_obs - support_mass)
            # Guard against numerical issues
            alpha = max(alpha, 1e-6)
            beta = max(beta, 1e-6)
            mean = alpha / (alpha + beta)
            # Approximate 95% credible interval via normal approximation
            variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
            std = math.sqrt(max(variance, 1e-12))
            ci_low = max(0.0, mean - 1.96 * std)
            ci_high = min(1.0, mean + 1.96 * std)

            results.append({
                "claim": claim,
                "posterior_mean": round(mean, 4),
                "ci_95": [round(ci_low, 4), round(ci_high, 4)],
                "support_mass": round(support_mass, 4),
                "evidence_count": n_obs,
                "independent_count": n_independent,
                "effective_score": round(support_mass * (1 + 0.15 * n_independent), 4),
            })

        # Rank by effective score then by posterior mean
        results.sort(key=lambda x: (x["effective_score"], x["posterior_mean"]), reverse=True)

        contradiction = False
        if len(results) > 1:
            mean0 = float(results[0]["posterior_mean"])
            mean1 = float(results[1]["posterior_mean"])
            contradiction = (mean0 - mean1) < CONFLICT_THRESHOLD

        status = "CONFLICTING_EVIDENCE" if contradiction else "PROVISIONAL_FINDING"
        top = results[0]

        # 4. Generate improvement suggestions
        suggestions = self._generate_suggestions(results, evidence, contradiction)

        # 5. Build final report
        report = {
            "version": VERSION,
            "record_id": self.record_id,
            "status": status,
            "question": self.question,
            "confidence": round(top["posterior_mean"], 4),
            "conclusion": top["claim"] if not contradiction else None,
            "top_claim": top,
            "competing_claims": results,
            "alternatives": self.alternatives,
            "suggestions": suggestions,
            "audit_trail": audit,
            "created_at": self.created_at,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

        report["fingerprint"] = fingerprint(report)
        return report

    def _insufficient(self, reason: str, audit: list[dict[str, Any]]) -> dict[str, Any]:
        audit.append({"step": "insufficient", "reason": reason})
        report: dict[str, Any] = {
            "version": VERSION,
            "record_id": self.record_id,
            "status": "INSUFFICIENT_EVIDENCE",
            "question": self.question,
            "confidence": 0.0,
            "conclusion": None,
            "top_claim": None,
            "competing_claims": [],
            "alternatives": self.alternatives,
            "missing": [reason, "Independent, high-reliability sources"],
            "suggestions": [
                "Collect at least two independent sources with reliability ≥ 0.7",
                "Prefer primary sources over secondary summaries",
            ],
            "audit_trail": audit,
            "created_at": self.created_at,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
        report["fingerprint"] = fingerprint(report)
        return report

    def _generate_suggestions(
        self, results: list[ClaimResult], evidence: list[Evidence], contradiction: bool
    ) -> list[str]:
        suggestions = []
        if contradiction:
            suggestions.append(
                "Evidence is conflicting. Seek a higher-reliability independent source that can adjudicate."
            )
            suggestions.append(
                "Consider whether the claims are actually mutually exclusive or can be reconciled under a more nuanced hypothesis."
            )

        low_ind = sum(1 for e in evidence if not e.independent)
        if low_ind > 0:
            suggestions.append(
                f"{low_ind} piece(s) of evidence marked non-independent; their weight was penalized. Prefer truly independent sources."
            )

        if len(evidence) < 3:
            suggestions.append("Sample size is small. Additional independent evidence will tighten the credible interval.")

        top_mean = results[0]["posterior_mean"] if results else 0
        if top_mean < 0.75 and not contradiction:
            suggestions.append(
                "Current confidence is moderate. Look for primary documents or direct measurements to raise reliability."
            )

        if not suggestions:
            suggestions.append("Evidence base is solid. Consider stress-testing the top claim against strong counter-evidence.")

        return suggestions


def fingerprint(record: dict[str, Any]) -> str:
    """
    Content-addressable fingerprint.
    Stable for identical decision content (question, evidence, alternatives, prior, conclusion, confidence, status).
    Excludes instance metadata and volatile fields.
    """
    volatile = {
        "analyzed_at", "fingerprint", "audit_trail",
        "record_id", "created_at", "version"
    }
    clean = {k: v for k, v in record.items() if k not in volatile}
    # Canonicalize evidence-like lists if present for stability
    payload = json.dumps(clean, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return sha256(payload).hexdigest()


def to_fathimind_decision(report: dict[str, Any]) -> dict[str, Any]:
    """Map an analysis report to a FathiMind Decision schema-compatible object (RFC-0001).

    Status mapping (aligned with shared contract):
    - PROVISIONAL_FINDING with confidence >= 0.75 → stable
    - PROVISIONAL_FINDING with confidence < 0.75 → warning
    - CONFLICTING_EVIDENCE → warning
    - INSUFFICIENT_EVIDENCE → critical

    Confidence is clamped to the contract bounds [0.3, 0.98].
    Additive fields are allowed; this produces a minimal valid decision.
    """
    if not isinstance(report, dict):
        raise TypeError("report must be a dict")

    status_raw = report.get("status", "INSUFFICIENT_EVIDENCE")
    conf = float(report.get("confidence", 0.0))
    # Clamp to schema bounds
    conf_clamped = max(0.3, min(0.98, conf))

    if status_raw == "PROVISIONAL_FINDING":
        decision_status = "stable" if conf >= 0.75 else "warning"
    elif status_raw == "CONFLICTING_EVIDENCE":
        decision_status = "warning"
    else:
        decision_status = "critical"

    # Build evidence list as strings for simplicity and schema compatibility
    evidence_items: list[str] = []
    top = report.get("top_claim") or {}
    if top:
        evidence_items.append(
            f"top_claim={top.get('claim')} posterior={top.get('posterior_mean')} "
            f"ci={top.get('ci_95')} n={top.get('evidence_count')}"
        )
    for s in report.get("suggestions", [])[:5]:
        evidence_items.append(f"suggestion: {s}")
    if not evidence_items:
        evidence_items.append("no supporting evidence")

    anomalies = []
    if status_raw == "CONFLICTING_EVIDENCE":
        anomalies.append("conflicting evidence detected")
    if status_raw == "INSUFFICIENT_EVIDENCE":
        anomalies.append("insufficient evidence")
    if conf < 0.6:
        anomalies.append("low confidence")

    decision = {
        "timestamp": report.get("analyzed_at") or datetime.now(timezone.utc).isoformat(),
        "status": decision_status,
        "confidence": round(conf_clamped, 4),
        "input": {
            "question": report.get("question", ""),
            "record_id": report.get("record_id"),
            "version": report.get("version"),
            "n_competing": len(report.get("competing_claims") or []),
        },
        "evidence": evidence_items,
        "anomalies": anomalies,
        "signature": report.get("fingerprint"),
        # Additive: full original report reference for replay
        "_source": "mfr_core_pro",
        "_original_status": status_raw,
    }
    return decision


def demo() -> None:
    print("=" * 60)
    print("MFR Adaptive Intelligence Core Pro – Demo")
    print("=" * 60)

    # Case 1: Strong agreement
    rec1 = IntelligenceRecord(
        question="هل هذا المستند صحيح؟",
        evidence=[
            Evidence("المستند صحيح", "source-A", 0.92, independent=True, weight=1.2),
            Evidence("المستند صحيح", "source-B", 0.88, independent=True),
            Evidence("المستند صحيح", "source-C", 0.75, independent=False, notes="secondary summary"),
        ],
        alternatives=["المستند مزيف", "المستند جزئياً صحيح"],
    )
    result1 = rec1.analyze()
    print("\n[Case 1 – Strong agreement]")
    print(json.dumps(result1, ensure_ascii=False, indent=2))

    # Case 2: Conflict
    rec2 = IntelligenceRecord(
        question="هل النظام آمن؟",
        evidence=[
            Evidence("النظام آمن", "audit-firm-X", 0.91, independent=True),
            Evidence("النظام غير آمن", "researcher-Y", 0.87, independent=True),
            Evidence("النظام آمن", "internal-report", 0.70, independent=False),
        ],
    )
    result2 = rec2.analyze()
    print("\n[Case 2 – Conflicting evidence]")
    print(json.dumps(result2, ensure_ascii=False, indent=2))

    # Case 3: Insufficient
    rec3 = IntelligenceRecord(question="هل يوجد دليل؟")
    result3 = rec3.analyze()
    print("\n[Case 3 – Insufficient]")
    print(json.dumps(result3, ensure_ascii=False, indent=2))



def main() -> None:
    """Minimal CLI for quick analysis."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="MFR Adaptive Intelligence Core Pro – evidence analysis"
    )
    parser.add_argument("question", nargs="?", default=None, help="The question to analyze (optional; omit to run demo)")
    parser.add_argument(
        "--evidence",
        action="append",
        nargs="+",
        metavar="ITEM",
        help="Evidence: CLAIM SOURCE RELIABILITY [WEIGHT] [INDEPENDENT] (repeatable). "
             "RELIABILITY 0-1, WEIGHT >0 (default 1.0), INDEPENDENT true/false (default true).",
    )
    parser.add_argument("--prior", type=float, default=0.5, help="Prior belief 0-1 (default 0.5)")
    parser.add_argument(
        "--alternatives",
        action="append",
        metavar="ALT",
        help="Alternative claims to consider (repeatable). Stored for context; analysis focuses on evidence.",
    )
    parser.add_argument("--demo", action="store_true", help="Run the built-in demo instead")
    parser.add_argument(
        "--decision",
        action="store_true",
        help="Emit FathiMind Decision contract (RFC-0001) instead of raw analysis report",
    )
    parser.add_argument(
        "--evidence-file",
        type=str,
        metavar="PATH",
        help="JSON file containing a list of evidence objects "
             "{claim, source, reliability, optional weight, optional independent}",
    )
    args = parser.parse_args()

    if args.demo or (not args.evidence and not args.evidence_file):
        demo()
        return
    if not args.question:
        parser.error("question is required when providing evidence")

    evidence = []
    if args.evidence_file:
        import json as _json
        from pathlib import Path as _Path
        try:
            raw = _json.loads(_Path(args.evidence_file).read_text(encoding="utf-8"))
        except (OSError, _json.JSONDecodeError) as exc:
            print(f"Failed to load evidence file: {exc}", file=sys.stderr)
            sys.exit(2)
        if not isinstance(raw, list):
            print("Evidence file must contain a JSON list", file=sys.stderr)
            sys.exit(2)
        for item in raw:
            if not isinstance(item, dict):
                print("Each evidence item must be an object", file=sys.stderr)
                sys.exit(2)
            try:
                evidence.append(
                    Evidence(
                        claim=item["claim"],
                        source=item["source"],
                        reliability=float(item["reliability"]),
                        independent=bool(item.get("independent", True)),
                        weight=float(item.get("weight", 1.0)),
                    )
                )
            except (KeyError, ValueError, TypeError) as exc:
                print(f"Invalid evidence item: {exc}", file=sys.stderr)
                sys.exit(2)
    for items in (args.evidence or []):
        if len(items) < 3:
            print("Each --evidence needs at least CLAIM SOURCE RELIABILITY", file=sys.stderr)
            sys.exit(2)
        claim, source, rel_str = items[0], items[1], items[2]
        weight = 1.0
        independent = True
        if len(items) >= 4:
            try:
                weight = float(items[3])
            except ValueError:
                print(f"Invalid weight: {items[3]}", file=sys.stderr)
                sys.exit(2)
        if len(items) >= 5:
            ind_str = items[4].lower()
            if ind_str in ("true", "1", "yes", "y"):
                independent = True
            elif ind_str in ("false", "0", "no", "n"):
                independent = False
            else:
                print(f"Invalid independent flag: {items[4]} (use true/false)", file=sys.stderr)
                sys.exit(2)
        try:
            rel = float(rel_str)
        except ValueError:
            print(f"Invalid reliability: {rel_str}", file=sys.stderr)
            sys.exit(2)
        evidence.append(Evidence(claim, source, rel, independent=independent, weight=weight))

    rec = IntelligenceRecord(
        question=args.question,
        evidence=evidence,
        prior_belief=args.prior,
        alternatives=args.alternatives or [],
    )
    result = rec.analyze()
    if args.decision:
        decision = to_fathimind_decision(result)
        print(json.dumps(decision, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
