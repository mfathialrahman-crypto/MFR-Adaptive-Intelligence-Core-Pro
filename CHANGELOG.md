## [2.1.18-pro] - 2026-10-22

### Improved
- Configurable prior_strength (default 2.0) on IntelligenceRecord for stronger or weaker prior influence.
- Fingerprint now includes prior_strength for full content addressability.
- Input validation rejects non-positive prior_strength.

### Verified
- Existing default behavior unchanged (prior_strength=2.0).
- All previous tests pass; new regression for configurable prior added.

## [2.1.17-pro] - 2026-10-22

### Improved
- Reject empty or whitespace-only questions at IntelligenceRecord construction (ValueError).
- Strengthens input validation for reliability and prevents silent low-quality analyses.
- Version aligned across version.py, pyproject.toml, and README.

### Verified
- All unit tests pass including new empty-question regression.
- Existing analysis, CLI, fingerprint, and decision mapping behavior preserved.

## [2.1.16-pro] - 2026-10-22

### Fixed (Critical)
- Restored full implementation of `mfr_core_pro.py` after accidental truncation to a stub. Core Bayesian analysis, Evidence validation, IntelligenceRecord.analyze(), fingerprinting, decision mapping, CLI, and demo are fully operational again.
- Insufficient-evidence reports include content-addressable fingerprint and original question.
- All analysis outputs satisfy analysis.schema.json required fields.
- validate_report() contract checker present.

### Verified
- All 30 unit tests pass.
- Strict mypy passes.
- CLI, decision mapping, and fingerprint stability confirmed.

## [2.1.15-pro] - 2026-10-21

### Improved
- Added regression tests for suggestion generation on small samples, conflicting evidence, and non-independent sources.
- Added direct unit test for the built-in demo() path.
- Raised measured logical coverage of core analysis paths.
