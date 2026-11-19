# Changelog

All notable changes to the MFR Adaptive Intelligence Core Pro public package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),

## [2.1.67+pro] - 2026-11-19

### Added
- Regression tests for `from_json` edge cases: non-object root, missing question field, and non-dict evidence items (skipped safely). Coverage of validation paths improved.

### Changed
- Version bump after verified local suite (32/32 passed).

and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for the base version (the `+pro` local version marker is a public surface marker).

## [2.1.66+pro] - 2026-11-19

### Added
- Edge-case unit tests for Evidence and IntelligenceRecord validation (long source/question/alternatives, too many evidence items).

### Changed
- Version bump after verified local suite.
