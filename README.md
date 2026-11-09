# MFR Adaptive Intelligence Core Pro

[![Tests](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.52+pro-green)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/blob/main/version.py)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Transparent adaptive intelligence core of the FathiMind ecosystem.  
Zero-dependency public MIT package. Deterministic, auditable, and evidence-first.

**Current version:** `2.1.52+pro` (see `version.py`)

## Doctrine

- No strong recommendation at low confidence.
- Every decision is a replayable trace (fingerprint + full audit trail).
- Layers stay separate: this core measures and verifies evidence; it does not invent facts.
- Public surface is accurate, tested, and competitive. No performance or security claims beyond what the tests demonstrate.

## Quick start

```bash
pip install -e git+https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git#egg=mfr-adaptive-intelligence-core-pro
python -c "from mfr_core_pro import IntelligenceRecord, Evidence; print('Core ready')"
```

Or clone and run the self-contained demo:

```bash
python mfr_core_pro.py
```

## Architecture (public core)

```
Evidence (claim, source, reliability, independent, weight)
    ↓
IntelligenceRecord.analyze()
    ↓
Bayesian update (Beta prior + soft observations + independence penalty + residual opposition)
    ↓
Status: PROVISIONAL_FINDING | CONFLICTING_EVIDENCE | INSUFFICIENT_EVIDENCE
    + confidence, 95% CI, suggestions, full audit trail, deterministic fingerprint
```

## Public contract

`IntelligenceRecord.analyze()` returns a dict containing at least:

- `version`, `record_id`, `status`, `question`, `confidence`, `decision_confidence`, `stability`
- `conclusion`, `top_claim`, `competing_claims`, `alternatives`, `suggestions`, `audit_trail`
- `created_at`, `analyzed_at`, `fingerprint` (SHA-256 content address)

See `schemas/analysis.schema.json` for the full machine-readable contract.

## Tests

```bash
pytest
```

35 tests covering validation, Bayesian updates, conflict detection, fingerprint stability, bounds, and the pure-Python report validator.

## License

MIT — see LICENSE.
