# MFR Adaptive Intelligence Core Pro

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Version](https://img.shields.io/badge/version-2.1.30--pro-orange)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro)
[![FathiMind](https://img.shields.io/badge/FathiMind-Public%20Core-blueviolet)](https://github.com/mfathialrahman-crypto/FathiMind)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Version **2.1.30-pro**  
Public cognitive component of the [FathiMind](https://github.com/mfathialrahman-crypto/FathiMind) ecosystem.

A rigorous, transparent, and self-improving evidence analysis engine designed for real decisions — not toy averaging.

---

## Why this exists

Most “intelligence” scripts do simple averaging and call it confidence.  
This core does better:

- **Bayesian-inspired belief updating** (Beta prior + soft observations)
- **Real independence penalty** (non-independent evidence is down-weighted)
- **Approximate 95% credible intervals**
- **Full audit trail** for every decision
- **Automatic generation of actionable improvement suggestions**
- **Stable content-addressable fingerprinting**
- **Weight-capped soft observations** so posteriors stay valid even with extreme weights
- **Conflict detection** with explanatory status

---

## Quick Start

```bash
git clone https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git
cd MFR-Adaptive-Intelligence-Core-Pro
pip install -e .
python mfr_core_pro.py          # runs the three demo cases
python -m pytest test_mfr_core_pro.py -v
```

Or single-file usage (zero install):

```bash
python mfr_core_pro.py
```

---


## CLI Usage

```bash
python mfr_core_pro.py "Is the system secure?" \
  --evidence "secure" "audit-firm" 0.91 \
  --evidence "vulnerable" "researcher" 0.87 1.2 false \
  --alternatives "partially secure" \
  --prior 0.5 \
  --validate

# Or load from JSON file:
python mfr_core_pro.py "Is the system secure?" --evidence-file evidence.json
```

The fourth argument (optional) is weight (>0, default 1.0).  
The fifth argument (optional) is independent flag (`true`/`false`/`yes`/`no`, default true).

Use `--validate` to enforce the analysis contract (exits non-zero if required fields or fingerprint are invalid).

Or run the demo:

```bash
python mfr_core_pro.py --demo
```

## Minimal Example

```python
from mfr_core_pro import IntelligenceRecord, Evidence

record = IntelligenceRecord(
    question="هل هذا المستند صحيح؟",
    evidence=[
        Evidence("المستند صحيح", "source-A", 0.92, independent=True, weight=1.2),
        Evidence("المستند صحيح", "source-B", 0.88, independent=True),
        Evidence("المستند صحيح", "source-C", 0.75, independent=False),
    ],
    alternatives=["المستند مزيف", "المستند جزئياً صحيح"],
)

result = record.analyze()
print(result["status"])          # PROVISIONAL_FINDING or CONFLICTING_EVIDENCE
print(result["confidence"])      # posterior mean
print(result["conclusion"])
print(result["suggestions"])
print(result["fingerprint"])     # content-addressable hash

# Optional: emit a FathiMind Decision contract object (RFC-0001)
from mfr_core_pro import to_fathimind_decision
decision = to_fathimind_decision(result)
print(decision["status"], decision["confidence"])
```

---

## Architecture (Inside the Core)

```
INPUT (question + Evidence list)
        │
        ▼
   Deduplication by source (keep strongest)
        │
        ▼
   Independence penalty + weight capping
        │
        ▼
   Beta-style update (alpha / beta) per claim
        │
        ▼
   Ranking by effective score + posterior mean
        │
        ▼
   Conflict detection → status
        │
        ▼
   Suggestions + Audit trail + Fingerprint
```

Every output is a complete, replayable decision object.

---

## Design Doctrine (aligned with FathiMind)

1. **No strong claim at low confidence.**
2. **Independence is enforced, not just declared.**
3. **Every decision leaves a replayable trace.**
4. **The system must suggest its own next improvement.**
5. **Provisional findings only — never absolute certainty.**

The full Project Engineering Constitution that governs continuous improvement of this repository lives in [`AGENTS.md`](./AGENTS.md).

---

## Part of the FathiMind Stack

| Layer | Role |
|-------|------|
| HelixMind | measure |
| MFR-Cognition | verify |
| AetherMind | reason |
| SovereignEvolution | evolve |
| **This Core (public)** | transparent adaptive analysis |

---

## Testing & Quality

```bash
python -m pytest test_mfr_core_pro.py -v
```

All critical paths are covered. The core is intentionally dependency-free (stdlib only) so it can be dropped into any environment.

---

## License

MIT License — free to use, modify, and distribute with attribution.

---

Built and continuously evolved by **Mohamed Fathi Alrahman**  
[FathiMind](https://github.com/mfathialrahman-crypto/FathiMind) — human-centric cognitive engineering.
