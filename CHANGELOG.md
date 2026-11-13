# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [Unreleased]

### Fixed
- CLI `--json` now handles missing files and permission errors with clear stderr messages and non-zero exit. Invalid JSON and other ValueError/OSError paths also exit cleanly. Previous silent crash on FileNotFoundError is resolved.
- Strengthened `IntelligenceRecord.from_json` to raise clear `ValueError` on invalid JSON, non-object root, or missing/invalid question field. Non-dict evidence items are skipped. Valid inputs unchanged.
- Restored CHANGELOG.md content that was accidentally truncated in a documentation commit. Public history for 2.1.56-pro and 2.1.59-pro is again present.

### Added
- Regression test `test_cli_missing_file` for the new CLI error path. Coverage remains ≥95%. All 46 tests pass.

## [2.1.60-pro] - 2026-11-13

### Fixed
- CLI `--json` robustness: FileNotFoundError, PermissionError, and other I/O/JSON errors now produce clear messages and exit code 1 instead of unhandled exceptions.

### Added
- `test_cli_missing_file` regression test.

## [2.1.59-pro] - 2026-11-10

### Fixed
- Strict mypy compliance: introduced `ClaimStat` TypedDict for claim statistics, resolved all type errors under `mypy --strict`. Fingerprint helper now type-safe. No behavioral change.

### Notes
- Type safety improvement aligns public surface claim of clean strict typing. All 39 tests continue to pass. Version sources (version.py, pyproject.toml, README) aligned.

## [2.1.56-pro] - 2026-11-09

### Fixed
- `competing_claims` previously included the top claim itself (semantic bug in report contract). It now correctly excludes the top claim and returns the next up to 3 competitors (`claim_stats[1:4]`). Single-claim analyses now correctly yield an empty competitors list.

### Added
- Regression test `test_competing_claims_excludes_top` covering multi-claim and single-claim cases.
- Strengthened `test_conflicting_evidence_detected` to assert top claim is never present in `competing_claims`.

### Notes
- Pure correctness fix; Bayesian math, fingerprints, and decision-contract fields unchanged. Backward-compatible for consumers that already treated competitors as the remainder of ranked claims.
