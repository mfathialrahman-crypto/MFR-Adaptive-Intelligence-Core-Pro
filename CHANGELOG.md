# Changelog

All notable changes to MFR Adaptive Intelligence Core Pro will be documented here.

## [2.1.8-pro] - 2026-10-17

### Maintainability / version hygiene
- Introduced `version.py` as the single source of truth for the package version.
- `mfr_core_pro.VERSION` now imports from `version.VERSION`.
- Aligned `pyproject.toml`, README badges, and runtime reports.
- Added packaging of `version` module.
- Added regression test for version consistency.

## [2.1.7-pro] - 2026-10-16

### User experience / CLI completeness
- CLI `--evidence` now accepts optional WEIGHT and INDEPENDENT flags after reliability.
- Format: `--evidence CLAIM SOURCE RELIABILITY [WEIGHT] [true|false]`
- Existing 3-argument usage remains fully compatible.
- Improved error messages for malformed evidence arguments.

## [2.1.6-pro] - 2026-10-16

### Reliability / CI
- Fixed CLI so `python mfr_core_pro.py` (no arguments) runs the built-in demo, matching README and CI workflow expectations.
- Made `question` positional argument optional; error only when evidence is supplied without a question.
- CI demo step now succeeds on all Python versions in the matrix.

## [2.1.5-pro] - 2026-10-16

### Reliability
- Extended CI matrix to Python 3.13 (in addition to 3.10–3.12). Pure stdlib; no behavior change.
