## [2.1.42-pro] - 2026-10-27

### Fixed
- `--evidence-file` now accepts the documented object format from README (with `question`, `evidence`, optional `prior_belief` and `alternatives`) in addition to a bare JSON array.
- CLI prefers explicit command-line values, then falls back to values present in the evidence file.
- Added regression test covering the object format. All 39 unit tests pass.

### Verified
- pytest 39/39 pass.
- No change to analysis logic, fingerprints, or numerical results when using array format.
- Version aligned across version.py, pyproject.toml, and README.

## [Unreleased]

### Documented
- Independent verification cycle (2026-10-27): confirmed pytest 38/38 pass and measured coverage ~69% on mfr_core_pro.py (CLI paths covered via subprocess). Updated AGENTS.md review note. Added coverage measurement instructions and AGENTS.md link to README. Added pytest-cov to optional dev dependencies. No functional changes. Public surface at v2.1.41-pro.

### Fixed
- Restored full CLI argument parser and demo() function that were accidentally removed during the magic-number extraction in v2.1.40-pro.
- --demo, positional question, --evidence, --evidence-file, --alternatives, --version, --decision, and --validate now work again.
- Evidence file loading, error messages, and exit codes match the previous tested contract.
- No change to analysis logic, constants, fingerprints, or numerical results.

### Verified
- pytest 38/38 pass.
- mypy --strict clean.
- Public surface at v2.1.41-pro.
