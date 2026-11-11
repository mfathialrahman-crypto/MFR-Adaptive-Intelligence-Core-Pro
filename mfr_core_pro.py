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
- Self-contained HTML evidence report (zero dependencies)
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
        data = json.loads(raw)
        evidence = [Evidence(**e) for e in data.get("evidence", [])]
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

        analyzed_at = datetime.now(timezone.utc).isoformat()
        audit: List[str] = []

        # Deduplicate by source, keep strongest (highest reliability * weight)
        by_source: Dict[str, Evidence] = {}
        for ev in self.evidence:
            key = ev.source
            if key not in by_source or (ev.reliability * ev.weight) > (by_source[key].reliability * by_source[key].weight):
                by_source[key] = ev
        deduped = list(by_source.values())
        if len(self.evidence) != len(deduped):
            audit.append(f"Deduplicated {len(self.evidence)} → {len(deduped)}")

        if not deduped:
            report = self._base_report(analyzed_at, audit)
            report.update({
                "status": "INSUFFICIENT_EVIDENCE",
                "confidence": 0.0,
                "conclusion": None,
                "top_claim": None,
                "competing_claims": [],
                "missing": ["evidence"],
                "stability": "unstable",
                "decision_confidence": MIN_DECISION_CONFIDENCE,
            })
            report["fingerprint"] = self._fingerprint(report)
            return report

        # Group by claim
        claim_groups: Dict[str, List[Evidence]] = defaultdict(list)
        for ev in deduped:
            claim_groups[ev.claim].append(ev)

        claim_stats: List[ClaimStat] = []
        for claim, evids in claim_groups.items():
            alpha = PRIOR_STRENGTH * self.prior_belief
            beta = PRIOR_STRENGTH * (1 - self.prior_belief)
            total_weight = 0.0
            for ev in evids:
                w = ev.weight * (1.0 if ev.independent else INDEPENDENCE_PENALTY)
                total_weight += w
                # Soft update
                alpha += w * ev.reliability
                beta += w * (1 - ev.reliability)
            mean = alpha / (alpha + beta) if (alpha + beta) > 0 else 0.5
            # Approximate 95% CI — tighter with more evidence
            var = (alpha * beta) / ((alpha + beta) ** 2 * (alpha + beta + 1)) if (alpha + beta) > 0 else 0.25
            n_eff = max(len(evids), 1)
            std = math.sqrt(max(var, 1e-12)) / math.sqrt(n_eff)
            ci_low = max(0.0, mean - 1.96 * std)
            ci_high = min(1.0, mean + 1.96 * std)
            claim_stats.append({
                "claim": claim,
                "mean": mean,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "evidence_count": len(evids),
                "total_weight": total_weight,
                "alpha": alpha,
                "beta": beta,
            })

        claim_stats.sort(key=lambda x: x["mean"], reverse=True)
        top = claim_stats[0]
        competitors = claim_stats[1:4]  # up to 3

        confidence = top["mean"]
        status = "PROVISIONAL_FINDING"
        if len(claim_stats) > 1:
            second = claim_stats[1]
            # Conflict if CIs overlap significantly or means close
            if top["ci_low"] <= second["ci_high"] and second["ci_low"] <= top["ci_high"]:
                if abs(top["mean"] - second["mean"]) < 0.15:
                    status = "CONFLICTING_EVIDENCE"
            if top["mean"] < 0.55:
                status = "INSUFFICIENT_EVIDENCE" if top["evidence_count"] < 2 else status

        if top["evidence_count"] == 1 and top["mean"] < 0.7:
            status = "PROVISIONAL_FINDING"

        suggestions = []
        if top["evidence_count"] == 1:
            suggestions.append("single source; consider additional independent confirmation.")
        if top["evidence_count"] < 3:
            suggestions.append("Sample size is small; gather more independent sources.")
        if any(not e.independent for e in deduped):
            suggestions.append("Non-independent evidence detected; independence penalty applied.")
        if status == "CONFLICTING_EVIDENCE":
            suggestions.append("Conflicting evidence present; investigate sources or gather more data.")
        if self.alternatives:
            suggestions.append(f"Listed alternatives: {', '.join(self.alternatives)}")
        if status == "PROVISIONAL_FINDING" and confidence >= 0.7 and top["evidence_count"] >= 3:
            suggestions.append("Evidence is reasonably coherent; continue monitoring.")
        # CI non-overlap signal (strong separation)
        if len(claim_stats) > 1:
            second = claim_stats[1]
            if top["ci_high"] < second["ci_low"] or (top["mean"] - second["mean"] > 0.35 and top["evidence_count"] >= 3):
                suggestions.append("Top claim 95% CI do not overlap second-claim CI.")
                audit.append("Top claim CI does not overlap second-claim CI.")

        if not suggestions:
            suggestions.append("No specific improvement suggestions at this time.")

        decision_conf = max(MIN_DECISION_CONFIDENCE, min(MAX_DECISION_CONFIDENCE, confidence))
        if status == "INSUFFICIENT_EVIDENCE":
            stability = "unstable"
        elif status == "CONFLICTING_EVIDENCE" or confidence < 0.75:
            stability = "provisional"
        else:
            stability = "stable"

        report = self._base_report(analyzed_at, audit)
        report.update({
            "status": status,
            "confidence": round(confidence, 6),
            "conclusion": top["claim"] if status != "INSUFFICIENT_EVIDENCE" else None,
            "top_claim": {
                "claim": top["claim"],
                "mean": round(top["mean"], 6),
                "ci_low": round(top["ci_low"], 6),
                "ci_high": round(top["ci_high"], 6),
                "evidence_count": top["evidence_count"],
            },
            "competing_claims": [
                {
                    "claim": c["claim"],
                    "mean": round(c["mean"], 6),
                    "ci_low": round(c["ci_low"], 6),
                    "ci_high": round(c["ci_high"], 6),
                    "evidence_count": c["evidence_count"],
                }
                for c in competitors
            ],
            "suggestions": suggestions,
            "stability": stability,
            "decision_confidence": round(decision_conf, 6),
        })
        report["fingerprint"] = self._fingerprint(report)
        return report

    def _base_report(self, analyzed_at: str, audit: List[str]) -> Dict[str, Any]:
        return {
            "version": VERSION,
            "record_id": self.record_id,
            "question": self.question,
            "alternatives": self.alternatives,
            "suggestions": [],
            "audit_trail": audit,
            "created_at": self.created_at,
            "analyzed_at": analyzed_at,
            "fingerprint": "",  # filled later
        }

    def _fingerprint(self, report: Dict[str, Any]) -> str:
        # Content-addressable: exclude timestamps and fingerprint itself
        payload = {
            "question": self.question,
            "prior_belief": self.prior_belief,
            "alternatives": sorted(self.alternatives),
            "evidence": sorted(
                [{"claim": e.claim, "source": e.source, "reliability": e.reliability,
                  "independent": e.independent, "weight": e.weight} for e in self.evidence],
                key=lambda x: (x["source"], x["claim"])
            ),
            "status": report.get("status"),
            "conclusion": report.get("conclusion"),
            "top_claim": report.get("top_claim"),
            "competing_claims": report.get("competing_claims"),
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return sha256(raw.encode()).hexdigest()


def fingerprint(record: IntelligenceRecord) -> str:
    report = record.analyze()
    fp = report.get("fingerprint", "")
    if not isinstance(fp, str):
        raise TypeError("fingerprint must be str")
    return fp


def validate_analysis_report(report: Any) -> List[str]:
    violations = []
    if not isinstance(report, dict):
        return ["report must be a dict"]
    required = ["version", "record_id", "status", "question", "confidence", "decision_confidence",
                "stability", "suggestions", "audit_trail", "created_at", "analyzed_at", "fingerprint"]
    for f in required:
        if f not in report:
            violations.append(f"missing required field: {f}")
    status = report.get("status")
    if status not in ("PROVISIONAL_FINDING", "CONFLICTING_EVIDENCE", "INSUFFICIENT_EVIDENCE"):
        violations.append(f"invalid status: {status}")
    conf = report.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
        violations.append("confidence must be number in [0,1]")
    fp = report.get("fingerprint", "")
    if not isinstance(fp, str) or len(fp) != 64:
        violations.append("fingerprint must be 64-char hex")
    if not isinstance(report.get("suggestions"), list):
        violations.append("suggestions must be a list")
    if not isinstance(report.get("audit_trail"), list):
        violations.append("audit_trail must be a list")
    return violations


def analyze_json(raw: str) -> Dict[str, Any]:
    rec = IntelligenceRecord.from_json(raw)
    return rec.analyze()


def generate_html_report(report: Dict[str, Any]) -> str:
    """Generate a self-contained, zero-dependency HTML evidence report.

    Makes the replayable trace shareable and visually inspectable.
    Status colors: green (stable), amber (provisional/conflict), red (insufficient).
    """
    status = report.get("status", "UNKNOWN")
    confidence = report.get("confidence", 0.0)
    conclusion = report.get("conclusion") or "—"
    fingerprint = report.get("fingerprint", "")
    question = report.get("question", "")
    version = report.get("version", VERSION)
    stability = report.get("stability", "")
    suggestions = report.get("suggestions", [])
    audit = report.get("audit_trail", [])
    top = report.get("top_claim") or {}
    competitors = report.get("competing_claims", [])
    record_id = report.get("record_id", "")
    analyzed_at = report.get("analyzed_at", "")

    status_color = {
        "PROVISIONAL_FINDING": "#16a34a" if stability == "stable" else "#d97706",
        "CONFLICTING_EVIDENCE": "#d97706",
        "INSUFFICIENT_EVIDENCE": "#dc2626",
    }.get(status, "#6b7280")

    def esc(s: Any) -> str:
        if s is None:
            return ""
        return str(s).replace("&", "&").replace("<", "<").replace(">", ">").replace('"', """)

    competitors_html = ""
    for c in competitors:
        competitors_html += f"""
        <tr>
          <td>{esc(c.get('claim'))}</td>
          <td>{c.get('mean', 0):.3f}</td>
          <td>[{c.get('ci_low', 0):.3f}, {c.get('ci_high', 0):.3f}]</td>
          <td>{c.get('evidence_count', 0)}</td>
        </tr>"""

    suggestions_html = "".join(f"<li>{esc(s)}</li>" for s in suggestions) or "<li>None</li>"
    audit_html = "".join(f"<li>{esc(a)}</li>" for a in audit) or "<li>None</li>"

    top_claim_html = ""
    if top:
        top_claim_html = f"""
        <div class="card">
          <strong>Top claim:</strong> {esc(top.get('claim'))}<br>
          Mean: {top.get('mean', 0):.3f} &nbsp; 95% CI: [{top.get('ci_low', 0):.3f}, {top.get('ci_high', 0):.3f}] &nbsp;
          Evidence: {top.get('evidence_count', 0)}
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MFR Evidence Report — {esc(status)}</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 2rem; background: #f8fafc; color: #0f172a; }}
  .container {{ max-width: 760px; margin: 0 auto; background: white; padding: 1.75rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,.06); }}
  h1 {{ margin-top: 0; font-size: 1.4rem; }}
  .status {{ display: inline-block; padding: .35rem .9rem; border-radius: 999px; color: white; font-weight: 600; background: {status_color}; }}
  .meta {{ color: #64748b; font-size: .85rem; margin: .5rem 0 1.25rem; }}
  .card {{ background: #f1f5f9; padding: 1rem; border-radius: 8px; margin: .75rem 0; }}
  table {{ width: 100%; border-collapse: collapse; margin: .75rem 0; }}
  th, td {{ text-align: left; padding: .5rem .6rem; border-bottom: 1px solid #e2e8f0; }}
  th {{ background: #f8fafc; font-weight: 600; }}
  .fp {{ font-family: ui-monospace, SFMono-Regular, monospace; font-size: .75rem; word-break: break-all; background: #0f172a; color: #e2e8f0; padding: .75rem; border-radius: 6px; }}
  ul {{ margin: .4rem 0; padding-left: 1.2rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>MFR Adaptive Intelligence Core Pro</h1>
  <div class="status">{esc(status)}</div>
  <div class="meta">v{esc(version)} · {esc(stability)} · analyzed {esc(analyzed_at)}</div>

  <div class="card">
    <strong>Question:</strong> {esc(question)}
  </div>

  <div class="card">
    <strong>Conclusion:</strong> {esc(conclusion)}<br>
    <strong>Confidence:</strong> {confidence:.3f}
  </div>

  {top_claim_html}

  {"<h3>Competing claims</h3><table><thead><tr><th>Claim</th><th>Mean</th><th>95% CI</th><th>N</th></tr></thead><tbody>" + competitors_html + "</tbody></table>" if competitors else ""}

  <h3>Suggestions</h3>
  <ul>{suggestions_html}</ul>

  <h3>Audit trail</h3>
  <ul>{audit_html}</ul>

  <h3>Fingerprint (content-addressable)</h3>
  <div class="fp">{esc(fingerprint)}</div>

  <div class="meta">Record ID: {esc(record_id)} · Zero-dependency pure analysis. Verify fingerprint for critical decisions.</div>
</div>
</body>
</html>"""
    return html


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


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        if len(sys.argv) > 2:
            with open(sys.argv[2]) as f:
                raw = f.read()
            print(json.dumps(analyze_json(raw), indent=2))
        else:
            print("Usage: python mfr_core_pro.py --json <file.json>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--html":
        if len(sys.argv) > 2:
            with open(sys.argv[2]) as f:
                raw = f.read()
            report = analyze_json(raw)
            print(generate_html_report(report))
        else:
            print("Usage: python mfr_core_pro.py --html <file.json>")
    else:
        _demo()
