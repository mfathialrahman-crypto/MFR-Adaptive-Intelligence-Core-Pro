# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [Unreleased]

## [2.1.46-pro] - 2026-10-31

### Added
- Fail-fast length bounds on untrusted input: claim ≤ 500, source ≤ 200, question ≤ 1000 characters.
- Explicit unit tests for the CI non-overlap suggestion and audit path.

### Security
- Hardened against memory amplification from oversized claim/source/question strings (DoS surface reduction). Existing MAX_EVIDENCE_ITEMS remains in force.

### Notes
- Bayesian update math unchanged. Length checks are additive and fail closed.

### Changed
- Updated AGENTS.md review timestamp after full local verification cycle (pytest 19/19, mypy --strict clean). No behavioral changes to core logic.
- Synced AGENTS.md Project Engineering Constitution with HQ: cleaned formatting, confirmed long-horizon section, updated review timestamp (2026-10-31 cycle). No behavioral changes to core logic.

## [2.1.45-pro] - 2026-10-30

### Added
- Decision-contract fields on every analysis report: `decision_confidence` (clamped) and `stability` (`stable` | `provisional` | `unstable`).
- Fail-fast validation of `prior_belief` in `IntelligenceRecord.__post_init__` (previously only checked inside `analyze`).
- Unit tests covering construction-time prior validation and the new decision-contract fields.

### Fixed
- Removed unused imports (`argparse`, `sys`).
- Activated previously defined but unused constants (`MIN_DECISION_CONFIDENCE`, `MAX_DECISION_CONFIDENCE`, `STABLE_CONFIDENCE_THRESHOLD`).
- Implemented the decision-contract fields and construction-time prior validation that were documented but missing from the analysis path. Constants are now used. Tests expanded (19 total).

### Notes
- Bayesian core math unchanged. New fields are additive and backward-compatible (schema already allowed additionalProperties).
- Schema updated to document `decision_confidence` and `stability`.

## [2.1.44-pro] - 2026-10-29

### Fixed
- Restored complete public surface: proper `README.md`, `pyproject.toml`, `CHANGELOG.md`, and comprehensive unit tests (`test_mfr_core_pro.py`).
- Aligned package metadata with `version.py` (base version 2.1.44) so CI version-consistency check passes.
- Ensured zero-dependency core remains installable and testable via standard Python tooling.

### Added
- Full unit test coverage for Evidence validation, insufficient evidence, provisional findings, conflicting evidence, independence penalties, fingerprint determinism, and CI non-overlap signals.
- Minimal demo entry point under `if __name__ == "__main__"` for the Actions demo step.

### Notes
- Core analysis logic (`mfr_core_pro.py`) unchanged in behavior; only packaging, documentation, and verification restored.
- CI matrix (Python 3.10–3.13) now expected to pass with real tests.

## Earlier
- Initial transparent Bayesian evidence core with audit trail, Beta prior updates, independence penalty, and confidence intervals.
