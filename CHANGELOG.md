# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local identifier marks the public surface).

## [2.1.59+pro] - 2026-11-11

### Fixed
- Version string is now PEP 440 compliant (`2.1.59+pro` instead of invalid `2.1.59-pro`). This unblocks `pip install -e .` and packaging tools. No behavioral change.
- Updated version sources (version.py, pyproject.toml, README.md) and changelog note.

### Notes
- Previous non-compliant version prevented editable installs. Tests: 39/39 passed, mypy --strict clean. Continuous verification cycle active.

## [2.1.59-pro] - 2026-11-10

### Fixed
- Strict mypy compliance: introduced `ClaimStat` TypedDict for claim statistics, resolved all type errors under `mypy --strict`. Fingerprint helper now type-safe. No behavioral change.

### Notes
- Type safety improvement aligns public surface claim of clean strict typing. All 39 tests continue to pass. Version sources (version.py, pyproject.toml, README) aligned.
