# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `-pro` suffix is a public surface marker).

## [Unreleased]

### Added
- Regression tests for non-overlapping 95% CI stronger-separation signal and for whitespace-stripped alternatives in suggestions. Coverage raised to 98%.

### Changed
- AGENTS.md last-reviewed stamp refreshed after local verification (2026-11-02T00:22Z: 25/25 pytest passed, 98% coverage, mypy --strict clean).

### Added
- Tests covering the built-in `_demo()` path and the default coherent-evidence suggestion branch. Coverage raised from 91% to 96% on Python 3.10.

### Changed
- AGENTS.md last-reviewed stamp refreshed after independent local verification (22/22 pytest passed, 96% coverage, mypy --strict clean).


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
