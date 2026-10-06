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
| Native 2-DoF held-out controller swap | ManiSkill Actions #37408526666 | 1/1 PASS | 4D state / 2D action serial PhysX articulation with unequal per-joint PD gains: all 6/6 held-out coupled state/action points improve; mean next-state error ratio 0.10363 (~9.65x lower than naive copying). The linear certificate remains approximate (unavoidable residual 3.108e-3), target effect rank=2. |
| Frozen-policy 30-step always-on CCLAT | ManiSkill Actions #37408718364 | FAIL (retained) | Always-on reuse of one local approximate adapter does not preserve the full frozen-policy rollout: mean error ratio 1.14492, terminal ratio 8.64355, despite slightly lower max transient error. This falsifies the claim that one-step improvement automatically composes over long horizons and motivates certified event-triggered/refusal semantics. |
| Calibrated dominance/refusal gate | ManiSkill Actions #37409250547 | 4/4 PASS | Empirical quadratic remainder envelopes gate transport only when adapted worst-case calibrated error is below fallback best-case calibrated error; overlapping intervals and out-of-domain queries fail closed. This is calibration evidence, not a global formal nonlinear bound. |
| Multi-rate common-horizon transport | ManiSkill Actions #37409246839 | 5/5 PASS | Zero-order-hold lifting compares controllers only after matching wall-clock horizon; exact continuous-dynamics discretizations at 20 Hz vs 100 Hz recover identity transport, gain shifts recover the correct action scaling, and unequal physical horizons are rejected. |
| Calibrated gated 30-step frozen-policy rollout | ManiSkill Actions #37409336635 | 1/1 PASS | After the frozen always-on negative, evidence-based switching intervenes 28/30 steps and refuses 2/30. Mean trajectory error ratio 0.73550 and max-error ratio 0.64188 versus naive passthrough; terminal absolute error remains <1e-6. This supports selective transport, not universal benefit. |
| Finite-sample risk-limited dominance gate | ManiSkill Actions #37455140291 | 6/6 PASS | Split-conformal residual bounds add explicit finite-sample resolution, calibration-domain, and familywise coverage checks. Insufficient samples, insufficient requested coverage, overlapping transport/fallback intervals, or out-of-domain queries fail closed. Coverage is marginal under exchangeability; this is not a global sequential safety guarantee. |
| Independent LeRobot anchor-lifetime differential | ManiSkill Actions #37455828589 | PASS | The same AST audit classifies official LeRobot pre-fix commit 240ea44c... as moving-anchor and official fix 7c98c1b... (#4057) as chunk-held anchor. This independently validates the hidden-state lifetime failure mode in a second maintained stack; it is not adoption of CCLAT code. |

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


### 2-DoF native extension

GitHub Actions **#37408526666** freezes a higher-dimensional native assay:
- common state: `[q1, q2, qdot1, qdot2]`;
- target action: two absolute joint targets;
- source gains: stiffness `[100, 80]`, damping `[10, 8]`;
- target gains: stiffness `[60, 120]`, damping `[6, 12]`;
- local A/B identified only at the origin;
- six coupled held-out state/action pairs evaluated without refitting.

Observed:
- mean naive next-state error: **1.016964639e-3**;
- mean CCLAT error: **1.053859192e-4**;
- ratio: **0.1036279** (~9.65x lower);
- improved held-out points: **6/6**;
- exact linear certificate: **false**;
- unavoidable operator residual: **3.10750082e-3**;
- target effect rank: **2**.

This materially strengthens the native evidence beyond the 1-DoF assay, but it
still does not establish task-level frozen-policy preservation; a separate
multi-step policy rollout gate is frozen and evaluated independently.


### Retained negative: always-on local transport

GitHub Actions **#37408718364** is a frozen failed gate and must remain in the
evidence record.

A single origin-linearized 2-DoF adapter was reused for 30 steps while the same
frozen state-feedback policy ran independently on source and target states.

Observed:
- mean naive trajectory error: **1.892317693e-4**;
- mean always-on CCLAT error: **2.166555507e-4**;
- mean ratio: **1.144921656** (worse);
- terminal naive error: **1.433861066e-9**;
- terminal CCLAT error: **1.239365334e-8**;
- terminal ratio: **8.643552457** (worse);
- max naive transient error: **2.100175524e-3**;
- max CCLAT transient error: **1.984665669e-3** (slightly better).

Interpretation: a useful approximate one-step transport does **not** compose
automatically over a policy rollout. Near the shared equilibrium, naive
controller mismatch becomes negligible while the approximate adapter can retain
a small structural bias. The failed run rules out an always-on local adapter as
the final method.

No threshold is changed after this result. The next method gate must decide
*before execution* when adaptation has a certified advantage over passthrough,
and must refuse/passthrough when that advantage cannot be established.
