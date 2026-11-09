# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version segment is a public surface marker).

## [Unreleased]

### Fixed
- Version string made PEP 440 compliant: `2.1.52+pro` (local version segment). Resolves `pip install -e` / packaging build failure caused by invalid `-pro` suffix. Branding preserved. Tests and mypy unchanged.

### Changed
- README version badge and current-version line aligned to `2.1.52+pro`.

### Documented
- Independent verification cycle (2026-11-09T06:20+04): Local clone, pytest 35/35 passed in 0.07s, mypy --strict clean. Packaging issue identified and fixed. AGENTS.md stamp refreshed. No remaining P0/P1. Continuous improvement active.

## [2.1.51-pro] - 2026-11-08

### Added
- Pure-Python `validate_analysis_report(report)` helper. Returns list of contract violations (empty if valid). Strengthens reliability verification without external dependencies. Covers required fields, status enum, confidence clamps, stability, fingerprint length, and list types.
- Unit test confirming every `analyze()` path produces a report that passes the validator, plus basic rejection cases.

### Changed
- Version bumped to 2.1.51-pro. Schema documentation updated to note decision-contract fields are always present.

### Documented
- Independent verification cycle (2026-11-08T14:20+04): Local clone, pytest 32/32 passed, coverage 98%, mypy --strict clean. AGENTS.md stamp refreshed. No P0/P1 issues. Continuous improvement active.
