# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [Unreleased]
### Documented
- Independent verification cycle (2026-11-05T23:14+04): fresh local clone pytest 28/28 passed in 0.06s, coverage 98% on mfr_core_pro.py (191 stmts, 4 miss), mypy --strict clean. AGENTS.md review timestamp refreshed. No P0/P1 issues. All core functionality verified.

### Documented
- Independent verification cycle (2026-11-05T12:19+04): local clone pytest 28/28 passed in 0.06s, coverage 98% (191 stmts, 4 miss), mypy --strict clean. AGENTS.md review timestamp refreshed and confirmed saved in GitHub. No P0/P1 issues.

### Documented
- Independent verification cycle (2026-11-05T06:15+04): local clone pytest 28/28 passed in 0.10s, coverage 98% (191 stmts, 4 miss), mypy --strict clean. AGENTS.md review timestamp refreshed and confirmed saved in GitHub. No P0/P1 issues.
- Independent verification cycle (2026-11-05T02:17+04): fresh local clone pytest 28/28 passed in 0.05s, coverage 98% (191 stmts, 4 miss), mypy --strict clean. AGENTS.md review timestamp refreshed and confirmed saved in GitHub. No P0/P1 issues.

### Added
- Re-enforced MAX_EVIDENCE_ITEMS bound inside IntelligenceRecord.analyze() to protect against post-construction mutation of the evidence list (reliability / DoS hardening).
- Unit test for the analyze-time evidence limit.

### Documented
- Independent verification cycle (2026-11-04T17:22+04): local clone pytest 28/28 passed (after new test), 98% coverage, mypy --strict clean. AGENTS.md review timestamp refreshed and confirmed saved in GitHub.
- Independent verification cycle (2026-11-04T15:16+04): local clone pytest 27/27 passed, 98% coverage, mypy --strict clean. AGENTS.md review timestamp refreshed and confirmed saved in GitHub.
- Independent verification cycle (2026-11-04T13:17+04): pytest 27/27 passed, 98% coverage, mypy --strict clean. AGENTS.md review timestamp refreshed and saved.

## [2.1.47-pro] - 2026-11-03

### Added
- String length bound on IntelligenceRecord.question (max 1000) for consistency with claim/source bounds and basic DoS/memory hardening.
- Unit tests for the new question length validation (27 total tests).

### Changed
- AGENTS.md last-reviewed stamp refreshed after local verification (27/27 pytest passed, ~98% coverage, mypy --strict clean).
- Aligned public version references (README, pyproject.toml, version.py).

## [2.1.46-pro] - 2026-11-02

### Added
- String length bounds on Evidence claim (max 500) and source (max 200) for reliability and basic DoS hardening.
- Unit tests covering the new length validation (25 total tests).

### Changed
- AGENTS.md last-reviewed stamp refreshed after local verification (25/25 pytest passed, coverage still ~98%, mypy --strict clean).

### Added
- Strengthened `test_ci_non_overlap_signal_when_present` to deterministically trigger non-overlapping 95% CIs and assert the stronger-separation audit and suggestion. Coverage raised from 96% to 98%.

### Changed
- AGENTS.md last-reviewed stamp refreshed after independent local verification (22/22 pytest passed, 98% coverage, mypy --strict clean).


### Documented
- Independent verification cycle (2026-11-01T12:18Z): Fresh local clone, pytest 20/20 passed, coverage 91%, mypy --strict clean. AGENTS.md constitution review timestamp refreshed. No critical P0/P1 issues. Continuous improvement active.

### Added
- Unit test for empty/whitespace source validation on Evidence (raises ValueError). Improves coverage of input contract.

### Changed
- Refreshed AGENTS.md verification stamp after fresh local clone verification (pytest 20/20 passed, coverage 91%, mypy --strict clean). No behavioral changes.
- Refreshed AGENTS.md review timestamp after local verification (pytest 19/19 passed, mypy --strict clean, coverage ~91% on core). No behavioral changes.
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
