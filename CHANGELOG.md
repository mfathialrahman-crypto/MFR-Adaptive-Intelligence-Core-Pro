# Changelog

## [2.1.75+pro] - 2026-11-24

### Added
- Regression tests for from_json evidence TypeError/ValueError paths, CLI PermissionError, and coherent suggestion trigger.
- Coverage improved for error-handling edges.

### Notes
- Verified locally: 52/52 pytest passed, coverage 98% (≥90%), mypy --strict clean. Versions aligned at 2.1.75+pro.

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version marker is a public surface marker).

## [2.1.74+pro] - 2026-11-23

### Added
- CLI: `--json` now accepts `-` or omitted file to read the record from stdin (better scripting UX).
- Switched CLI to argparse for clearer help and option handling.

### Notes
- Verified locally: 48/48 pytest passed, coverage ≥90%, mypy --strict clean. Versions aligned at 2.1.74+pro.

## [2.1.73+pro] - 2026-11-22

### Added
- `sample_record.json` example for one-command CLI demo (`python mfr_core_pro.py --json sample_record.json`).
- README quick example pointing to the sample.

### Fixed
- Status decision: weak top claim (mean < 0.55, evidence_count < 2) now correctly yields `INSUFFICIENT_EVIDENCE` instead of being overwritten to `PROVISIONAL_FINDING` by the single-evidence rule. The single-weak-source provisional path is preserved only when status was still provisional.

### Notes
- Verified locally: 47/47 pytest passed, coverage 99% (≥90%), mypy --strict clean. Version sources aligned at 2.1.73+pro. AGENTS.md constitution refreshed with verification stamp (updated 2026-11-23 01:17 +04 after independent local re-verification).

## [2.1.72+pro] - 2026-11-21

### Added
- Additional regression tests for low-mean insufficient path, conflicting suggestions exercise, unstable stability confirmation, and CLI PermissionError path.

### Notes
- Analysis logic for status assignment refined in 2.1.73+pro.

## [2.1.71+pro] - 2026-11-21

### Added
- Additional regression tests covering from_json invalid evidence fields, high-confidence coherent analysis, CLI invalid JSON content, and fingerprint type guard.

## [2.1.68+pro] - 2026-11-20

### Fixed
- Confidence interval calculation now uses pure Beta posterior standard deviation (no double-counting of sample size).

## [2.1.64-pro] - 2026-11-16

### Added
- Initial public release surface with Bayesian evidence core, full audit trail, and deterministic fingerprint.
