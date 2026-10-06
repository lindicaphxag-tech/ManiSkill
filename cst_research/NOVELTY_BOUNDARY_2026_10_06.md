# Novelty Boundary Audit — 2026-10-06

## Claims we explicitly do NOT make

The following are established ideas and are not claimed as contributions:

- simulation / approximate simulation / bisimulation relations;
- controller/interface synthesis from simulation relations;
- feedback refinement and abstraction-based control;
- pseudoinverse minimum-norm control allocation;
- counterexample-guided inductive synthesis (CEGIS);
- absolute-vs-delta or joint-vs-task action-space comparisons;
- action normalization as part of executable robot policy semantics.

Relevant neighboring lines include classical bisimulation controller synthesis,
modern simulation-relation/control-interface characterizations, CEGIS-based
controller synthesis, and 2026 robot-learning studies of action-space design
and controller gains.

## Narrow research hypothesis

The current candidate contribution is a **robot-learning deployment compiler**:

> Given an already-trained frozen policy and two concrete controller
> implementations, extract their executable action/state contracts, determine
> whether policy outputs can be migrated while preserving a declared physical
> behavior, synthesize the required state/action adapter when possible, and
> return machine-checkable refusal evidence when not.

The novelty burden therefore sits on four pieces together:

1. **Implementation-to-contract extraction** from real robot-learning stacks,
   including normalization, frames, delta baselines, previous-target memory,
   interpolation and controller-owned state.
2. **Frozen-policy controller migration**, where policy weights are unchanged
   and the compiler operates strictly at the executable interface.
3. **Proof-carrying deployment result**: exact / approximate / refuse plus the
   state/action adapter, validity scope and unmatched-direction evidence.
4. **Upstream-grounded validation**: real action-conversion failures and
   independent stacks, not only synthetic control examples.

## Current evidence

Already implemented on the public research branch:

- local closed-loop exact/approx/impossible certificate;
- constructive unmatched-direction witness;
- finite-horizon local error bound;
- finite-pool regional shared-adapter consistency;
- counterexample-guided frozen-pool synthesis;
- different-dimensional controller-state handshake;
- ManiSkill joint-position executable contract compiler;
- 3600 randomized migrations spanning absolute, delta-current, delta-target and
  normalized/non-normalized charts.

External anchor:

- ManiSkill issue #429 reports 0% conversion success for one
  pd_joint_delta_pos -> pd_joint_pos path.
- A separate minimal two-file PR-ready branch fixes the concrete semantic
  mismatch and has a focused green CI run.

## What is still required before a strong novelty claim

- automatic extraction from the actual ManiSkill runtime controller object,
  rather than manually instantiated contracts;
- one second independent stack (robomimic or LeRobot);
- a true closed-loop simulator replay showing source-vs-migrated trajectory
  behavior;
- at least one external maintainer review/merge or independent reproduction;
- nonlinear validity-region evidence beyond a finite sample pool.

Until these gates are crossed, label the work **L8-candidate**, not L8 achieved.
