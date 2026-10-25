## [2.1.30-pro] - 2026-10-25

### Improved
- Added `--compact` CLI flag for single-line JSON output, improving scriptability and pipeline use.
- Version aligned across version.py, pyproject.toml, and README.

### Verified
- All existing unit tests pass.
- New compact output produces valid JSON without whitespace.
- No change to analysis logic or default pretty-print behavior.

## [2.1.29-pro] - 2026-10-24

### Improved
- Added regression tests covering remaining suggestion-generation branches:
  coherent large-sample default message, single-source confirmation prompt,
  non-independent + small-sample combination, and alternatives listing.
- Added CLI tests for `--decision` contract emission and out-of-range `--prior`.
  Raises measured confidence in public contract and CLI reliability without changing analysis behavior.

### Verified
- All 34 unit tests pass.
- mypy --strict remains clean.
- Existing analysis, fingerprints, status logic, and other CLI behavior unchanged.
- Version aligned across version.py, pyproject.toml, and README.
