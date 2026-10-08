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
saturation, action remainder, and legacy/current runtime controller layouts.
A staged upstream-style `robosuite_add_delta_actions.py` candidate now mirrors
the existing robomimic delta->absolute script.

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

`100 passed in 3.03s`

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
python -m pip install numpy scipy pytest
cd cst_research
python -m pytest -q test_*.py
```

For exact run IDs and evidence status, see `EVIDENCE_LEDGER.md`.


## Fork-native upstream path

The two independent external candidates are now in their native project forks,
not only staged inside the CST research branch:

- **robomimic #270:** `lindicaphxag-tech/robomimic`,
  clean branch `feature/absolute-to-delta-actions-270-pr`;
  latest focused semantic suite: **7 passed**.
- **LeRobot #3312:** `lindicaphxag-tech/lerobot`,
  clean branch `fix/act-relative-actions-3312-pr`;
  current-main focused ACT suite: **9 passed, 5 skipped**; final project
  pre-commit gate is being completed.

Neither branch counts as external adoption until an upstream maintainer reviews,
merges, or otherwise retains the contribution.


### PR-ready second and third stack candidates

**robomimic #270**
- maintainer-invited feature;
- clean 1-commit / 5-file PR-final branch;
- focused tests green;
- live robosuite 1.5.1 Panda OSC assay: max goal error `2.944e-08`,
  max recovered native-action error `4.814e-08`.

**LeRobot #3312**
- maintainer explicitly invited ACT support;
- rebased/audited on official main `ca69a206...`;
- clean 1-commit / 3-file PR-final branch;
- `8 passed, 5 skipped`; ruff all green;
- default ACT processor path is unchanged unless relative actions are explicitly
  enabled.

Neither candidate is upstream-reviewed or merged yet; GitHub App permissions
block upstream PR/review writes and require manual UI submission.


### Evidence added 2026-10-08

- Implementation: [fail-closed OSC handshake](executable_osc_migration.py)
  (`initial_joint` migration with explicit unsupported-mode refusals).
- [100-test deterministic public suite](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37709468190).
- [8-test real Panda/Lift, same-MJCF controller swap with full-scene numerical negative control](https://github.com/lindicaphxag-tech/robomimic/actions/runs/37706956215).
- External replication thread #77 has a new, falsifiable experimental
  update, including requests for *negative* reproductions.
- Official ManiSkill #429 RL-demo base/fix test is **in progress** and must
  not be counted as a successful policy demonstration without a completed
  result.

**Acceptance boundary:** No new external maintainer review/merge of this
research line and no independent replay yet. This is not a certified
hardware-safe policy migration.


## Live goal-history transport

- Goal-memory executable code:
  [`desired_osc_online_transport.py`](desired_osc_online_transport.py).
- Fail-closed missing-state and out-of-range refuse examples are included
  in the **100-test** [research suite](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37714476522).
- Real robosuite Panda/Lift and Stack six-trial state-complete
  action adapter:
  [15/15 physical tests](https://github.com/lindicaphxag-tech/robomimic/actions/runs/37713698317).
- Online desired OSC has a separate
  [17-test real validation](https://github.com/lindicaphxag-tech/robomimic/actions/runs/37714363692),
  subject to initial-goal-alignment follow-up.
- We do not claim frozen learned policy parity or independent
  maintainer adoption from these author-run experiments.


## Reviewed evidence as of 2026-10-08: frozen trained policies, not scripted actions

**Distinct from earlier scripted-controller tests**, a third-party
ActionShift-pretrained PPO (full SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`)
was loaded with **no training/fine-tuning** into official ManiSkill Panda
PickCube PhysX CPU. Every paired arm uses its own runtime observations.
The parent model is credited to ActionShift, not to us.

| Frozen-PPO experiment | Src | Adapter | Negative control |
|---|---:|---:|---:|
| Delta -> physical absolute EE controller; preregistered 32 seeds `10001..10032` | 32/32 | 31/32 | raw copy 0/32 |
| Achieved-delta -> target-history-relative delta; preregistered **different** 32 seeds `18001..18032` | 31/32 | **32/32** with bounded *non-exact* projection | raw copy 3/32 |
| Same target-history experiment: strict exact/refuse | 31/32 | **3/32** | 29/32 episodes refused |

- [Frozen delta->absolute CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505);
  [preregistered holdout, including failure seed 10014](FROZEN_PPO_32_SEED_HOLDOUT_RESULT_2026_10_08.md).
- [Frozen target-memory and feasibility CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37749474021);
  [frozen report with all negative cases](FROZEN_PPO_STATEFUL_FEASIBILITY_32_SEED_RESULT_2026_10_08.md).
  The target controller augments the observation from **42D to 49D**;
  the unchanged PPO receives its original 42D ABI while the runtime
  adapter reads the extra 7D memory. Hard action limits make one-step
  exact target transfer impossible in 29/32 episodes; the bounded
  adapter executed 31 `NOT_EXACT` action projections across those
  29 episodes. No task success implies precise trajectory equivalence.
- [Original-code reproducibility audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37749366189):
  seed 10014 original holdout failed compiled **12/12** isolated processes
  (source 12/12 at step 31). Instrumented diagnostic code previously
  changed both policy and controller episode trajectories, so we are
  examining state-getter side effects; mechanism not yet established.
- [External upstream-ready narrow patch for ManiSkill #429](https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/429-numpy-tensor-replay-minimal):
  type/shape bug, not claimed as semantic-normalization novelty.
  [Exact patch confirmed on 16 official RL demos](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715715576).
  This upstream fix is **not merged** and requires maintainer approval.

### Reviewer-critical missing evidence

A second competent frozen policy/task, controller-family generalization,
exact observation/controller ABI extraction independent of manual code
inspection, physical feasibility residual metrics, release-quality
standalone CPU reproduction, independent reproduction or code adoption.
Robot or patient safety and L8/L9 ranking have **not** been demonstrated.

**Closest research**: [ActionShift](https://github.com/Archerkattri/actionshift)
already addresses frozen policy action-interface adaptation including
target/frame/lag semantics; [RACE at ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/fab80bb9d97e9b9ff5c19f91f72838c6-Abstract-Conference.html)
already handles robot action execution time and physical reachability
constraints. Our more precise hypothesis is **runtime controller-owned
state + observation ABI preservation + infeasibility-aware action
execution**, but any broad originality claim requires independent
review against these and related works.
