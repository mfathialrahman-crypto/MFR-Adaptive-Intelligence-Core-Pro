## [Unreleased]

### Fixed
- Aligned pyproject.toml project version to exactly match version.py (2.1.38-pro). Previously missing the -pro local identifier.

### Verified
- pytest 38/38 passed after the alignment.
- No change to runtime behavior or fingerprints.

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
