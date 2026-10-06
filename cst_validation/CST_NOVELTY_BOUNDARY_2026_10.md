# Controller-Semantic Transport — novelty boundary (2026-10)

Status: **research method candidate; not yet an external-adoption claim**.

## What is already prior art

CST does **not** claim any of the following as new:

- choosing delta rather than absolute robot actions;
- choosing joint-space rather than task-space actions;
- canonical state/action representations for heterogeneous robot data;
- action adapters for cross-embodiment policies;
- inverse kinematics, trajectory retargeting, or controller tuning;
- converting a physical absolute target into a relative command when all
  required state is already known.

Recent work makes these boundaries especially important.

**Demystifying Action Space Design for Robotic Manipulation Policies (2026)**
systematically studies absolute vs delta and joint vs task-space action choices
at large real-robot scale. CST is not an action-representation performance
study.

**SPACE (2026)** uses Cartesian state delta as a universal representation and
an Action Adapter to convert that representation into robot-specific control
commands. CST is not claiming the general idea of a canonical action space or
an action adapter.

**InternW0-Delta (2026)** converts heterogeneous datasets into a canonical
state-action representation before large-scale training. CST is not a data
standardization contribution.

## Narrow method hypothesis

Existing robot-learning stacks often treat action conversion as a stateless
numeric map. That is insufficient whenever a controller action is interpreted
relative to physical state, a previous target, a frame, a normalization chart,
or another hidden controller variable.

CST models a controller as a stateful semantic transducer

    C : (x_t, z_t, u_t) -> (y_t, z_{t+1}),

where:
- x_t is externally observable physical state;
- z_t is controller-owned hidden semantic state (for example previous target);
- u_t is the native action representation;
- y_t is the physical control goal / shared observable.

A source-to-target transport is exact only when a compiler can construct

    T(x_t, z_t^A, z_t^B, u_t^A) = u_t^B

such that the two controllers produce the same declared physical observable and
the relation between their hidden semantic states is preserved for the next
step.

The research claim is therefore **not** "we can convert delta to absolute."
It is:

> A controller conversion can be treated as a proof-carrying semantic
> compilation problem. Exactness, information loss, target ambiguity and
> unrepresentability can be classified before execution, and stateful
> conversions can be certified over whole trajectories rather than assumed
> from per-step numeric formulas.

## Current constructive pieces

The research branch contains:

1. explicit source-native -> physical-command -> physical-target ->
   target-native decode/encode semantics;
2. hidden target-state semantics for absolute, delta-current and delta-target
   joint controllers;
3. one-step proof certificates with representability masks and semantic
   residuals;
4. a fail-closed trace compiler that returns the exact prefix and first
   unrepresentable step rather than silently clipping the remainder;
5. randomized long-trace tests for semantic drift;
6. an independent native ManiSkill simulator assay under construction.

## Decisive promotion gates

CST should not be presented as L8/L9 until the following are true.

### Gate A — upstream bug closure
ManiSkill issue #429 must have a reproducible upstream-base failure and a
minimal fix that a maintainer accepts or technically validates.

### Gate B — native state equivalence
For at least one exact controller pair, source and compiled-target executions
must start from identical simulator state and preserve:
- controller physical targets;
- robot joint state trajectory within a declared tolerance;
- task outcome where relevant.

### Gate C — stateful necessity
At least one pair involving controller-owned target state must show that naive
stateless action copying/conversion drifts or becomes unrepresentable while the
state-aware compiler either preserves the target-state relation or refuses at
the correct first step.

### Gate D — second independent stack
At least one equivalent semantic bug / conversion path must be reproduced in a
second maintained stack such as robomimic, LeRobot, IsaacLab or another public
robot-learning framework.

### Gate E — external retention
At least one maintained external repository must retain the fix, test, or
compiler-derived semantic contract. A fork-only validation does not count as
adoption.

## Paper-safe headline today

> Robot action conversion is not always a stateless change of coordinates.
> When controller-owned state participates in action meaning, reliable
> conversion requires state-aware semantic compilation and an explicit
> representability/refusal contract.

Do not currently write:
- "CST solves cross-controller conversion in general";
- "CST guarantees identical robot trajectories";
- "CST has been adopted by ManiSkill";
- "CST is L8/L9";
- "CST is the first action adapter or canonical action representation."


## Closed-loop extension boundary

The current research branch additionally studies controller migration at the
closed-loop local-dynamics level. This extension must be distinguished from
several adjacent areas:

- **SPACE (2026)** learns a universal Cartesian state-delta representation and
  robot-specific Action Adapter, including robustness to controller-gain and
  control-frequency shifts. CCLAT therefore does not claim that adapting
  commands across robot dynamics or controller changes is new.
- **XPolicyLab (2026)** standardizes observation/action/trajectory schemas and
  adapter interfaces across many policies and environments. CCLAT does not
  claim policy/runtime interface standardization.
- **ActionShift (2026)** studies adaptation to hidden action-interface
  contracts (permutation, sign, scale, target convention, frame, latency,
  gripper semantics). CCLAT does not claim hidden-contract adaptation or
  action-interface benchmarking.
- Classical control already contains simulation/bisimulation, approximate
  simulation, state-feedback matching, control allocation, and model-refinement
  ideas. CCLAT does not claim those mathematical primitives as new.

The narrowed closed-loop hypothesis is:

> For a frozen robot policy being migrated between controller implementations,
> the deployment interface should expose a proof-carrying refinement step that
> (i) includes controller-owned semantic state, (ii) tests whether source
> closed-loop directions are representable in the target controller's local
> executable image, (iii) synthesizes a stateful adapter when possible, and
> (iv) returns an explicit impossibility witness or finite-horizon deviation
> bound otherwise.

The novelty burden is therefore on the **robot-policy migration compiler and
its executable evidence**, not on pseudoinverses, state feedback, or
bisimulation theory themselves.

### Additional promotion evidence required

The linear closed-loop method is frozen in
`cst_validation/CCLAT_METHOD_V0_1.md`. It remains method-level evidence until
a native nonlinear held-out controller-swap assay verifies that the synthesized
adapter improves real simulator state evolution without tuning on the held-out
points.
