## [Unreleased]

### Documented
- Independent full inspection cycle (2026-10-26): re-ran pytest (38/38 pass) and mypy --strict (clean). Updated AGENTS.md review note. No critical issues; public surface remains at v2.1.38-pro.

## [2.1.38-pro] - 2026-10-26

### Improved
- Extracted the approximate 95% CI z-score (previously magic 1.96) into the named constant CI_Z_SCORE.
- Improves code clarity and consistency with other named constants (PRIOR_STRENGTH, OPPOSITION_FACTOR, etc.).
- No change to numerical results, fingerprints, status decisions, or CLI behavior.

### Verified
- All 38 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior and public surface unchanged.
- Version aligned across version.py, pyproject.toml, and README.

## [2.1.37-pro] - 2026-10-26

### Fixed
- Restored the verified working `mfr_core_pro.py` after an intermediate push left a placeholder that broke CI and unit tests.
- Core logic matches the last known-good state (PRIOR_STRENGTH, OPPOSITION_FACTOR, INDEPENDENCE_FACTOR named constants retained).

### Verified
- All 38 unit tests pass.
- mypy --strict clean.
- Demo runs successfully.
- Version aligned across version.py, pyproject.toml, and README.

## [2.1.36-pro] - 2026-10-26

### Improved
- Extracted the fixed prior strength (previously magic 2.0) into the named constant PRIOR_STRENGTH.
- Improves code clarity, consistency with other named factors (INDEPENDENCE_FACTOR, OPPOSITION_FACTOR, MAX_EFFECTIVE_WEIGHT), and future maintainability.
- No change to numerical results, fingerprints, status decisions, or CLI behavior.

### Verified
- All 38 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior and public surface unchanged.
- Version aligned across version.py, pyproject.toml, and README.

## [2.1.35-pro] - 2026-10-26

### Improved
- Extracted the soft opposition residual weight (previously magic 0.5) into the named constant OPPOSITION_FACTOR.
- Improves code clarity, consistency with INDEPENDENCE_FACTOR / MAX_EFFECTIVE_WEIGHT, and future maintainability.
- No change to numerical results, fingerprints, status decisions, or CLI behavior.

### Verified
- All 38 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior and public surface unchanged.
- Version aligned across version.py, pyproject.toml, and README.

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
