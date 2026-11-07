# AGENTS.md — Project Engineering Constitution

**MFR Adaptive Intelligence Core Pro** (public MIT layer of FathiMind)

This file is the binding constitution for every human contributor and AI agent working on this repository.

## Doctrine (non-negotiable)

1. No strong recommendation at low confidence.
2. No fake changes or invented test results.
3. Every decision is a replayable trace (fingerprint + full audit trail).
4. Layers stay separate — this package is the transparent evidence → Bayesian verification layer only.
5. Public transparency where it builds trust; private engines stay private.
6. Continuous evolution only with verified, high-value, safe changes.

Priority order: **stability → security → functional correctness → performance → quality → UX → innovation**.

## Evidence rules

- Do not claim a fix until code is changed, tests run, and results observed.
- Do not invent coverage numbers, versions, or CI conclusions.
- Prefer small branch commits; never force-push main; create PRs for review.
- Redact secrets (tokens, paths, credentials) in logs and public artifacts.
- Fail closed on uncertain inputs (bounds, validation, no-follow where applicable).

## Single source of truth

- Version lives in `version.py`. `pyproject.toml`, README, badges, and public signals must stay aligned.
- CI (Python 3.10–3.13 matrix + coverage ≥90% + mypy --strict + version-consistency) is the contract.
- Claims of health or performance must be reproducible by `pytest` or the demo in under five minutes.

## Public competitiveness

- Accurate badges tied to default-branch CI.
- Zero-dependency runtime. One-command demo + tests.
- Architecture diagram and doctrine in README.
- Topics: `fathimind`, `cognitive-systems`, `engineering-os`, `bayesian`, `evidence`, `audit-trail`.
- No inflated metrics. Evidence links over adjectives.

## Last reviewed

- 2026-11-07T16:33+04 — Independent local clone verification: pytest 31/31 passed, coverage 98%, mypy --strict clean, version 2.1.50-pro aligned. Constitution restored from PLACEHOLDER.

---

Part of the [FathiMind](https://github.com/mfathialrahman-crypto/FathiMind) cognitive engineering operating system.
