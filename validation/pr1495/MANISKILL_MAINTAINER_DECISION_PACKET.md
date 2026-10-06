# ManiSkill maintainer decision packet — #1472 / #1495

This is intentionally short. The full evidence remains in the public validation PR and frozen snapshot.

## One decision

Current public evidence says the two fixes should **not** be reviewed as independent deployable units.

On two identical-request official-demo corpora:

- converter-only repair is materially worse than current main;
- controller-only repair is materially worse than current main;
- composed repair has lower converter→controller SO(3) semantic error than main.

But the clean composed/adapter path still fails the current execution non-regression gate:

- current main: **9/10 × 5** fresh-process repeats;
- clean candidate: **8/10 × 5** fresh-process repeats.

So the evidence supports neither singleton merge nor composed promotion yet.

## Minimal maintainer question

Which upstream direction best matches ManiSkill 4 plans?

**A — Defer both semantics fixes to the MS4 controller redesign.**
Keep #1469/#1138 as migration requirements and close/defer #1472/#1495.

**B — Treat #1472 + #1495 as one compatibility-sensitive migration.**
Review a combined patch only after a host-native replay/non-regression test and a migration note for downstream policies/controllers that may have compensated for the old behavior.

**C — Preserve current controller semantics for compatibility.**
Document the current sign/representation convention explicitly and reject the proposed semantic correction.

No merge request is implied by this packet. A one-letter/design-direction answer is enough to avoid further work in the wrong direction.

## Why a local unit test is insufficient here

The local representation/sign fixes are individually defensible, but the current stack contains compensating semantics. The deployable unit is therefore not the same as the locally correct patch unit.

Canonical public evidence:

- paired semantic interaction: workflow `37401619096`;
- repeatability-qualified execution gate: workflow `37407944746`;
- public evidence PR: `lindicaphxag-tech/ManiSkill#1`;
- frozen evidence branch: `evidence/semrepair-2026-10-06-v1`.

## AI disclosure

Substantial AI assistance was used for code audit, experiment harnesses, and drafting. The contributor is responsible for verifying exact source identities, public runs, negative results, and the technical interpretation.
