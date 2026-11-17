# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [2.1.65-pro] - 2026-11-17

### Changed
- CLI --help output now lists both the installed `mfr-core` command and the direct `python mfr_core_pro.py` form, with cleaner formatting.

### Notes
- No change to analysis logic. 53 tests continue to pass. mypy --strict clean. Continuous improvement cycle active.

## [2.1.64-pro] - 2026-11-16

### Added
- CLI `--help` / `-h` flag prints usage (demo, --version, --json) and exits 0.
- Regression test `test_cli_help_flag` covering the new help path.

### Notes
- 53 tests pass. mypy --strict clean. Coverage remains ≥90%. Continuous improvement cycle active. No behavioral change to analysis logic.

## [2.1.63-pro] - 2026-11-14

### Added
- Regression tests for low-mean single-source and multi-source paths (`test_low_mean_single_source_stays_provisional`, `test_low_mean_two_sources_insufficient`).

### Notes
- 52 tests pass. mypy --strict clean. Coverage remains ≥90%. Continuous improvement cycle active.

## [2.1.62-pro] - 2026-11-14

### Added
- CLI `--version` / `-V` flag prints the current package version and exits 0.
- Direct-coverage tests for `--version` / `-V` and default demo path (`test_cli_version_flag`, `test_cli_default_demo_runs`) so coverage stays ≥90%.

### Notes
- 50 tests pass. mypy --strict clean. Coverage 91.9% (≥90% gate). Version sources aligned. CI expected green after this fix.

## [2.1.61-pro] - 2026-11-14

### Added
- Console script entry point `mfr-core` (via `pyproject.toml` `[project.scripts]`). After `pip install -e .` the command `mfr-core` runs the demo or accepts `--json <file>`.
- Extracted `main()` function so the CLI is reusable and importable. Behavior of `python mfr_core_pro.py` unchanged.

### Changed
- CLI usage message for missing `--json` argument now goes to stderr and the process exits with code 1 (consistent with other error paths). Previously printed to stdout and exited 0.

### Notes
- All 48 tests pass. mypy --strict clean. Coverage remains ≥90%. Version sources (version.py, pyproject.toml, README) aligned.

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
