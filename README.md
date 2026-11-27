# MFR Adaptive Intelligence Core Pro

[![Tests](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.1.79%2Bpro-green)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/blob/main/version.py)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Transparent adaptive intelligence core of the FathiMind ecosystem.  
Zero-dependency public MIT package. Deterministic, auditable, and evidence-first.

**Current version:** `2.1.80+pro` (see `version.py`)

## Doctrine

- No strong recommendation at low confidence.
- Every decision is a replayable trace (fingerprint + full audit trail).
- Layers stay separate: this core measures and verifies evidence; it does not invent facts.
- Public surface is accurate, tested, and competitive. No performance or security claims beyond what the tests demonstrate.

## Quick start

```bash
pip install -e .
mfr-core --help
mfr-core --version
python mfr_core_pro.py          # demo
```

## Analysis example

Use the included `sample_record.json`:

```bash
python mfr_core_pro.py --json sample_record.json
# or from stdin: cat sample_record.json | python mfr_core_pro.py --json -
```

See `schemas/analysis.schema.json` for the full report contract.

## Development

```bash
pip install -e ".[dev]"
pytest
mypy --strict mfr_core_pro.py version.py
```

Coverage gate ≥90% is enforced in CI.

## Architecture note

This is the public transparent core. Private engines (HelixMind, MFR-Cognition, AetherMind, SovereignEvolution) remain proprietary.

Full handbook: [FathiMind HQ](https://github.com/mfathialrahman-crypto/FathiMind).
