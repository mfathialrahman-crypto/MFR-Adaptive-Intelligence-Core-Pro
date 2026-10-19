# Changelog

All notable changes to MFR Adaptive Intelligence Core Pro will be documented here.

## [2.1.15-pro] - 2026-10-19

### Improved
- Evidence JSON file loader now accepts an optional `notes` field and passes it through to the Evidence object.
- Fully backward compatible; existing evidence files continue to work.
- Version aligned across VERSION constant, pyproject.toml, and README.

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

## [2.1.11-pro] - 2026-10-17

### User experience / CLI
- Added `--evidence-file PATH` to load evidence from a JSON array of objects.
- Supports structured, repeatable input for automation and integration.
- Existing `--evidence` flag remains fully compatible.
- Added analysis report JSON schema under `schemas/analysis.schema.json` (documentation contract; no runtime dependency).

### Reliability
- CLI now accepts either flag-based or file-based evidence.
- All existing unit tests continue to pass.

## [2.1.10-pro] - 2026-10-17

### Code quality
- Extracted the conflict-detection threshold to a named constant `CONFLICT_THRESHOLD = 0.18`.
- Documented the rationale in source. Behavior is unchanged.
- All unit tests continue to pass.

## [2.1.9-pro] - 2026-10-17

### Code quality / typing
- Strengthened static typing throughout the core module.
- Introduced `ClaimResult` TypedDict for analysis claim records.
- Added explicit return type and parameter types to satisfy strict mypy.
- All unit tests continue to pass; behavior is unchanged.
- Ready for optional type-checking in CI.

## [2.1.8-pro] - 2026-10-17

### User experience / CLI completeness
- Added optional `--alternatives` flag to CLI (repeatable) to record competing hypotheses for context.
- Alternatives are stored in the analysis record; core evidence analysis remains unchanged.
- Fully backward compatible.

## [2.1.7-pro] - 2026-10-16

### Documentation
- README now explicitly references `AGENTS.md` as the governing Project Engineering Constitution.

### User experience / CLI completeness
- CLI `--evidence` now accepts optional WEIGHT and INDEPENDENT flags after reliability.
- Format: `--evidence CLAIM SOURCE RELIABILITY [WEIGHT] [true|false]`
- Existing 3-argument usage remains fully compatible.
- Improved error messages for malformed evidence arguments.

## [2.1.6-pro] - 2026-10-16

### Reliability / CI
- Fixed CLI so `python mfr_core_pro.py` (no arguments) runs the built-in demo, matching README and CI workflow expectations.
- Made `question` positional argument optional; error only when evidence is supplied without a question.
- CI demo step now succeeds on all Python versions in the matrix.

## [2.1.5-pro] - 2026-10-16

### Reliability
- Extended CI matrix to Python 3.13 (in addition to 3.10–3.12). Pure stdlib; no behavior change.

## [2.1.4-pro] - 2026-10-13

### Developer & user experience
- Added minimal CLI (`python mfr_core_pro.py "question" --evidence ...`) for quick analysis without writing code.
- `--demo` flag and `--prior` support.
- Existing demo and library API unchanged.

## [2.1.3-pro] - 2026-10-13

### Bayesian prior correctness
- `prior_belief` is now actually used: mapped to a weak Beta prior (concentration ≈ 2).
- Validation rejects prior_belief outside [0, 1].
- Audit trail records the prior parameters used.
- Added tests confirming prior influence and rejection of invalid priors.

## [2.1.2-pro] - 2026-10-13

### Reliability & quality improvements
- Fingerprint is now truly content-addressable: excludes record_id, created_at, version, and other volatile fields so identical evidence produces identical fingerprints across instances.
- Added unit test verifying cross-instance stability.
- All previous tests continue to pass.
