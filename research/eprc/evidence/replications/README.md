# Independent EPRC / DEC replication via pull request

Issues are disabled on this fork, so independent evidence is accepted through ordinary GitHub pull requests.

## Minimal path

1. Fork this repository.
2. Run the public capsule and your own frozen policy/controller experiment.
3. Add exactly one JSON file under `research/eprc/evidence/replications/`.
4. Compute its canonical `evidence_digest` with `canonical_evidence_digest`.
5. Open a pull request against this fork.

Positive results are not required. A clean REJECT, failed repair, false accept, false reject, or unstable support result is useful if the evidence is complete.

## Required fields

- producer GitHub / lab identity;
- explicit independence attestation;
- source repository + immutable commit;
- policy family + immutable checkpoint;
- controller representation;
- physical support intervention protocol;
- support stability;
- held-out intervention residual;
- representability margin;
- emitted PASS / TRANSPORT / REPAIR / REJECT decision;
- actual execution outcome;
- canonical SHA-256 evidence digest.

Self-authored records from `lindicaphxag-tech` / `fhby` are rejected by the validator and do not count toward L8.

## Why PRs are preferred

A PR gives the replication an immutable diff, author identity, review conversation, CI result and merge history. That is stronger evidence than a star, a screenshot, or an unversioned message.