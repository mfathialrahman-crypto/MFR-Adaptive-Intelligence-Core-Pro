# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` suffix is a public surface marker).

## [2.1.66+pro] - 2026-11-17

### Fixed
- Packaging: changed version suffix from invalid PEP440 `-pro` to valid local version `+pro` so `pip install -e .` and wheel builds succeed.
- Aligned version.py, pyproject.toml, README, CHANGELOG, AGENTS.md, and tests.
- Restored full analysis implementation that had been accidentally replaced earlier (retained).

### Notes
- 53/53 pytest passed after the change. mypy --strict clean. Continuous cycle: packaging reliability improved.

## [2.1.65-pro] - 2026-11-17

### Changed
- CLI --help output now lists both the installed `mfr-core` command and the direct `python mfr_core_pro.py` form, with cleaner formatting.

### Notes
- No change to analysis logic. 53 tests continue to pass. mypy --strict clean. Continuous improvement cycle active.
