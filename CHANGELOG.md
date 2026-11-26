# Changelog

## [2.1.77+pro] - 2026-11-26

### Fixed
- Restored complete AGENTS.md Project Engineering Constitution (was placeholder).
- Expanded test suite with regression coverage for analysis paths (deduplication, conflict, insufficient evidence, suggestions, stability), fingerprint determinism, from_json round-trip, validate_analysis_report, and CLI (version, --json file/stdin, error paths).
- Coverage restored to ≥90% (verified 91% locally) so the CI gate passes again.

### Improved
- Added hard size limit (1 MiB) on JSON input in `IntelligenceRecord.from_json` and CLI `--json` to bound memory use and improve reliability against oversized payloads.
- Expanded regression tests to 26 cases covering evidence count limit, JSON root type, prior type, invalid evidence fields, size limit, stable status + CI non-overlap, and CLI size/permission edges.
- Local verification: 26 passed, 93% coverage.

### Verified
- 26 tests pass.
- No functional change to valid analysis behavior.
- Version alignment (version.py == pyproject.toml) preserved.
