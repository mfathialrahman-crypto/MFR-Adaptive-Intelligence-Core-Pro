# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [2.1.59-pro] - 2026-11-10

### Fixed
- Strict mypy compliance: introduced `ClaimStat` TypedDict for claim statistics, resolved all type errors under `mypy --strict`. Fingerprint helper now type-safe. No behavioral change.

### Notes
- Type safety improvement aligns public surface claim of clean strict typing. All 39 tests continue to pass. Version sources (version.py, pyproject.toml, README) aligned.

## [2.1.56-pro] - 2026-11-09

### Fixed
- `competing_claims` previously included the top claim itself (semantic bug in report contract). It now correctly excludes the top claim and returns the next up to 3 competitors (`claim_stats[1:4]`). Single-claim analyses now correctly yield an empty competitors list.

### Added
- Regression test `test_competing_claims_excludes_top` covering multi-claim and single-claim cases.
- Strengthened `test_conflicting_evidence_detected` to assert top claim is never present in `competing_claims`.

### Notes
- Pure correctness fix; Bayesian math, fingerprints, and decision-contract fields unchanged. Backward-compatible for consumers that already treated competitors as the remainder of ranked claims.

## [Unreleased]

### Added
- Zero-dependency CLI (`python mfr_core_pro.py --json record.json`) and `analyze_json()` helper for easy programmatic and script use. Improves public package usability while preserving zero-deps and determinism.
- Edge-case tests for zero-reliability evidence and CLI/JSON path.

### Changed
- Version bumped to 2.1.54-pro. All version sources aligned.

## [2.1.53-pro] - 2026-11-09

### Notes
- Previous cycle confirmed stable.

## [Unreleased]

### Fixed
- Restored complete `mfr_core_pro.py` after accidental placeholder overwrite on main. Core Bayesian analysis, validation, fingerprinting, and decision-contract fields are fully operational again.

### Added
- JSON serialization (`to_dict` / `from_dict` / `to_json` / `from_json`) on `Evidence` and `IntelligenceRecord`. Zero-dependency persistence and replay of decision inputs. Round-trip preserves analysis fingerprints. New regression test.

### Changed
- Version remains 2.1.53-pro (already aligned in version.py and pyproject.toml). README badge and text updated to match.

### Documented
- Independent verification (2026-11-09T08:20+04): Local clone, restored core, pytest 36/36 passed, mypy --strict clean. AGENTS.md stamp refreshed. No P0/P1 remaining. Continuous cycle active.

## [2.1.52-pro] - 2026-11-08

### Added
- Pure-Python `validate_analysis_report(report)` helper. Returns list of contract violations (empty if valid). Strengthens reliability verification without external dependencies. Covers required fields, status enum, confidence clamps, stability, fingerprint length, and list types.
- Unit tests confirming every `analyze()` path produces a report that passes the validator, plus basic rejection cases.

### Changed
- Version bumped to 2.1.52-pro. Schema documentation updated to note decision-contract fields are always present.

### Documented
- Independent verification cycle (2026-11-08T21:20+04): Local clone, pytest 33/33 passed, coverage 98%+, mypy --strict clean. AGENTS.md stamp refreshed. Validator implemented to close CHANGELOG/code gap. No P0/P1 issues. Continuous improvement active.

## [2.1.51-pro] - 2026-11-08

### Added
- Pure-Python `validate_analysis_report(report)` helper. Returns list of contract violations (empty if valid). Strengthens reliability verification without external dependencies. Covers required fields, status enum, confidence clamps, stability, fingerprint length, and list types.
- Unit test confirming every `analyze()` path produces a report that passes the validator, plus basic rejection cases.

### Changed
- Version bumped to 2.1.51-pro. Schema documentation updated to note decision-contract fields are always present.

### Documented
- Independent verification cycle (2026-11-08T14:20+04): Local clone, pytest 32/32 passed, coverage 98%, mypy --strict clean. AGENTS.md stamp refreshed. No P0/P1 issues. Continuous improvement active.

## [2.1.50-pro] - 2026-11-07

### Fixed
- Version consistency CI job now correctly compares full VERSION strings from version.py and pyproject.toml using reliable extraction (previously split base incorrectly and had fragile sed escaping, causing false mismatch).

### Added
- Unit test `test_version_aligned_with_pyproject` that parses pyproject.toml and asserts equality with VERSION. Prevents regression of the alignment gate.

### Documented
- Independent verification: local clone pytest 31/31 passed, coverage 98%, mypy --strict clean. AGENTS.md refreshed.

## [2.1.49-pro] - 2026-11-06

### Changed
- Fingerprint now includes the alternatives list (normalized and sorted) so that inputs affecting suggestions and the full report contract are content-addressable. Empty/whitespace alternatives are ignored consistently with construction cleaning.

### Added
- Regression test confirming alternatives change the fingerprint and that order/whitespace is normalized.

### Documented
- Independent verification: local clone pytest 30/30 passed after change.

## [2.1.48-pro] - 2026-11-06

### Added
- Bounds on `alternatives` list: max 50 items and max 200 characters per alternative (with empty/whitespace stripping). Consistent reliability / DoS hardening with claim/source/question bounds.
- Unit test covering alternatives length and count validation (29 total tests).

### Documented
- Independent verification cycle (2026-11-06): local clone pytest 29/29 passed, demo OK, version aligned. Continuous improvement cycle.

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

###
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
