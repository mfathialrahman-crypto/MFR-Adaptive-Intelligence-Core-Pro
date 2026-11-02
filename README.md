# MFR Adaptive Intelligence Core Pro

**Evidence → Bayesian Reasoning → Verification → Self-Improvement**

Transparent adaptive intelligence core of the FathiMind ecosystem.  
Zero-dependency public MIT package. Deterministic, auditable, and evidence-first.

**Current version:** `2.1.46-pro` (see `version.py`)

## Doctrine

- No strong recommendation at low confidence.
- Every decision is a replayable trace (fingerprint + full audit trail).
- Layers stay separate: this core measures and verifies evidence; it does not invent facts.
- Public surface is accurate, tested, and competitive. No performance or security claims beyond what the tests demonstrate.

## Architecture

```
Evidence (claim, source, reliability, independent, weight)
        │
        ▼
Deduplicate by source → Group by claim
        │
        ▼
Beta prior (strength 2.0) + soft positive / opposition updates
        │
        ▼
Posterior mean + approximate 95% CI
        │
        ▼
Status: INSUFFICIENT_EVIDENCE | CONFLICTING_EVIDENCE | PROVISIONAL_FINDING
        │
        ▼
Suggestions + content-addressable SHA-256 fingerprint
```

## Quick start

```bash
# Clone and run tests (no install required for local use)
git clone https://github.com/mfathialrahman-crypto/MFR-Adaptive-Intelligence-Core-Pro.git
cd MFR-Adaptive-Intelligence-Core-Pro
python -m pytest test_mfr_core_pro.py -v

# Or run the built-in demo
python mfr_core_pro.py
```

### Programmatic use

```python
from mfr_core_pro import Evidence, IntelligenceRecord

record = IntelligenceRecord(
    question="Is the system healthy?",
    evidence=[
        Evidence(claim="healthy", source="monitor-a", reliability=0.9, independent=True),
        Evidence(claim="healthy", source="monitor-b", reliability=0.85, independent=True),
    ],
    alternatives=["healthy", "degraded"],
)
report = record.analyze()
print(report["status"], report["conclusion"], report["confidence"])
print(report["fingerprint"])
```

## Hardening notes (2.1.46-pro)

- `MAX_EVIDENCE_ITEMS = 1000` — rejects oversized evidence lists.
- `MAX_STRING_LENGTH = 4096` — rejects pathological claim/source/question strings.
- Content-addressable SHA-256 fingerprints independent of timestamps and record IDs.
- Decision-contract fields: `decision_confidence`, `stability`.

## License

MIT — see `LICENSE`.
