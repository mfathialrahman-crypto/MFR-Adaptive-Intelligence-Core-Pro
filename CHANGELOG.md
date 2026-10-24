## [2.1.26-pro] - 2026-10-24

### Improved
- Raised unit-test coverage of the CLI entry point (`main()`) from ~72% to 88% by adding direct calls with mocked `sys.argv`.
  Improves reliability of the command-line interface and regression protection without changing behavior.
- Added edge-case tests for invalid `--prior`, incomplete `--evidence` arguments, `--demo`, and `--alternatives`.

### Verified
- All 45 unit tests pass locally.
- Existing analysis logic, fingerprints, and CLI contract unchanged.
- mypy --strict clean.
- Coverage measured at 88% on `mfr_core_pro.py`.

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

## [2.1.21-pro] - 2026-10-23

### Improved
- Strengthened `validate_report()` with additional checks.
- Added tests for fingerprint length and status validation.

### Verified
- Tests pass.
- No behavior change to analysis.
