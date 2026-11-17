# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version marker is a public surface marker).

## [2.1.67+pro] - 2026-11-17

### Changed
- Deduplication now keys on `(source, claim)` instead of source alone, preserving multi-claim evidence from the same source.
- CLI `--json` accepts `-` or omitted path to read from stdin for better automation.

### Notes
- Analysis contract unchanged. Tests updated and pass. Version sources aligned.

## [2.1.66+pro] - 2026-11-17

### Fixed
- Version string changed from 2.1.66-pro to 2.1.66+pro to satisfy PEP 440. Editable installs and packaging now succeed. Tests updated accordingly.


### Fixed
- Restored full analysis implementation (fingerprint, validate_analysis_report, suggestions, decision_confidence, stability, audit trail) that had been accidentally replaced by a simplified placeholder in the previous "restore" commit. Tests now collect and pass again.

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
