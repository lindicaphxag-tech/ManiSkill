# CST novelty audit — 2026-10

Status: **working novelty boundary, not a priority claim**.

This audit intentionally removes broad claims already covered by current robot
learning systems and papers.

## Adjacent work that constrains CST

### LeRobot relative actions

LeRobot already provides `RelativeActionsProcessorStep` /
`AbsoluteActionsProcessorStep` and defines a relative trajectory where every
action in a chunk is offset from a state cached at prediction time. Its merged
PR #2970 introduced this representation and PR #3711 made the processor
pipeline part of the pretrained checkpoint contract.

Therefore CST does **not** claim relative-action preprocessing, chunk-latched
references, absolute↔relative subtraction, relative-action statistics, or
checkpoint processor wiring as new.

### NVIDIA Isaac-GR00T ActionChunk

Current Isaac-GR00T explicitly implements both `relative_chunking` (all poses
relative to a common reference frame) and `delta_chunking` (each pose relative
to the previous pose).

Therefore CST does **not** claim the relative-vs-delta taxonomy or generic
trajectory conversion as new.

### Action-space research

Feng et al., *Demystifying Action Space Design for Robotic Manipulation
Policies*, ICML 2026, systematically studies absolute/delta and joint/task-space
choices with 13,000+ real-world rollouts and 500+ trained models.

CAT (arXiv:2608.24111) studies trajectory-level continuous action
representations. UMR (arXiv:2609.34256) proposes a universal manipulation
representation for cross-embodiment transfer. These works remove any broad
claim that CST introduces the importance, unification, or learning advantage of
action representations.

## Narrow CST hypothesis that remains

CST targets a different question:

> Given two already-existing controller/action conventions and the controller
> state actually recorded at a boundary or over a sequence, can software decide
> *before rollout* whether the source physical command semantics are uniquely
> identifiable and exactly representable by the target convention, and either
> compile an exact native target action/sequence or return a constructive
> refusal witness?

The candidate contribution is the conjunction of:

1. **reference-state identifiability** — distinguish endogenous, exogenous, and
   latched reference state and fail when required provenance is absent;
2. **target-image membership** — exact conversion is forbidden when the
   physical semantic goal lies outside the target native action image;
3. **reference-machine sequence transport** — compile between fixed-latch,
   measured-current, accumulated-target, and absolute conventions while
   updating the correct reference automaton;
4. **constructive refusal** — identify the first nonrepresentable step,
   violating coordinates, or missing state rather than silently clipping;
5. **independent verification** — bind chart/context identities to a proof
   record and re-check semantics without invoking the compiler.

## Explicit non-claims

CST does not currently claim:

- a new policy action representation;
- better policy learning performance;
- a universal embodiment representation;
- generic controller dynamics equivalence;
- exact task-success preservation;
- robot safety;
- formal theorem-prover verification;
- LeRobot, GR00T, ManiSkill, or robomimic adoption.

## Falsifiers

The novelty claim must contract if prior work is found that already combines
controller reference-state identifiability, exact target-action-image
membership, sequence reference-machine compilation, and constructive refusal
for cross-controller robot action conversion under equivalent assumptions.

Even if the software mechanism remains useful, external adoption and E3/E4
rollout evidence are separate requirements for a strong research claim.
