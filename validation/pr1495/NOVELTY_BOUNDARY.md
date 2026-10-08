# Novelty Boundary and Nearest-Concept Audit

This note intentionally narrows the research claim. It is a defense against overclaiming, not a novelty certificate.

## Claims we should NOT make

### "Proof-carrying" is new

It is not. Proof-Carrying Code dates to Necula's POPL 1997 work, and recent systems also use proof-carrying / machine-checkable evidence for agentic changes and generated artifacts.

Therefore this project should not claim novelty from attaching a certificate to a repair.

### "Semantic program repair" is new

It is not. Automated program repair has long included semantic constraints, retesting, multi-point repair, runtime feedback, and structured repair procedures.

Therefore this project should not claim novelty from detecting a semantic mismatch, synthesizing a patch, or retesting it.

### "Runtime feedback after repair" is new

It is not. Recent APR systems explicitly incorporate runtime feedback, and recent agent-repair systems use retest-conditioned updates.

Therefore the contribution is not simply a detect→repair→rerun loop.

## Narrow research claim

The strongest current contribution is the conjunction of four properties:

1. **Compensating semantic defects in a robot execution stack**  
   Two locally incorrect boundaries can partially cancel, so the current system looks approximately correct under a local semantic metric.

2. **Non-monotone repair activation**  
   Repairing either defect alone can make behavior dramatically worse even when the local repair itself is semantically justified.

3. **Repair-set interaction certificate**  
   Repairs are evaluated factorially on identical frozen requests, with an explicit interaction term:
   `E12 = L12 - L1 - L2 + L0`,
   episode-level identities, and cluster-aware uncertainty.

4. **Authority separated from correctness**  
   A local correctness certificate is not execution authority. Activation requires independent interaction and execution-effect gates.

The current ManiSkill evidence is valuable because all four properties occur in a production robot-learning software boundary rather than a synthetic patch benchmark.

## Current evidence supporting this boundary

Frozen direct semantic-fidelity evidence reported approximately:

- current main: 0.018963° mean SO(3) error;
- converter-only repair: 161.489889°;
- controller-only repair: 161.486206°;
- composed repair: 0.017321°.

Latest 10-demo execution replay:

- current main: 9/10;
- converter-only: 1/10;
- controller-only: 0/10;
- composed: 8/10.

This combination is important:

- semantic composition is near-perfect;
- execution non-regression is not yet established.

That directly motivates separate semantic-interaction and execution-effect authorization gates.

## Nearest concept families checked

This audit includes, but is not limited to:

- Proof-Carrying Code (Necula, POPL 1997);
- semantic-defect automated repair / constraint-guided repair;
- runtime-feedback automated program repair;
- proof-carrying AI / artifact-generation systems;
- structured repair for interactive agents.

None of these categories should be treated as absent from prior work.

The paper should instead ask a narrower question:

> When multiple semantic defects in embodied-software boundaries compensate for one another, what evidence is required before a locally correct repair is allowed to change executable robot behavior?

## Novelty wording to prefer

Prefer:

> interaction-aware authorization of executable repairs under compensating semantic defects

or:

> repair-set authorization for non-monotone semantic repair in robot software

Avoid:

> the first proof-carrying repair system

> the first semantic repair framework

> the first runtime-verified repair system

unless an exhaustive literature review later justifies such a statement.

## Evidence still required for a strong paper claim

- complete paired semantic-fidelity result on immutable corpora;
- execution-domain non-regression on a larger paired sample;
- at least one additional independent defect interaction or external reproduction;
- upstream maintainer retention / discussion if obtainable;
- policy-level experiment only after the semantic and execution gates are resolved.

## External references used for boundary-setting

- George C. Necula, "Proof-carrying code", POPL 1997, DOI 10.1145/263699.263712.
- "Automatic Repair of Semantic Defects Using Restraint Mechanisms", Symmetry 2020.
- "SEED-APR: A closed-loop self-evolving framework for automated program repair", Systems and Soft Computing, 2026.
- "PRISM: Proof-Carrying Artifact Generation through LLM x MDE Synergy and Stratified Constraints", arXiv:2510.25890.
- "Safe, Untrusted, Proof-Carrying AI Agents: toward the agentic lakehouse", arXiv:2510.09567.

This is a targeted nearest-concept audit, not an exhaustive systematic review.
