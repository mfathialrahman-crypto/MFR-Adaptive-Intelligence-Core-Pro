# Changelog

## [2.1.44-pro] - 2026-10-29

### Fixed
- Restored public surface: replaced PLACEHOLDER files with working README, pyproject.toml, unit tests, and CLI demo.
- Added `main()` entry point so `python mfr_core_pro.py` produces a demonstrable analysis report.
- Aligned version between version.py and pyproject.toml.

### Added
- Comprehensive unit tests covering validation, insufficient evidence, provisional findings, conflicts, fingerprint determinism, and evidence limits.
- CLI support for `--evidence-file` JSON input and built-in `--demo`.

All analysis logic, fingerprints, and numerical results remain unchanged from the previous functional core.
