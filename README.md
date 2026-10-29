# MFR Adaptive Intelligence Core Pro

**Transparent Bayesian evidence analysis for the FathiMind cognitive operating system.**

[![CI](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.44--pro-orange)](version.py)

Zero-dependency public package. Evidence → Bayesian belief update (Beta prior) → verification → actionable suggestions. Full audit trail and content-addressable fingerprint.

```
question + evidence list
        │
        ▼
   Beta posterior update (independence-weighted)
        │
        ▼
   claim ranking + 95% CI
        │
        ▼
   status (PROVISIONAL_FINDING | CONFLICTING_EVIDENCE | INSUFFICIENT_EVIDENCE)
        │
        ▼
   suggestions + fingerprint
```

## Quick start

```bash
# Clone and run the demo
git clone https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git
cd MFR-Adaptive-Intelligence-Core-Pro
python mfr_core_pro.py --demo
```

Or analyze your own evidence:

```bash
python mfr_core_pro.py --evidence-file my_evidence.json
```

Example `my_evidence.json`:

```json
{
  "question": "Is the service healthy?",
  "prior_belief": 0.5,
  "alternatives": ["healthy", "degraded"],
  "evidence": [
    {"claim": "healthy", "source": "probe-1", "reliability": 0.9, "independent": true},
    {"claim": "healthy", "source": "probe-2", "reliability": 0.85, "independent": true}
  ]
}
```

## Tests

```bash
pip install pytest
python -m pytest test_mfr_core_pro.py -v
```

Matrix tested on Python 3.10–3.13 via GitHub Actions. Type-checked with `mypy --strict`.

## Doctrine

1. No strong recommendation at low confidence.
2. Every decision is a replayable trace (fingerprint + audit_trail).
3. Layers stay separate — this package is the transparent public core only.
4. Public transparency where it builds trust.

See [AGENTS.md](AGENTS.md) for the full engineering constitution.

## Architecture note

This is the public MIT surface of the FathiMind ecosystem. Private engines (HelixMind, MFR-Cognition, AetherMind, SovereignEvolution) remain proprietary. Shared schemas live in the [FathiMind HQ](https://github.com/mfathialrahman-crypto/FathiMind) repository.

**Owner:** Mohamed Fathi Alrahman
