# Changelog

All notable changes to MFR Adaptive Intelligence Core Pro will be documented here.

## [2.1.2-pro] - 2026-10-13

### Reliability & quality improvements
- Fingerprint is now truly content-addressable: excludes record_id, created_at, version, and other volatile fields so identical evidence produces identical fingerprints across instances.
- Strengthened Evidence validation (non-empty claim/source, positive numeric weight).
- Added regression tests for validation edges, deduplication, and cross-instance fingerprint stability.
- Added standard Python .gitignore.
- CI now tests Python 3.10, 3.11, and 3.12.

## [2.1.1-pro] - 2026-10-13

### Elite public elevation
- World-class README with full architecture, doctrine, badges, and usage paths
- Added SECURITY.md and CONTRIBUTING.md
- Strengthened public positioning as the transparent layer of FathiMind
- Metadata and install experience polished

## [2.1.0-pro] - 2026-10-11

- Initial public MIT release of the Adaptive Intelligence Core
- Bayesian-style Beta updates with independence penalty
- Full audit trail + content-addressable fingerprints
- Actionable self-improvement suggestions
- Conflict detection and credible intervals
