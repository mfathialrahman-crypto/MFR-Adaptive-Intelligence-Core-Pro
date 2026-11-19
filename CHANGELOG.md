# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version marker is a public surface marker).

## [2.1.67+pro] - 2026-11-19

### Fixed
- `IntelligenceRecord.from_json` now raises clear `ValueError` (with index) for incomplete or invalid evidence items and non-numeric `prior_belief`, instead of raw `TypeError`.

### Added
- Four regression tests covering incomplete evidence fields, non-object evidence items, bad prior type, and reliability out-of-range via JSON path.

### Notes
- Verified locally: 33/33 pytest passed. Analysis logic unchanged. Version sources aligned at 2.1.67+pro.

## [2.1.66+pro] - 2026-11-19

### Added
- Edge-case unit tests for Evidence and IntelligenceRecord validation (long source/question/alternative, max evidence count, max alternatives, independence penalty path). Coverage raised to 93%.

### Notes
- Verified locally: 29/29 pytest passed, coverage 93% (≥90%), mypy --strict clean. No functional changes to analysis logic. Version sources remain aligned.

## [2.1.66+pro] - 2026-11-17

### Fixed
- Version string changed from 2.1.66-pro to 2.1.66+pro to satisfy PEP 440. Editable installs and packaging now succeed. Tests updated accordingly.

### Fixed
- Restored full analysis implementation (fingerprint, validate_analysis_report, suggestions, decision_confidence, stability, audit trail) that had been accidentally replaced by a simplified placeholder in the previous "restore" commit. Tests now collect and pass again.

### Changed
- CI type-check job now runs mypy --strict on both mfr_core_pro.py and version.py.
- AGENTS.md review footer refreshed after local verification (53/53 pytest, 92% coverage, mypy clean).

### Notes
- Critical regression fixed. 53/53 pytest passed, coverage 92% (≥90%), mypy --strict clean. Version sources aligned.

## [2.1.65-pro] - 2026-11-17

### Changed
- CLI --help output now lists both the installed `mfr-core` command and the direct `python mfr_core_pro.py` form, with cleaner formatting.

### Notes
- No change to analysis logic. 53 tests continue to pass. mypy --strict clean. Continuous improvement cycle active.

## [2.1.64-pro] - 2026-11-16

### Added
- Initial public release surface with Bayesian evidence core, full audit trail, and deterministic fingerprint.

## 2026-11-18
- tests: added CLI error-path coverage for --json (missing file, no arg, invalid content). Suite now 56 tests; coverage on core raised to 98%.
- docs: refreshed AGENTS.md verification stamp after local confirmation.
