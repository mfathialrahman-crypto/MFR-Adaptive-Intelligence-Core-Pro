# Changelog

## [2.1.80+pro] - 2026-11-27

### Fixed
- CI separation messaging is now accurate: non-overlap message only when 95% CIs do not overlap; separate message for strong mean separation. No change to analysis results or decision fields.

### Verified
- 30 tests pass. Coverage ≥90%. mypy --strict clean. Version sources aligned.

## [2.1.79+pro] - 2026-11-27

### Added
- Expanded regression tests (30 total) covering prior_belief type, evidence field validation, CI non-overlap, stable status, and demo path.
- Coverage raised to 96%.

### Changed
- AGENTS.md cycle note updated.

## [2.1.78+pro] - 2026-11-26

### Added
- CLI `--validate` flag: after `--json` analysis, runs pure-Python contract validation and exits 2 on violations. Strengthens public reproducibility of the decision-contract fields without changing analysis results.

### Verified
- 23 tests pass. Coverage ≥90%. mypy --strict clean. No functional change to valid analysis paths.

## [2.1.77+pro] - 2026-11-26

### Fixed
- Restored complete AGENTS.md Project Engineering Constitution (was placeholder).
- Expanded test suite with regression coverage for analysis paths (deduplication, conflict, insufficient evidence, suggestions, stability), fingerprint determinism, from_json round-trip, validate_analysis_report, and CLI (version, --json file/stdin, error paths).
- Coverage restored to ≥90% (verified 91% locally) so the CI gate passes again.

### Verified
- 18 tests pass.
- No functional change to valid analysis behavior.
- Version alignment (version.py == pyproject.toml) preserved.
