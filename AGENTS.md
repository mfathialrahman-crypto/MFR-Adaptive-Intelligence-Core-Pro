# AGENTS.md — MFR Adaptive Intelligence Core Pro

Constitution for any agent (human or AI) working on this public package.

**Last independent verification:** 2026-11-07 (local clone, pytest 31/31, coverage 98%, mypy --strict clean)

## Role of this package

Transparent Bayesian evidence core of the FathiMind ecosystem.  
Public MIT surface. Zero runtime dependencies. Deterministic and auditable.

It measures and verifies evidence. It does not invent facts, make strong claims at low confidence, or cross into private engine territory (Cognition, Helix, Aether, Evolution).

## Non-negotiable doctrine

1. No strong recommendation at low confidence.
2. Every decision leaves a replayable trace (fingerprint + full audit trail).
3. Layers stay separate: this core is the evidence / measurement layer only.
4. Public surface must be accurate, tested, and competitive. No performance or security claims beyond what the tests demonstrate.
5. Prefer the simplest design that is correct, testable, and hard to misuse.

## Engineering rules

- Single source of truth for version is `version.py`. Keep `pyproject.toml`, README, and this file aligned.
- All changes must keep the test suite green. Run `python -m pytest test_mfr_core_pro.py -v` before claiming success.
- Coverage gate in CI is ≥ 90%. Do not inflate with empty tests.
- `mypy mfr_core_pro.py --strict` must stay clean.
- Do not introduce third-party runtime dependencies.
- Bounds on inputs (MAX_EVIDENCE_ITEMS, string lengths, alternatives) exist for reliability / DoS hardening — preserve them.
- Fingerprint is content-addressable (question + prior + alternatives + evidence). Changing any of these must change the fingerprint.
- Status values are only: `INSUFFICIENT_EVIDENCE` | `CONFLICTING_EVIDENCE` | `PROVISIONAL_FINDING`.
- Suggestions must stay actionable and non-prescriptive.

## Continuous improvement cycle

Inspect → Detect → Analyze → Prioritize → Develop → Test → Verify → Record → Improve

Priority order for any change:

1. Stability and correctness
2. Security / input hardening
3. Functional completeness of the evidence contract
4. Performance and determinism
5. Documentation and competitive public surface
6. Secondary polish

## What not to do

- Do not claim tests passed unless you ran them and observed the result.
- Do not invent coverage numbers or CI conclusions.
- Do not force-push main.
- Do not add features that dilute the evidence-first contract.
- Do not move private engine logic into this public package.

## Acceptance for a change

- Tests green on the changed code
- Version, CHANGELOG, and any public claims updated together when the contract or behaviour changes
- Rollback path is clear (git revert of the commit is sufficient for pure analysis changes)

When in doubt, prefer a smaller, verified improvement over a large untested one.
