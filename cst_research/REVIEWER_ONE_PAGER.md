# Certified Closed-Loop Semantic Transport — Reviewer One-Pager

**Status: L8-candidate research prototype. Not yet externally adopted.**

## One-sentence problem

A frozen robot policy may emit numerically valid actions that become physically
wrong after a controller, reference convention, action rate, or controller
state change. CST asks whether that migration is executable, synthesizes the
required adapter when possible, and refuses with evidence when it is not.

## Why this is not just action normalization

The executable meaning of an action depends on more than shape and range:

- absolute vs relative coordinates;
- which state owns the relative reference;
- normalized vs physical controller chart;
- controller-owned memory (previous target, integrator, filter state);
- controller action range / saturation;
- policy-chunk query time vs execution-step state availability;
- control frequency and hold semantics.

The same numeric action can therefore denote different physical goals even when
dimensions, units and ranges match.

## External anchors

### ManiSkill #429

A public issue reports 0% success for one
`pd_joint_delta_pos -> pd_joint_pos` conversion path. A ManiSkill maintainer
previously described fully accurate action-space conversion as highly
non-trivial and potentially publication-worthy.

This work has:
- a public technical diagnosis comment on #429;
- a minimal PR-ready two-file / two-commit branch;
- a public identical-regression base-fail / fix-pass workflow;
- focused fix CI passing.

Maintainer response to the new diagnosis is still pending.

### robomimic #270

The issue explicitly requests the reverse of robomimic's existing
delta->absolute conversion. Maintainer `amandlek` stated they are happy to
accept a PR.

CST's second-stack prototype derives the inverse from current robosuite OSC
controller semantics, including scaling, SO(3), desired-goal memory,
saturation, and action remainder.

## Implemented method stack

1. **Implementation -> executable contract extraction**
   - reads controller runtime fields rather than manually labeling examples.

2. **Closed-loop local transport**
   - synthesizes stateful action adapters;
   - outputs EXACT / APPROXIMATE / IMPOSSIBLE;
   - returns an unmatched physical-direction witness when exact transport is
     impossible.

3. **Regional consistency**
   - distinguishes pointwise convertibility from existence of one deployable
     adapter across a state set;
   - counterexample-guided frozen-pool refinement.

4. **Controller-state handshake**
   - maps controllers with different internal state dimensions;
   - includes previous target / controller memory in proof obligations.

5. **Reference ownership**
   - ABSOLUTE;
   - CURRENT_STATE;
   - CHUNK_ANCHOR;
   - PREVIOUS_COMMAND;
   - CONTROLLER_TARGET;
   - per-dimension masks such as relative arm + absolute gripper.

6. **Causal deployability**
   - PRECOMPUTABLE;
   - REQUIRES_STEP_HOOK;
   - EXECUTABLE_WITH_STEP_HOOK;
   - REFUSE_MISSING_RUNTIME_STATE.

7. **Just-in-time transport**
   - converts frozen action chunks at execution time when future references are
     not available at policy-query time.

8. **Controller-rate transport**
   - compiles integer rate upsampling under a declared ZOH physical-goal
     contract;
   - catches the failure mode where repeated delta commands accumulate multiple
     times.

## Public quantitative evidence

### Full research suite

Latest public run:

`59 passed in 1.30s`

### ManiSkill contract matrix

`3 source modes x 3 target modes x 2 source normalization x 2 target
normalization x 100 random cases = 3,600 migrations`.

Every in-range migration must reconstruct the source controller goal exactly;
out-of-range cases are labeled saturated rather than silently accepted.

### Pinned LeRobot parity

Against actual pinned public LeRobot action-conversion source:

- 2,000 trajectories;
- 18,000 action vectors;
- max goal error: approximately `1.49e-7`;
- stacked current-frame parity: `0.0`.

### Bounded cross-stack JIT

LeRobot-style CHUNK_ANCHOR -> CURRENT_STATE step-time transport:

- 2,000 trajectories;
- 18,000 action vectors;
- JIT max physical-goal error: approximately `7.45e-9`;
- naive tensor-copy mean max goal error: approximately `0.571`;
- naive tensor-copy global max goal error: approximately `1.152`.

### Robosuite OSC inverse

- achieved-state and desired-goal reference modes;
- 2,000 randomized executable-goal round trips;
- SO(3) inverse uses group composition, not rotvec subtraction.

## What is deliberately NOT claimed as novel

CST does not claim invention of:

- bisimulation / simulation relations;
- control-interface synthesis;
- CEGIS;
- pseudoinverse control allocation;
- delta actions;
- action normalization;
- high-frequency action chunks;
- asynchronous VLA execution.

The research hypothesis is the integration of these correctness obligations
into an **implementation-to-certificate compiler for frozen robot-policy
controller migration**, grounded in real robot-learning stacks and upstream
failures.

## Current negative evidence / unresolved gates

- Maintainer adoption: 0.
- #429 maintainer response to the new diagnosis: pending.
- robomimic fork / upstream PR: not yet available through the current GitHub
  integration.
- ManiSkill task-level simulator assay is blocked before controller execution by
  hosted-runner rendering-device requirements in task visual-asset creation.
- Continuous nonlinear validity-region proof: not yet established.
- Real-robot safety: not claimed.

## Hard gates for stronger status

**Strong L8 evidence**
1. upstream maintainer technical approval / review / merge;
2. actual controller or trajectory base-vs-fix execution evidence;
3. second-stack upstream integration or independent reproduction.

**L9-level evidence**
requires strong external retention/use, independent reproduction, or
peer-reviewed recognition in addition to the above.

## Reproduce

Checkout branch:

`research/closed-loop-semantic-transport-v1`

Then:

```
python -m pip install numpy pytest
cd cst_research
python -m pytest -q test_*.py
```

For exact run IDs and evidence status, see `EVIDENCE_LEDGER.md`.
