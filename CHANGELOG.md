# Changelog

All notable changes to MFR Adaptive Intelligence Core Pro will be documented here.

## [2.1.9-pro] - 2026-10-17

### Transparency
- Analysis reports now include `evidence_notes` when any evidence carries non-empty notes.
- Improves auditability without changing core scoring logic.
- Fully backward compatible (new optional field).

## [2.1.8-pro] - 2026-10-17

### User experience / CLI completeness
- Added optional `--alternatives` flag to CLI (repeatable) to record competing hypotheses for context.
- Alternatives are stored in the analysis record; core evidence analysis remains unchanged.
- Fully backward compatible.

## [2.1.7-pro] - 2026-10-16

### Documentation
- README now explicitly references `AGENTS.md` as the governing Project Engineering Constitution.

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

## [2.1.4-pro] - 2026-10-13

### Developer & user experience
- Added minimal CLI (`python mfr_core_pro.py "question" --evidence ...`) for quick analysis without writing code.
- `--demo` flag and `--prior` support.
- Existing demo and library API unchanged.

## [2.1.3-pro] - 2026-10-13

### Bayesian prior correctness
- `prior_belief` is now actually used: mapped to a weak Beta prior (concentration ≈ 2).
- Validation rejects prior_belief outside [0, 1].
- Audit trail records the prior parameters used.
- Added tests confirming prior influence and rejection of invalid priors.

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
