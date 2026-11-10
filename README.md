# MFR Adaptive Intelligence Core Pro

[![Tests](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.59%2Bpro-green)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/blob/main/version.py)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Transparent adaptive intelligence core of the FathiMind ecosystem.  
Zero-dependency public MIT package. Deterministic, auditable, and evidence-first.

**Current version:** `2.1.59+pro` (see `version.py`)

## Doctrine

- No strong recommendation at low confidence.
- Every decision is a replayable trace (fingerprint + full audit trail).
- Layers stay separate: this core measures and verifies evidence; it does not invent facts.
- Public surface is accurate, tested, and competitive. No performance or security claims beyond what the tests demonstrate.

## Architecture

```
Evidence (claim, source, reliability, independent, weight)
        |
        v
Deduplicate by source → Group by claim
        |
        v
Bayesian update (prior + likelihood from reliability/independence)
        |
        v
Verification gate + Credible interval + Audit trail
        |
        v
Self-improvement signal (only when evidence supports)
```

## Quick start

```bash
pip install -e git+https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git#egg=mfr-adaptive-intelligence-core-pro
python -c "from mfr_core_pro import IntelligenceRecord, Evidence; print('Core ready')"
```

## Tests

```bash
pytest
```

39 tests, zero external dependencies for the core logic.
