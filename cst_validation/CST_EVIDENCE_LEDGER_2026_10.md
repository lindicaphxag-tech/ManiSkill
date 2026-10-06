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
| Closed-loop transport synthesis + impossibility witness | ManiSkill Actions #37407305028 | 8/8 PASS | A local state-feedback adapter can be synthesized when target input effects span the required source dynamics/action directions; otherwise the method returns a structural witness and propagates residuals into an H-step deviation bound. |
| Native held-out closed-loop controller swap | ManiSkill Actions #37408214302 | 3/3 PASS | Different PD gains (source 100/10, target 60/6): CCLAT improves all 6 held-out PhysX state/action points; mean next-state error ratio 0.09663 (about 10.35x lower than naive action copying), worst ratio 0.10766. The local certificate correctly remains approximate, with unavoidable operator residual 4.936e-4. An identical-controller control case is exact, while a zero-stiffness target is rejected fail-closed. |

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

## Closed-loop promotion status

- Local method / impossibility witness: satisfied.
- Native nonlinear held-out controller swap: satisfied by #37408214302.
- Native negative unactuated-target calibration: satisfied in the same run.
- Multi-DOF/task-level held-out transport: pending.
- Maintained external retention: pending.

## Promotion gates

CST can move from L8-candidate toward an L8 claim only after:

1. ~~strict upstream-base-fail / clean-fix-pass evidence is green~~ — satisfied by #37405088768;
2. ~~native stateful necessity is green~~ — satisfied by #37404990097;
3. a minimal #429 patch receives maintainer technical confirmation or merge;
4. a second independent maintained stack reproduces the semantic failure or
   retains a CST-derived fix/test.

L9 additionally requires independent reuse or strong paper-level external
validation. More self-authored tests alone do not promote the level.


### Closed-loop CCLAT gate

Frozen method spec: `cst_validation/CCLAT_METHOD_V0_1.md`.

Accepted method evidence: ManiSkill Actions **#37407305028**, 8/8 PASS.

The closed-loop layer synthesizes a local state-feedback adapter

    u_tgt = K_x x_tgt + K_u u_src

and checks whether `[A_src - A_tgt, B_src]` is representable in the target
controller input image. When it is not, the implementation returns the dominant
unavoidable residual direction instead of reporting optimizer failure. The
finite-horizon certificate propagates the frozen one-step residual under a
declared local state/action radius.

The model-level result is now paired with a frozen native PhysX assay,
GitHub Actions **#37408214302**. Two real one-joint PD controllers use different
gains (source stiffness/damping 100/10; target 60/6). Local finite differences
at the origin are the only data used to synthesize the adapter. Six held-out
state/action pairs are then evaluated without refitting.

Observed mean next-state error:
- naive source-action copying: 1.664304752e-4;
- CCLAT transport: 1.608163168e-5;
- ratio: **0.0966267** (~10.35x lower).

Every held-out case improves; the worst transported/naive ratio is **0.107657**.
Importantly, the linear certificate is **not exact**: the frozen unavoidable
operator residual is **4.9362753e-4**. The evidence therefore supports useful
approximate compensation rather than a false exact-equivalence claim.

The same native suite also includes:
- identical source/target controller gains -> exact transport control case;
- zero target stiffness -> target action has no position authority and CCLAT
  rejects the pair fail-closed.

This remains a local/small-system nonlinear assay, not a global robot-safety
guarantee or a claim of task-level policy preservation.
