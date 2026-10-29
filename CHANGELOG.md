## [2.1.44-pro] - 2026-10-29

### Added
- Hard limit of 4096 characters on claim, source, question, and alternative strings (`MAX_STRING_LENGTH`). Oversized inputs raise `ValueError`. Further bounds memory for reliability and basic DoS resistance. Regression tests included.

### Changed
- Version bump to 2.1.44-pro. AGENTS.md review timestamp refreshed.

## [2.1.43-pro] - 2026-10-29

### Added
- Hard limit of 1000 evidence items per analysis (`MAX_EVIDENCE_ITEMS`). Oversized inputs raise `ValueError` before processing. Bounds memory and CPU for reliability and basic DoS resistance. Regression test included.

### Changed
- Version bump to 2.1.43-pro. AGENTS.md review timestamp refreshed after independent verification cycle.

## [Unreleased]
### Documented
- Independent verification cycle (2026-10-28 22:15Z): confirmed AGENTS.md constitution present and saved on GitHub. Local verification: pytest 43/43 pass, coverage 68% on mfr_core_pro.py. CI green. No functional changes. Public surface at v2.1.42-pro.

### Documented
- Independent full inspection cycle (2026-10-28 21:16Z): confirmed AGENTS.md constitution present and saved on GitHub. Local verification: pytest 43/43 pass, coverage ~68% on mfr_core_pro.py. CI green on recent runs. No functional changes. Public surface at v2.1.42-pro.

### Improved
- CLI `--prior` handling is now explicit: default is `None` so that an explicit `--prior` always overrides any `prior_belief` present in an evidence file, and the fallback to 0.5 is unambiguous when neither is supplied. Previous logic relied on the default value 0.5 being distinguishable, which was fragile.
- Added two regression tests covering CLI-override and default-prior cases. pytest 43/43 pass.

### Documented
- Independent verification cycle (2026-10-28 16:15Z): confirmed pytest 43/43 pass after prior-handling improvement. Updated AGENTS.md review timestamp. Public surface at v2.1.42-pro.

## [2.1.42-pro] - 2026-10-27

### Fixed
- `--evidence-file` now accepts the documented object format from README (with `question`, `evidence`, optional `prior_belief` and `alternatives`) in addition to a bare JSON array.
- CLI prefers explicit command-line values, then falls back to values present in the evidence file.
- Added regression test covering the object format.

### Verified
- pytest 41/41 pass (independent local run 2026-10-27).
- Coverage ~68% on mfr_core_pro.py (CLI main covered via subprocess, not counted).
- mypy --strict clean.
- No change to analysis logic, fingerprints, or numerical results when using array format.
- Version aligned across version.py, pyproject.toml, and README.
- Documentation updated to match measured test count and coverage.

## [Unreleased]
### Documented
- Independent verification cycle (2026-10-28): confirmed pytest 41/41 pass and measured coverage ~68% on mfr_core_pro.py. Updated AGENTS.md last-reviewed footer on Core Pro and FathiMind HQ. No functional changes. Public surface at v2.1.42-pro.

### Improved
- Added direct unit test for `demo()` function to raise measured coverage from ~66% to ~68% (CLI main still covered via subprocess). pytest 41/41 pass.

### Documented
- Independent verification cycle (2026-10-27): confirmed pytest 41/41 pass and measured coverage ~68% on mfr_core_pro.py. Updated README test count and coverage figure. No functional changes. Public surface at v2.1.42-pro.

### Fixed
- Restored full CLI argument parser and demo() function that were accidentally removed during the magic-number extraction in v2.1.40-pro.
- --demo, positional question, --evidence, --evidence-file, --alternatives, --version, --decision, and --validate now work again.
- Evidence file loading, error messages, and exit codes match the previous tested contract.
- No change to analysis logic, constants, fingerprints, or numerical results.
