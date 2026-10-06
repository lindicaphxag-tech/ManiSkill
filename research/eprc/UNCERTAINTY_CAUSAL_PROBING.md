# Uncertainty-causal certificate probing

The first fully green VQ-BeT PushT run exposed a failure mode in a generic
"collect more probes" strategy.

The frozen held-out repair request was inconclusive even though:

- five paired-RNG DEC replicates were identical;
- q95 cross-seed DEC radius was 0;
- preprocessing and paired-policy repeat errors were 0.

The dominant uncertainty was instead finite-difference **scale drift**
(3.0126 in operator norm).

A directional information-matrix update cannot, by itself, justify shrinking a
curvature/locality envelope. Treating all uncertainty as one scalar beta would
therefore spend black-box queries without interrogating the mechanism that
blocks the certificate.

## Rule

Each uncertainty source has an admissible evidence action:

| bottleneck | admissible next experiment |
| --- | --- |
| finite-difference locality / scale drift | smaller symmetric physical perturbation |
| paired-policy stochasticity | repeated paired-randomness query |
| requested-direction uncertainty | targeted support-direction probe |
| global support coverage | weakest-information-direction probe |
| controller authority | replan/change controller; no extra policy probe |
| resolved certificate | stop |

Evidence from one row is not credited as shrinking another row.

This is an **evidence-provenance rule**, not a claim that one experiment is
guaranteed to resolve the certificate.

## Real VQ-BeT consequence

Using the frozen run-37456801175 values, the router selects:

`SHRINK_SYMMETRIC_SCALE`

rather than the six additional directional probes proposed by the earlier
information-only AMRC planner.

That changes the next real-policy experiment from "more directions" to a
nested-scale locality assay.

## Claim boundary

Adaptive experimental design and active learning are established fields. The
claim under test is narrower: physical repairability certificates for frozen
robot policies require **uncertainty-source-preserving evidence acquisition**;
otherwise a runtime can appear to gain confidence from evidence that never
measured the active failure mechanism.
