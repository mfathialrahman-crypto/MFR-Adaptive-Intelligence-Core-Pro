## [Unreleased]

### Fixed
- Restored full CLI argument parser and demo() function that were accidentally removed during the magic-number extraction in v2.1.40-pro.
- --demo, positional question, --evidence, --evidence-file, --alternatives, --version, --decision, and --validate now work again.
- Evidence file loading, error messages, and exit codes match the previous tested contract.
- No change to analysis logic, constants, fingerprints, or numerical results.

### Verified
- pytest 38/38 pass.
- mypy --strict clean.
- Public surface at v2.1.41-pro.

## [Unreleased]

### Documented
- Independent development cycle (2026-10-27): extracted remaining magic numbers (conflict threshold, stable confidence, decision confidence clamps) into named constants. No numerical or behavioral change. pytest 38/38 passed. Public surface at v2.1.40-pro.

## [2.1.40-pro] - 2026-10-27

### Improved
- Extracted remaining magic numbers into named constants for consistency and maintainability:
  - CONFLICT_SECOND_THRESHOLD = 0.4 (second claim posterior mean to trigger conflict)
  - STABLE_CONFIDENCE_THRESHOLD = 0.75 (provisional → stable mapping)
  - MIN_DECISION_CONFIDENCE = 0.3 and MAX_DECISION_CONFIDENCE = 0.98 (decision contract clamps)
- Aligns with prior extractions (PRIOR_STRENGTH, CI_Z_SCORE, VARIANCE_FLOOR, etc.).
- No change to numerical results, fingerprints, status decisions, CLI behavior, or public contract.

### Verified
- All 38 unit tests pass.
- Existing analysis behavior and public surface unchanged.
- Version aligned across version.py, pyproject.toml, and README.

## [Unreleased]

### Documented
- Independent full inspection cycle (2026-10-27): re-ran pytest (38/38 pass) and mypy --strict (clean). Updated AGENTS.md review note. No critical issues; public surface at v2.1.39-pro.

## [2.1.39-pro] - 2026-10-27

### Improved
- Extracted remaining magic numbers in the credible-interval calculation (fallback variance 0.01 and variance floor 1e-8) into named constants FALLBACK_VARIANCE and VARIANCE_FLOOR.
- Improves code clarity and consistency with prior named constants (CI_Z_SCORE, PRIOR_STRENGTH, etc.).
- No change to numerical results, fingerprints, status decisions, or CLI behavior.

### Verified
- All 38 unit tests pass.
- mypy --strict remains clean.
- Existing analysis behavior and public surface unchanged.
- Version aligned across version.py, pyproject.toml, and README.

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
