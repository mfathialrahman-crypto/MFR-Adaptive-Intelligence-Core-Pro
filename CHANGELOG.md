# Changelog

## [2.1.77+pro] - 2026-11-26

### Fixed
- Restored complete AGENTS.md Project Engineering Constitution (was placeholder).
- Expanded test suite with regression coverage for analysis paths (deduplication, conflict, insufficient evidence, suggestions, stability), fingerprint determinism, from_json round-trip, validate_analysis_report, and CLI (version, --json file/stdin, error paths).
- Coverage restored to ≥90% (verified 91% locally) so the CI gate passes again.

### Verified
- 18 tests pass.
- No functional change to valid analysis behavior.
- Version alignment (version.py == pyproject.toml) preserved.
