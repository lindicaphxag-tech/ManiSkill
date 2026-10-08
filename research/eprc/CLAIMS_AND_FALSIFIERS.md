# Claims, authority, and falsifiers

This file is the shortest review contract for the DEC / CRG / AMRC line.

## C1 — representation-invariant local physical response

**Claim under test:** after semantic/controller lifting, equivalent action
parameterizations expose the same local physical response class more reliably
than raw action-space comparison.

**Required evidence:** source-bound controller semantics plus held-out physical
response prediction.

**Falsifier:** raw action distance or static metadata predicts held-out physical
response equally well under the frozen prospective bank.

## C2 — repairability is stricter than local sensitivity

**Claim under test:** a stable nonzero local response is not sufficient to
authorize a repair; controller authority and local-model validity matter.

**Required evidence:** real frozen-policy states where DEC is stable but CRG is
INCONCLUSIVE / IMPOSSIBLE / local-model rejected.

**Current witness:** VQ-BeT PushT has zero observed stochastic radius but
non-contracting finite-difference scale drift.

**Falsifier:** generic bounded residual correction matches CRG recovery and
false-accept rate under equal tuning budget.

## C3 — uncertainty source determines the next experiment

**Claim under test:** information-limited cases should receive targeted probes,
whereas locality-limited cases should shrink scale or reject the local model.

**Required evidence:** frozen matched-query comparison.

**Falsifier:** equal-budget same-scale repetition resolves locality-limited
cases just as often and as safely as source-directed routing.

## C4 — certificate-directed identification can stop early

**Claim under test:** the runtime need not identify a full Jacobian when a
specific repairability certificate can be resolved earlier.

**Required evidence:** policy evaluations to first terminal certificate at
matched false-accept rate.

**Falsifier:** dense/coded fixed-budget probing uses no more policy evaluations
or yields materially safer decisions.

## C5 — higher local model order — falsified for the flagship

The richer response-jet extension was prospectively tested on five frozen
states.

Result:

- jet upgrades: **0/5**;
- jet rescues: **0/5**;
- frozen decision: `DROP_JET_FROM_FLAGSHIP`.

This extension is therefore **not a flagship claim**. It remains a negative
model-order result showing that extra local polynomial complexity should not be
introduced without held-out physical evidence.

## C6 — external validation

No self-authored result can satisfy this claim.

**Trigger:** one machine-valid independent frozen-policy replication plus either
maintained robotics-runtime adoption/merge or a second independent policy-family
replication.

Until then, the project is an externally inspectable **L8-candidate**, not an
externally validated L8/L9 result.
