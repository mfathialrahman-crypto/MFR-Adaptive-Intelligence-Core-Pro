## [2.1.18-pro] - 2026-10-23

### Improved (Reliability)
- Unified independence down-weighting to a single constant INDEPENDENCE_FACTOR = 0.6 (previously 0.7 in dedup strength vs 0.6 in Bayesian update).
- Suggestions now surface listed alternatives when provided, improving actionability.
- Removed unused imports (asdict, TypedDict).

### Verified
- All unit tests pass including new regressions for factor consistency and alternatives-aware suggestions.
- Existing analysis behavior, fingerprints for identical inputs, CLI, and decision mapping preserved.
- Version remains aligned: version.py 2.1.18-pro, pyproject.toml 2.1.18.

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
