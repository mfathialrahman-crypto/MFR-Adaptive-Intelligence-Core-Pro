## [2.1.22-pro] - 2026-10-23

### Improved
- Removed unused imports (`asdict`, `TypedDict`) from `mfr_core_pro.py` for cleaner code quality and maintainability.
  (Cleanup completed in follow-up commit after the initial claim.)
- Version aligned across version.py (2.1.22-pro), pyproject.toml (2.1.22), and README.

### Verified
- All 33 unit tests pass locally after the cleanup.
- No functional changes; fingerprints, analysis logic, CLI, and decision mapping preserved.

## [2.1.21-pro] - 2026-10-23

### Added
- `_generate_suggestions` now accepts and surfaces listed alternatives when present.
  Suggestion text includes the alternative claims so they are visible in the report.
- Regression test `test_suggestions_include_alternatives` verifies the behavior.

### Fixed
- Version alignment: version.py, pyproject.toml, and README now all report 2.1.21-pro / 2.1.21.
- Previous commit claimed the feature but only bumped version.py; implementation and test are now complete.

### Verified
- All 33 unit tests pass locally.
- Existing fingerprints and status logic for independent-only evidence unchanged.

# Changelog

## [2.1.19-pro] - 2026-10-23

### Fixed
- Unified independence penalty to a single constant `INDEPENDENCE_FACTOR = 0.6`.
  Previously `_strength()` used 0.7 while Beta updates used 0.6, causing inconsistent ranking of non-independent evidence during deduplication.
- Deduplication now uses the same factor as belief updating.

### Verified
- All existing unit tests pass.
- Fingerprints and analysis outputs for independent-only evidence remain unchanged.
- No regressions in status, confidence, or suggestion generation.

## [2.1.18-pro] - 2026-10-22

### Fixed
- Aligned public documentation (README badge and version text) with single source of truth `version.py` (2.1.18-pro) and packaging version (2.1.18).
- Prevents user-facing version drift on the competitive public surface.

### Verified
- All 31 unit tests continue to pass after documentation-only change.
- No functional code modified.

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
- Version aligned across code, packaging, and docs.

### Verified
- All 27 unit tests pass.
- Existing CLI, decision mapping, and fingerprint behavior preserved.

# Changelog

All notable changes to MFR Adaptive Intelligence Core Pro will be documented here.

## [2.1.14-pro] - 2026-10-19

### Fixed
- Restored complete `mfr_core_pro.py` implementation after accidental truncation to placeholder.
- Verified: 20/20 unit tests pass; strict mypy clean; CLI `--decision` and demo work.
- Aligned product VERSION constant with packaging version intent (2.1.14).

## [2.1.13-pro] - 2026-10-18

### Interoperability / CLI
- Added optional `--decision` flag that emits a FathiMind Decision contract (RFC-0001) instead of the raw analysis report.
- Non-breaking; default output remains the full analysis object.
- Restored full core implementation that was accidentally overwritten by a placeholder in the previous commit.
- All unit tests (19) and strict mypy continue to pass.

## [2.1.12-pro] - 2026-10-18

### Interoperability / Competitive
- Added `to_fathimind_decision(report)` that maps an analysis report to a FathiMind Decision schema-compatible object (RFC-0001).
- Status mapping: high-confidence provisional → stable; lower or conflicting → warning; insufficient → critical.
- Confidence is clamped to the shared contract bounds [0.3, 0.98].
- Evidence and anomalies are populated for replayability. Additive fields allowed.
- New unit tests cover strong, insufficient, and conflict cases.
- Fully backward compatible; existing analyze() output is unchanged.
