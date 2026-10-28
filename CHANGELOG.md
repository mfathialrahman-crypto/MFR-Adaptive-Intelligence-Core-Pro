## [2.1.43-pro] - 2026-10-28

### Improved
- Added direct unit tests for `main()` CLI paths (demo, evidence, evidence-file object, decision+validate, error cases).
- Measured coverage on mfr_core_pro.py raised from ~68% to ~92% (CLI main now counted; remaining misses are argparse version exit and a few rare branches).
- pytest 48/48 pass.

### Verified
- All existing analysis contracts, fingerprints, and numerical results unchanged.
- No regressions in CLI behavior.

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
### Improved
- Added direct unit test for `demo()` function to raise measured coverage from ~66% to ~68% (CLI main still covered via subprocess). pytest 41/41 pass.

### Documented
- Independent verification cycle (2026-10-27): confirmed pytest 41/41 pass and measured coverage ~68% on mfr_core_pro.py. Updated README test count and coverage figure. No functional changes. Public surface at v2.1.42-pro.

### Fixed
- Restored full CLI argument parser and demo() function that were accidentally removed during the magic-number extraction in v2.1.40-pro.
- --demo, positional question, --evidence, --evidence-file, --alternatives, --version, --decision, and --validate now work again.
- Evidence file loading, error messages, and exit codes match the previous tested contract.
- No change to analysis logic, constants, fingerprints, or numerical results.
