## [2.1.78+pro] - 2026-11-25

### Improved
- Added regression test for CLI FileNotFoundError path (test_cli_file_not_found).
- Coverage raised from 98% to 99% (263 statements, 3 remaining edge branches).

### Verified
- 37/37 pytest pass, 99% coverage, mypy --strict clean.
- No functional regression.


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
