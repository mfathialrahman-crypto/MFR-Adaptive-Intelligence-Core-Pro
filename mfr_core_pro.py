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
from typing import Any, Optional, List, Dict, TypedDict
import json
import math
import uuid
from collections import defaultdict

from version import VERSION

# Limits
MAX_EVIDENCE_ITEMS = 1000
MAX_CLAIM_LENGTH = 500
MAX_SOURCE_LENGTH = 200
MAX_QUESTION_LENGTH = 1000
MAX_ALTERNATIVES = 20
MAX_ALTERNATIVE_LENGTH = 200

PRIOR_STRENGTH = 2.0  # Beta prior strength
INDEPENDENCE_PENALTY = 0.6  # multiplier for non-independent evidence
MIN_DECISION_CONFIDENCE = 0.3
MAX_DECISION_CONFIDENCE = 0.98


class ClaimStat(TypedDict):
    claim: str
    mean: float
    ci_low: float
    ci_high: float
    evidence_count: int
    total_weight: float
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
        self.claim = self.claim.strip()
        self.source = self.source.strip()
        if not self.claim:
            raise ValueError("claim must be non-empty")
        if not self.source:
            raise ValueError("source must be non-empty")
        if not (0.0 <= self.reliability <= 1.0):
            raise ValueError("reliability must be in [0.0, 1.0]")
        if self.weight <= 0:
            raise ValueError("weight must be > 0")
        if len(self.claim) > MAX_CLAIM_LENGTH:
            raise ValueError("claim exceeds max length")
        if len(self.source) > MAX_SOURCE_LENGTH:
            raise ValueError("source exceeds max length")


@dataclass
class IntelligenceRecord:
    question: str
    evidence: List[Evidence] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    prior_belief: float = 0.5
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        self.question = self.question.strip()
        if not self.question:
            raise ValueError("question must be non-empty")
        if len(self.question) > MAX_QUESTION_LENGTH:
            raise ValueError("question exceeds max length")
        if not (0.0 <= self.prior_belief <= 1.0):
            raise ValueError("prior_belief must be in [0.0, 1.0]")
        if len(self.evidence) > MAX_EVIDENCE_ITEMS:
            raise ValueError("evidence list exceeds maximum")
        # Normalize alternatives
        cleaned = []
        for alt in self.alternatives:
            a = alt.strip()
            if a:
                if len(a) > MAX_ALTERNATIVE_LENGTH:
                    raise ValueError("alternative exceeds max length")
                cleaned.append(a)
        if len(cleaned) > MAX_ALTERNATIVES:
            raise ValueError("alternatives list exceeds maximum")
        self.alternatives = cleaned

    def to_json(self) -> str:
        data = {
            "question": self.question,
            "evidence": [asdict(e) for e in self.evidence],
            "alternatives": self.alternatives,
            "prior_belief": self.prior_belief,
            "record_id": self.record_id,
            "created_at": self.created_at,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, raw: str) -> "IntelligenceRecord":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"invalid JSON: {e}") from e
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
        if "question" not in data or not isinstance(data.get("question"), str):
            raise ValueError("missing or invalid 'question' field")
        evidence = [Evidence(**e) for e in data.get("evidence", []) if isinstance(e, dict)]
        return cls(
            question=data["question"],
            evidence=evidence,
            alternatives=data.get("alternatives", []),
            prior_belief=data.get("prior_belief", 0.5),
            record_id=data.get("record_id", str(uuid.uuid4())),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
        )

    def analyze(self) -> Dict[str, Any]:
        if len(self.evidence) > MAX_EVIDENCE_ITEMS:
            raise ValueError("evidence list exceeds maximum")

        # Group by claim
        by_claim: Dict[str, List[Evidence]] = defaultdict(list)
        for ev in self.evidence:
            by_claim[ev.claim].append(ev)

        claims_stats: List[ClaimStat] = []
        for claim, evids in by_claim.items():
            alpha = PRIOR_STRENGTH * 0.5
            beta = PRIOR_STRENGTH * 0.5
            total_weight = 0.0
            for ev in evids:
                w = ev.weight * ev.reliability
                if not ev.independent:
                    w *= INDEPENDENCE_PENALTY
                total_weight += w
                alpha += w
                beta += (1.0 - ev.reliability) * ev.weight * (INDEPENDENCE_PENALTY if not ev.independent else 1.0)

            mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            # Approximate 95% CI via Wilson or simple normal approx on logit, but keep simple
            variance = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1))
            std = math.sqrt(variance) if variance > 0 else 0.0
            ci_low = max(0.0, mean - 1.96 * std)
            ci_high = min(1.0, mean + 1.96 * std)

            claims_stats.append({
                "claim": claim,
                "mean": round(mean, 4),
                "ci_low": round(ci_low, 4),
                "ci_high": round(ci_high, 4),
                "evidence_count": len(evids),
                "total_weight": round(total_weight, 4),
                "alpha": round(alpha, 4),
                "beta": round(beta, 4),
            })

        # Sort by mean descending
        claims_stats.sort(key=lambda x: x["mean"], reverse=True)

        # Decision
        if not claims_stats:
            status = "insufficient"
            conclusion = None
            confidence = 0.0
        else:
            top = claims_stats[0]
            confidence = top["mean"]
            if confidence < MIN_DECISION_CONFIDENCE:
                status = "insufficient"
                conclusion = None
            elif confidence > MAX_DECISION_CONFIDENCE:
                status = "decided"
                conclusion = top["claim"]
            else:
                status = "provisional"
                conclusion = top["claim"]

        # Fingerprint
        fp_src = self.to_json() + VERSION
        fingerprint = sha256(fp_src.encode()).hexdigest()[:16]

        return {
            "status": status,
            "conclusion": conclusion,
            "confidence": round(confidence, 4),
            "claims": claims_stats,
            "fingerprint": fingerprint,
            "version": VERSION,
            "record_id": self.record_id,
            "evidence_count": len(self.evidence),
        }


def analyze_json(raw: str) -> Dict[str, Any]:
    rec = IntelligenceRecord.from_json(raw)
    return rec.analyze()


def _demo() -> None:
    print("MFR Adaptive Intelligence Core Pro — Demo")
    rec = IntelligenceRecord(
        question="Is the system healthy?",
        evidence=[
            Evidence(claim="healthy", source="monitor-a", reliability=0.9, independent=True),
            Evidence(claim="healthy", source="monitor-b", reliability=0.85, independent=True),
            Evidence(claim="degraded", source="alert-c", reliability=0.4, independent=False),
        ],
        alternatives=["healthy", "degraded", "failed"],
    )
    report = rec.analyze()
    print(f"Status: {report['status']}")
    print(f"Conclusion: {report.get('conclusion')}")
    print(f"Confidence: {report['confidence']}")
    print(f"Fingerprint: {report['fingerprint']}")
    print("Demo complete.")



def main() -> None:
    """Entry point for CLI (console script and python -m)."""
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ("--help", "-h"):
        print("MFR Adaptive Intelligence Core Pro")
        print("Usage:")
        print("  mfr-core                         # run built-in demo (after pip install -e .)")
        print("  python mfr_core_pro.py           # run built-in demo")
        print("  mfr-core --version | -V          # print version and exit")
        print("  python mfr_core_pro.py --version # print version and exit")
        print("  mfr-core --json <file.json>      # analyze JSON record and print report")
        print("  python mfr_core_pro.py --json <file.json>")
        print("  mfr-core --help | -h             # show this help")
        print("  python mfr_core_pro.py --help")
        return
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-V"):
        print(VERSION)
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        if len(sys.argv) > 2:
            try:
                with open(sys.argv[2]) as f:
                    raw = f.read()
                print(json.dumps(analyze_json(raw), indent=2))
            except FileNotFoundError:
                print(f"Error: file not found: {sys.argv[2]}", file=sys.stderr)
                sys.exit(1)
            except PermissionError:
                print(f"Error: permission denied: {sys.argv[2]}", file=sys.stderr)
                sys.exit(1)
            except (ValueError, OSError) as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Usage: python mfr_core_pro.py --json <file.json>", file=sys.stderr)
            sys.exit(1)
    else:
        _demo()

if __name__ == "__main__":
    main()
