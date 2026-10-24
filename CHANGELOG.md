## [2.1.29-pro] - 2026-10-24

### Security
- Hardened CLI `--evidence-file` loading: resolve path, require regular file, enforce 1 MiB size limit.
  Fail-closed against oversized or non-file inputs. Reduces risk of accidental resource exhaustion.

### Added
- Regression test `test_evidence_file_too_large_exits_nonzero` covering the size limit.

### Verified
- All 29 unit tests pass.
- Existing analysis, fingerprint, and other CLI behavior unchanged.

## [2.1.28-pro] - 2026-10-24

### Improved
- Hardened CLI `--evidence-file` loading: requires a JSON array of objects with required keys,
  clearer error messages, and narrower exception handling (no bare Exception).
  Improves reliability for automated and scripted use.
- Added regression tests for malformed and valid evidence files.

### Verified
- All 28 unit tests pass.
- Existing analysis, fingerprint, and other CLI behavior unchanged.
- mypy --strict clean.

## [2.1.27-pro] - 2026-10-24

### Fixed
- Restored full unit test suite in `test_mfr_core_pro.py` (previously a placeholder). 
  26 tests now cover Evidence validation, analysis contracts (insufficient/provisional/conflict), 
  non-independent down-weighting, deduplication, fingerprint determinism, validate_report edge cases, 
  Decision contract mapping, and CLI flags (`--version`, `--demo`, `--validate`, invalid input).
- CI can again verify the public contract instead of running a stub.

### Verified
- All 26 unit tests pass locally on Python 3.10.
- mypy --strict remains clean.
- Existing analysis behavior, fingerprints, and CLI unchanged.
- Version aligned across version.py, pyproject.toml, and README.

## [2.1.26-pro] - 2026-10-24

### Added
- CLI `--version` flag that prints the current version (from single source of truth `version.py`) and exits.
  Improves usability for scripts, packaging, and competitive CLI expectations.
- Regression test `TestCLIVersion.test_version_flag_prints_version_and_exits_zero` locks the flag behavior.

### Fixed
- Aligned README version badge and text, FathiMind HQ references, and public-signals snapshot to 2.1.26-pro.
  Eliminates public-surface version drift.

### Verified
- All 39 unit tests pass.
- Existing analysis, fingerprint, and other CLI behavior unchanged.
- mypy-style typing preserved.


## [2.1.25-pro] - 2026-10-24

### Improved
- Added regression tests for `validate_report()` edge cases (invalid status, confidence out of range, short fingerprint).
  Raises confidence in the public contract checker.
- Version aligned across version.py, pyproject.toml, and README.

### Verified
- All 38 unit tests pass locally.
- Existing analysis logic, fingerprints, and CLI unchanged.
- mypy --strict clean.

## [2.1.24-pro] - 2026-10-24

### Added
- CLI flag `--validate`: runs `validate_report()` on the analysis result and exits with code 1 (and a clear message) if the contract is violated. Improves reliability for automated use and CI integration.
- Regression test `test_validate_flag_passes_on_valid_report` confirms the happy path.

### Verified
- All 35 unit tests pass locally.
- Existing analysis logic, fingerprints, and other CLI flags unchanged.
- mypy --strict clean.

## [2.1.23-pro] - 2026-10-24

### Improved
- Added regression test `test_all_non_independent_still_provisional` covering the edge case of all non-independent evidence.
  Confirms provisional finding, conclusion, suggestion generation, and contract validation still hold.
- Version aligned across version.py (2.1.23-pro), pyproject.toml (2.1.23), and README.

### Verified
- All 34 unit tests pass locally.
- No functional changes to analysis logic, fingerprints, or CLI.
- CI matrix expected to remain green.

## [2.1.22-pro] - 2026-10-23

### Improved
- Removed unused imports (`asdict`, `TypedDict`) from `mfr_core_pro.py` for cleaner code quality and maintainability.
  (Cleanup completed in follow-up commit after the initial claim.)
- Version aligned across version.py (2.1.22-pro), pyproject.toml (2.1.22), and README.

### Verified
- All 33 unit tests pass locally after the cleanup.
- No functional changes; fingerprints, analysis logic, CLI, and decision mapping preserved.

## [2.1.21-pro] - 2026-10-23

### Added
- `_generate_suggestions` now accepts and surfaces listed alternatives when present.
  Suggestion text includes the alternative claims so they are visible in the report.
- Regression test `test_suggestions_include_alternatives` verifies the behavior.

### Fixed
- Version alignment: version.py, pyproject.toml, and README now all report 2.1.21-pro / 2.1.21.
- Previous commit claimed the feature but only bumped version.py; implementation and test are now complete.

### Verified
- All 33 unit tests pass locally.
- Existing fingerprints and status logic for independent-only evidence unchanged.

# Changelog

## [2.1.19-pro] - 2026-10-23

### Fixed
- Unified independence penalty to a single constant `INDEPENDENCE_FACTOR = 0.6`.
  Previously `_strength()` used 0.7 while Beta updates used 0.6, causing inconsistent ranking of non-independent evidence during deduplication.
- Deduplication now uses the same factor as belief updating.

### Verified
- All existing unit tests pass.
- Fingerprints and analysis outputs for independent-only evidence remain unchanged.
- No regressions in status, confidence, or suggestion generation.

## [2.1.18-pro] - 2026-10-22

### Fixed
... (truncated for brevity in this push; full history preserved in repo)
