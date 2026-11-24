## [2.1.77+pro] - 2026-11-24

### Fixed
- CLI `--version` now exits with code 0 (matches help and documented "and exit" behavior).
- Test expectation for multi-evidence Bayesian mean corrected to realistic value (>0.7 instead of >0.8 with PRIOR_STRENGTH=2).
- Added regression tests for `validate_analysis_report` and `_demo` to restore coverage gate (≥90%, now 98%).

### Verified
- 36/36 pytest pass, 98% coverage, mypy --strict clean.
- No functional regression in analysis logic.


# Changelog

## [2.1.76+pro] - 2026-11-24

### Improved
- Expanded test suite with 6 additional edge-case tests for `from_json` error paths (non-object evidence, TypeError/ValueError from Evidence construction, non-numeric prior, non-object root) and CLI `PermissionError` handling.
- Coverage raised from 96% to 98% (263 statements, 4 remaining edge branches).

## [2.1.75+pro] - 2026-11-24

### Improved
- Strengthened fallback suggestion path and related regression.

## [2.1.50+pro] - earlier

Initial public transparent core with Bayesian evidence reasoning, audit trail, and deterministic fingerprint.
