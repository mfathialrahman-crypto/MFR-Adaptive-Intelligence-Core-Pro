## [2.1.31-pro] - 2026-10-25

### Improved
- Added unit tests covering the built-in demo() path and validate_report missing-field edge cases.
- Raises measured coverage of public demo and contract checker without altering analysis or CLI behavior.

### Verified
- All 39 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior, fingerprints, status logic, and CLI unchanged.
- Version aligned across version.py, pyproject.toml, and README.

## [2.1.30-pro] - 2026-10-25

### Improved
- Expanded unit tests for the FathiMind decision contract mapping (`to_fathimind_decision`):
  explicit coverage of INSUFFICIENT_EVIDENCE → critical + anomaly,
  CONFLICTING_EVIDENCE → warning + anomaly, and low-confidence provisional paths.
- Raises measured confidence in the public contract surface without altering analysis logic.

### Verified
- All 37 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior, fingerprints, status logic, and CLI unchanged.
- Version aligned across version.py, pyproject.toml, and README.
