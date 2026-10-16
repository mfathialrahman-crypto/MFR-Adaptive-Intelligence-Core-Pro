# MFR Adaptive Intelligence Core Pro

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro/actions)
[![Version](https://img.shields.io/badge/version-2.1.8--pro-orange)](https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro)
[![FathiMind](https://img.shields.io/badge/FathiMind-Public%20Core-blueviolet)](https://github.com/mfathialrahman-crypto/FathiMind)

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Version **2.1.8-pro**  
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
python -m unittest test_mfr_core_pro.py -v
```

Or single-file usage (zero install):

```bash
python mfr_core_pro.py
```

---
