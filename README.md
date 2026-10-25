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
  --validate \
  --compact

# Or load from JSON file:
python mfr_core_pro.py "Is the system secure?" --evidence-file evidence.json
```

The fourth argument (optional) is weight (>0, default 1.0).  
The fifth argument (optional) is independent flag (`true`/`false`/`yes`/`no`, default true).

Use `--validate` to enforce the analysis contract (exits non-zero if required fields or fingerprint are invalid).

Use `--compact` for single-line JSON suitable for pipelines.

Or run the demo:

```bash
python mfr_core_pro.py --demo
```
