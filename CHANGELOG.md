# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version marker is a public surface identifier, PEP 440 compliant).

## [2.1.59+pro] - 2026-11-10

### Fixed
- Packaging: version string made PEP 440 compliant (`2.1.59+pro` local version). Previous `2.1.59-pro` blocked `pip install -e` and setuptools validation.
- Strict mypy compliance retained: `ClaimStat` TypedDict for claim statistics, fingerprint helper type-safe. No behavioral change.

### Notes
- Verified locally: 39/39 tests pass. Packaging now succeeds. Version sources aligned (version.py, pyproject.toml, README, CHANGELOG).

## [2.1.56-pro] - 2026-11-09

### Fixed
- `competing_claims` previously included the top claim itself (semantic bug in report contract). It now correctly excludes the top claim and returns the next up to 3 competitors (`claim_stats[1:4]`). Single-claim analyses now correctly yield an empty competitors list.

### Notes
- All 39 tests continue to pass. Documentation and version sources updated.
