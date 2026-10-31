# MFR Adaptive Intelligence Core Pro

[![CI](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/workflows/Run%20MFR%20Adaptive%20Intelligence%20Core%20Pro/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.45--pro-brightgreen)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/blob/main/version.py)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Transparent adaptive intelligence core of the FathiMind ecosystem.  
Zero-dependency public MIT package. Deterministic, auditable, and evidence-first.

**Current version:** `2.1.45-pro` (see `version.py`)

## Doctrine

- No strong recommendation at low confidence.
- Every decision is a replayable trace (fingerprint + full audit trail).
- Layers stay separate: this core measures and verifies evidence; it does not invent facts.
- Public surface is accurate, tested, and competitive. No performance or security claims beyond what the tests demonstrate.

## Architecture

```
Evidence (claim, source, reliability, independent, weight)
        │
        ▼
Deduplicate by source → Group by claim
        │
        ▼
Beta prior (strength 2.0) + soft positive / opposition updates
        │
        ▼
Posterior mean + approximate 95% CI
        │
        ▼
Status: INSUFFICIENT_EVIDENCE | CONFLICTING_EVIDENCE | PROVISIONAL_FINDING
        │
        ▼
Suggestions + content-addressable SHA-256 fingerprint
```

The analysis report conforms to the [JSON Schema](schemas/analysis.schema.json) (additive fields allowed).

## Quick start

```bash
# Clone and run tests (no install required for local use)
git clone https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git
cd MFR-Adaptive-Intelligence-Core-Pro
python -m pytest test_mfr_core_pro.py -v

# Or run the built-in demo
python mfr_core_pro.py
```

### Programmatic use

```python
from mfr_core_pro import Evidence, IntelligenceRecord

record = IntelligenceRecord(
    question="Is the system healthy?",
    evidence=[
        Evidence(claim="healthy", source="monitor-a", reliability=0.9, independent=True),
        Evidence(claim="healthy", source="monitor-b", reliability=0.85, independent=True),
        Evidence(claim="degraded", source="alert-c", reliability=0.4, independent=False),
    ],
    alternatives=["healthy", "degraded", "failed"],
)
report = record.analyze()
print(report["status"], report["conclusion"], report["confidence"])
print(report["fingerprint"])
```

## Installation

```bash
pip install -e .
# or
pip install pytest && python -m pytest
```

Requires Python ≥ 3.10. No third-party runtime dependencies.

## Testing & CI

- Unit tests: `python -m pytest test_mfr_core_pro.py -v`
- Type check: `mypy mfr_core_pro.py --strict`
- GitHub Actions matrix: Python 3.10–3.13 + version consistency between `version.py` and `pyproject.toml`.
- Coverage gate ≥ 90% on the core module.

## Security

See [SECURITY.md](SECURITY.md). Pure analysis library — no network, no secrets, no external calls.  
Always treat confidence scores as relative evidence strength, not absolute certainty. Verify fingerprints for critical decisions.

## License

MIT — see [LICENSE](LICENSE).

---

Part of the [FathiMind](https://github.com/mfathialrahman-crypto/FathiMind) cognitive engineering operating system.  
Topics: `fathimind`, `cognitive-systems`, `engineering-os`, `bayesian`, `evidence`.
