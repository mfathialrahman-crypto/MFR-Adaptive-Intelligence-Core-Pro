# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [Unreleased]

## [2.1.61-pro] - 2026-11-14

### Added
- Console script entry point `mfr-core` (via `pyproject.toml` `[project.scripts]`). After `pip install -e .` the command `mfr-core` runs the demo or accepts `--json <file>`.
- Extracted `main()` function so the CLI is reusable and importable. Behavior of `python mfr_core_pro.py` unchanged for valid inputs; usage path now exits non-zero with message on stderr for consistency with other error paths.

### Notes
- All 46 tests pass. mypy --strict clean. Coverage remains ≥90%. Version sources aligned.

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
