# CST evidence ledger — 2026-10-06

This ledger separates **method evidence**, **native simulator evidence**,
**upstream differential evidence**, and **external adoption**. A green workflow
is not automatically an accepted scientific claim.

## Current claim level

**L8 candidate only. L8 is not yet claimed. L9 is not claimed.**

External maintained adoption of CST: **0**.

The public upstream motivation is ManiSkill issue #429. The maintainer states
that exact action-space conversion is highly non-trivial and that the reported
0% delta-joint -> joint-position conversion looks like a bug. This repository
does not treat that statement as adoption or endorsement of CST.

## Accepted evidence

| Evidence | Frozen run | Result | What it supports |
|---|---|---|---|
| Semantic morphism classification | ManiSkill Actions #37389728690 | PASS | Exact equivalence / projection / target ambiguity / local unrepresentability can be distinguished in a shared observable space. |
| Stateful one-step controller semantics | ManiSkill Actions #37403825598 | 6/6 PASS | Absolute, delta-current and delta-target commands require different state semantics; hidden previous target can be necessary. |
| Trace-level state-machine compiler | ManiSkill Actions #37404181955 | 9/9 PASS | Whole traces can preserve a target-state relation, or fail closed at the first unrepresentable step; includes a 500-step zero-semantic-drift randomized case. |
| Chart-local saturation effects | ManiSkill Actions #37404910125 | 5/5 PASS | Clipping is not transferable by dimension/index alone and need not commute with cross-coordinate transport. |
| Native ManiSkill/PhysX delta-current -> absolute equivalence | ManiSkill Actions #37404638720 | 4/4 PASS | Real PDJointPosController instances on independent headless PhysX articulations receive equal physical targets and remain qpos/qvel equivalent after five physics substeps for four non-trivial normalized source actions. |
| Native hidden-state necessity / target-delta transport | ManiSkill Actions #37404990097 | 5/5 PASS total suite | A real target-delta controller is transported to an absolute controller over a multi-step sequence. Finite-stiffness tracking makes measured qpos diverge from the controller-owned previous target, so current-qpos stateless interpretation is observably wrong; state-aware transport preserves target/qpos/qvel equivalence. |
| Black-box closed-loop transport core | ManiSkill Actions #37407103809 | PASS | Minimum-residual executable-effect adapter synthesis, irreducible unit-action error lower bound, finite-horizon error propagation, two-scale black-box Jacobian estimation, and held-out counterexample refusal are executable and tested. |
| Native PhysX black-box controller certificate | ManiSkill Actions #37407148766 | PASS | From fresh independent headless PhysX rollouts, finite-difference executable effects recover the delta-current -> absolute joint adapter and pass held-out action perturbations in an augmented [qpos, qvel, target] observable without using analytic controller Jacobians. |

## Pending evidence

### Native stateful target-delta assay

Completed: ManiSkill Actions #37404990097, PASS.

The native suite contains four delta-current cases plus one multi-step
target-delta case (5/5 total). The target-delta case explicitly asserts that,
after the first finite-stiffness control interval, the controller-owned hidden
target differs from measured current qpos. A stateless current-relative
interpretation therefore predicts a different next target, while state-aware
transport continues to preserve source/target physical targets and qpos/qvel
under independent PhysX simulations.

### Strict upstream-base-fail / patch-pass differential

The first differential workflow (#37404740645) is **superseded and excluded**
from evidence. Although the patched branch passed and the upstream base failed,
the base initially failed because the test mock omitted
`config.lower/config.upper`, not at the intended NumPy/torch conversion
boundary.

The corrected strict differential is ManiSkill Actions **#37405088768** and is
accepted evidence:

- clean patch: the frozen reproducer passes **2/2**;
- current upstream main/base `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`:
  the same reproducer fails **2/2**;
- both upstream failures reach
  `gym_utils.clip_and_scale_action -> torch.clip` and raise the expected
  `TypeError` because the recorded trajectory arm action is a
  `numpy.ndarray`;
- the workflow itself refuses to pass unless that exact NumPy/torch boundary
  appears in the upstream failure log.

The upstream repository's current `main` head was independently checked and
is the same frozen SHA `62ff3a58...`, so this is not evidence against a stale
historical revision.

## External second-stack targets

### robomimic #270

Open request for absolute -> delta dataset action conversion. A maintainer has
publicly stated that a PR for this functionality is welcome.

Potential CST value: controller-semantic round-trip tests and explicit
rotation/controller conventions rather than component-wise subtraction.

Status: no user fork/adoption submitted from this work yet.

### IsaacLab #1548

Open bug on clipping semantics for task-space actions. A maintainer explicitly
acknowledges flaws in using the existing dictionary logic for non-joint
actions.

Potential CST value: saturation as a chart-local semantic effect. A joint
limit dictionary cannot be reused for task-space coordinates merely because
dimensions happen to match.

Status: no CST patch submitted; this is currently independent external
motivation, not adoption.

## Promotion gates

CST can move from L8-candidate toward an L8 claim only after:

1. ~~strict upstream-base-fail / clean-fix-pass evidence is green~~ — satisfied by #37405088768;
2. ~~native stateful necessity is green~~ — satisfied by #37404990097;
3. a minimal #429 patch receives maintainer technical confirmation or merge;
4. a second independent maintained stack reproduces the semantic failure or
   retains a CST-derived fix/test.

L9 additionally requires independent reuse or strong paper-level external
validation. More self-authored tests alone do not promote the level.


## Closed-loop extension status

A separate research branch `research/cst-closed-loop-v1` extends CST from
target-level semantic compilation to executable closed-loop effect transport.

Current accepted evidence on that branch:

- **#37407103809 — PASS:** local executable-effect image inclusion, minimum-residual adapter synthesis, irreducible error witness, finite-horizon error envelope, two-scale black-box effect estimation, and held-out falsification.
- **#37407148766 — PASS:** a native headless PhysX assay estimates the source and target executable effects from fresh simulator/controller rollouts and certifies the held-out delta-current -> absolute transport.

The closed-loop branch still remains **L8-candidate**. These are self-authored
validation results, not maintained external adoption. Promotion still requires
upstream retention and a second maintained stack.
