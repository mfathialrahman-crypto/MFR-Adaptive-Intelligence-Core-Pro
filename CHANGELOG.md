# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version marker is a public surface marker).

## [2.1.74+pro] - 2026-11-22

### Added
- MAX_JSON_SIZE (1 MiB) guard in IntelligenceRecord.from_json to reject oversized untrusted JSON input, improving reliability against large payloads.
- Regression test for the size limit.

### Notes
- Verified locally: 48/48 pytest passed, mypy --strict clean. Versions aligned.

## [2.1.73+pro] - 2026-11-21

### Fixed
- Status decision: weak top claim (mean < 0.55, evidence_count < 2) now correctly yields `INSUFFICIENT_EVIDENCE` instead of being overwritten to `PROVISIONAL_FINDING` by the single-evidence rule. The single-weak-source provisional path is preserved only when status was still provisional.

### Added
- Regression coverage for the corrected insufficient path (verified locally 43/43, coverage 99%).

### Notes
- Verified locally: 43/43 pytest passed, coverage 99% (≥90%), mypy --strict clean. Version sources aligned at 2.1.73+pro. Core restored and pushed after accidental placeholder write.

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
