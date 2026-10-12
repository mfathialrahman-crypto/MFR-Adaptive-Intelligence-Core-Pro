# MFR Adaptive Intelligence Core Pro

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Version **2.1.1-pro**

Public cognitive component of the FathiMind ecosystem.  
A rigorous, transparent, and self-improving evidence analysis engine.

## Why this exists

Most "intelligence" scripts do simple averaging and call it confidence.  
This core does better:

- Bayesian-inspired belief updating (Beta prior)
- Real independence penalty (non-independent evidence is down-weighted)
- Approximate 95% credible intervals
- Full audit trail for every decision
- Automatic generation of actionable improvement suggestions
- Stable content-addressable fingerprinting
- Weight-capped soft observations so posteriors stay valid even with extreme weights

## Installation

```bash
git clone https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git
cd MFR-Adaptive-Intelligence-Core-Pro
python -m pip install -e .  # optional (requires pyproject.toml)
```

Or just run the single file:

```bash
python mfr_core_pro.py
```

## Quick Example

```python
from mfr_core_pro import IntelligenceRecord, Evidence

record = IntelligenceRecord(
    question="هل هذا المستند صحيح؟",
    evidence=[
        Evidence("المستند صحيح", "source-A", 0.92, independent=True, weight=1.2),
        Evidence("المستند صحيح", "source-B", 0.88, independent=True),
        Evidence("المستند صحيح", "source-C", 0.75, independent=False),
    ],
)

result = record.analyze()
print(result["status"])
print(result["confidence"])
print(result["conclusion"])
print(result["suggestions"])
print(result["fingerprint"])
```

## Running Tests

```bash
python -m unittest test_mfr_core_pro.py -v
```

## Design Doctrine (aligned with FathiMind)

1. No strong claim at low confidence.
2. Independence is enforced, not just declared.
3. Every decision leaves a replayable trace.
4. The system must suggest its own next improvement.
5. Provisional findings only — never absolute certainty.

## Part of the FathiMind Stack

- **HelixMind** → measure
- **MFR-Cognition** → verify
- **AetherMind** → reason
- **SovereignEvolution** → evolve
- **This Core (public)** → transparent adaptive analysis layer

## License

MIT License — free to use, modify, and distribute with attribution.

---

Built and continuously evolved by **Mohamed Fathi Alrahman**  
FathiMind — human-centric cognitive engineering.
