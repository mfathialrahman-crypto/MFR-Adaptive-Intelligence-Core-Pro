# MFR Adaptive Intelligence Core Pro

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml/badge.svg)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions/workflows/run-demo.yml)
[![Version](https://img.shields.io/badge/version-2.1.43-pro-orange)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro)
[![FathiMind](https://img.shields.io/badge/FathiMind-Public%20Core-blueviolet)](https://github.com/mfathialrahman-crypto/FathiMind)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Version **2.1.43-pro**  
Public cognitive component of the [FathiMind](https://github.com/mfathialrahman-crypto/FathiMind) ecosystem.

Zero external dependencies. Pure Python. MIT licensed.

## What it does

Given a question and a list of evidence items (claim, source, reliability, independence, weight), it produces:

- A status: `PROVISIONAL_FINDING`, `CONFLICTING_EVIDENCE`, or `INSUFFICIENT_EVIDENCE`
- A confidence score and (when appropriate) a conclusion
- Approximate 95% credible intervals on the top claims
- An ordered list of competing claims with posterior means
- Actionable improvement suggestions
- A full audit trail
- A stable, content-addressable SHA-256 fingerprint
- A mapping to the FathiMind Decision contract

### Design properties

- Bayesian-inspired belief updating (Beta prior + soft observations)
- Real independence penalty (non-independent evidence is down-weighted)
- Approximate 95% credible intervals
- Full audit trail for every decision
- Automatic generation of actionable improvement suggestions
- Stable content-addressable fingerprinting
- Weight-capped soft observations so posteriors stay valid even with extreme weights
- Conflict detection with explanatory status

---

## Quick Start

```bash
git clone https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git
cd MFR-Adaptive-Intelligence-Core-Pro
pip install -e .
python mfr_core_pro.py          # runs the three demo cases
```

Or use the installed entry point:

```bash
mfr-core --version
mfr-core --validate
mfr-core --decision
```

### Analyze your own evidence

Create `evidence.json`:

```json
{
  "question": "Is the release safe to ship?",
  "prior_belief": 0.5,
  "evidence": [
    {"claim": "safe", "source": "ci-green", "reliability": 0.95, "independent": true, "weight": 1.0},
    {"claim": "safe", "source": "reviewer-A", "reliability": 0.8, "independent": true, "weight": 1.0},
    {"claim": "unsafe", "source": "flaky-test", "reliability": 0.4, "independent": false, "weight": 0.5}
  ],
  "alternatives": ["needs more tests", "hold for review"]
}
```

Then:

```bash
python mfr_core_pro.py --evidence-file evidence.json
python mfr_core_pro.py --evidence-file evidence.json --decision
python mfr_core_pro.py --evidence-file evidence.json --validate
```

---

## Output contract

The analysis report matches `schemas/analysis.schema.json`.

Key fields: `version`, `status`, `question`, `confidence`, `conclusion`, `top_claim`, `competing_claims`, `suggestions`, `audit_trail`, `fingerprint`.

See the schema for the full contract. Additive fields are allowed.

---

## Testing

```bash
pip install pytest pytest-cov
pytest test_mfr_core_pro.py -v
pytest test_mfr_core_pro.py --cov=mfr_core_pro --cov-report=term-missing
```

46 unit tests covering validation, analysis paths, fingerprint stability, decision contract, CLI edge cases, and suggestion generation.

Coverage on the core module is currently ~69% (CLI entry points are exercised via subprocess and not counted in the default coverage run). CI runs the same tests plus a strict mypy check and a version-consistency gate on Python 3.10–3.13.

---

## Versioning

Single source of truth is `version.py`. `pyproject.toml` and this README stay aligned.

---

## Documentation

- [AGENTS.md](AGENTS.md) — Project Engineering Constitution (continuous improvement rules)
- [CHANGELOG.md](CHANGELOG.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)

---

## License

MIT. See [LICENSE](LICENSE).

---

Part of the FathiMind cognitive operating system.
Public transparent layer. No secrets. Evidence first.
