## [2.1.34-pro] - 2026-10-25

### Improved
- Optimized multi-claim opposition calculation from O(n²) nested summation to O(n) via precomputed effective weights.
- No change to numerical results, fingerprints, or status decisions; improves scalability for larger evidence sets while keeping the soft-opposition model.

### Verified
- All 38 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior and CLI unchanged.
- Version aligned.

## [2.1.33-pro] - 2026-10-25

### Fixed
- CLI `--evidence` parsing now catches invalid weight (and other conversion) values and exits cleanly with code 2 instead of raising an uncaught ValueError traceback.
- Improves reliability of the public CLI surface for malformed input.

### Added
- Regression test confirming invalid weight produces exit code 2 with no traceback.

### Verified
- All 38 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior, fingerprints, and valid CLI paths unchanged.
- Version aligned across version.py, pyproject.toml, and README.

## [2.1.32-pro] - 2026-10-25

### Improved
- Added CI job `version-consistency` that fails the build if the base version in `version.py` does not match `pyproject.toml`.
- Prevents public-surface version drift that previously required manual alignment commits.

### Verified
- Existing 37 unit tests continue to pass locally.
- mypy --strict remains clean.
- No change to analysis behavior, fingerprints, or CLI.

## [2.1.31-pro] - 2026-10-25

### Improved
- Added unit tests covering the built-in demo() path and validate_report missing-field edge cases.
- Raises measured coverage of public demo and contract checker without altering analysis or CLI behavior.
- Aligned README version badge and text to match version.py / pyproject.toml (was lagging at 2.1.30-pro).

### Verified
- All 37 unit tests pass.
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
