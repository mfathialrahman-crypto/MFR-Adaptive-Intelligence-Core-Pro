# Changelog

## [Unreleased]

### Improved
- CLI `--json` file reading now uses explicit `encoding="utf-8"` for reliable cross-platform handling of non-ASCII content.
- Added regression test `test_cli_json_utf8_file` covering non-ASCII question/claim/source.

### Verified
- 24 tests pass. Coverage ≥90%. mypy --strict clean. No functional change to valid analysis paths.


## [2.1.78+pro] - 2026-11-26

### Added
- CLI `--validate` flag: after `--json` analysis, runs pure-Python contract validation and exits 2 on violations. Strengthens public reproducibility of the decision-contract fields without changing analysis results.

### Verified
- 23 tests pass. Coverage ≥90%. mypy --strict clean. No functional change to valid analysis paths.

## [2.1.77+pro] - 2026-11-26

### Fixed
- Restored complete AGENTS.md Project Engineering Constitution (was placeholder).
- Expanded test suite with regression coverage for analysis paths (deduplication, conflict, insufficient evidence, suggestions, stability), fingerprint determinism, from_json round-trip, validate_analysis_report, and CLI (version, --json file/stdin, error paths).
- Coverage restored to ≥90% (verified 91% locally) so the CI gate passes again.

### Verified
- 18 tests pass.
- No functional change to valid analysis behavior.
- Version alignment (version.py == pyproject.toml) preserved.
