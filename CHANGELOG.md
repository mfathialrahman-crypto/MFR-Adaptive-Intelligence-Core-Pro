# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [2.1.44-pro] - 2026-10-29

### Fixed
- Restored complete public surface: proper `README.md`, `pyproject.toml`, `CHANGELOG.md`, and comprehensive unit tests (`test_mfr_core_pro.py`).
- Aligned package metadata with `version.py` (base version 2.1.44) so CI version-consistency check passes.
- Ensured zero-dependency core remains installable and testable via standard Python tooling.

### Added
- Regression test for prior_belief out-of-range rejection (now 17 unit tests).
- Full unit test coverage for Evidence validation, insufficient evidence, provisional findings, conflicting evidence, independence penalties, fingerprint determinism, and CI non-overlap signals.
- Minimal demo entry point under `if __name__ == "__main__"` for the Actions demo step.

### Notes
- Core analysis logic (`mfr_core_pro.py`) unchanged in behavior; only packaging, documentation, and verification restored.
- CI matrix (Python 3.10–3.13) now expected to pass with real tests.

## Earlier
- Initial transparent Bayesian evidence core with audit trail, Beta prior updates, independence penalty, and confidence intervals.
