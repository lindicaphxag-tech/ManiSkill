# ManiSkill #429 — Official RL demonstration replay: upstream baseline vs fixed converter

Date: 2026-10-08.  This is a *public, reproducible, scoped A/B experiment*,
not evidence of general controller-swap equivalence.

## Input and execution protocol

- Official ManiSkill `PickCube-v1` RL trajectory archive downloaded via
  `python -m mani_skill.utils.download_demo PickCube-v1 --quiet`.
- Source file in the archive:
  `rl/trajectory.none.pd_joint_delta_pos.physx_cuda.h5`.
- 997 source episodes in JSON metadata, all labeled `pd_joint_delta_pos`.
- **Identical input bytes** copied separately for baseline and patch; first
  8 episodes in each replay.
- Target control mode: `pd_joint_pos`.
- Simulator for this comparison: `physx_cpu`, not the source `physx_cuda`.
- `--use-first-env-state --save-traj --obs-mode none --count 8`.
- Baseline uses unmodified `origin/main`
  `mani_skill/trajectory/utils/actions/conversion.py`.
- Patch uses `fix/joint-delta-to-joint-pos-pr` production blob
  `15d127773e502ee58a3a6c3ac600deced681bf3d`.
- The exact production blob SHA was independently checked to match the
  candidate in the validation workflow.

## Canonical evidence

https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37709660093

The workflow retains `baseline_replay.log`, `patched_replay.log`, and
`comparison.json` as a downloadable Actions artifact.

### Baseline — cannot report task success rate

The unmodified converter fails at the very first official episode with:

```
TypeError: clip() received an invalid combination of arguments
- got (numpy.ndarray, int, int)
```

Trace: `from_pd_joint_delta_pos` calls
`gym_utils.clip_and_scale_action(ori_action_dict["arm"], low, high)`;
the runtime function expects a torch.Tensor but receives a NumPy action
row from the HDF5 trajectory.

This is a real pre-replay execution bug. It must **not** be reported as a
measured `0/8` task success rate, because the baseline crashes without
running to completion.

### Patched converter — 4 of 8 successful replays

With the corrected converter (NumPy-safe source scaling and target-native
action re-encoding), the same replay pipeline finishes:

```
Replayed 8 episodes, 4/8=50.00% demos saved
```

The 4 failures are episodes 2, 4, 6, and 7 under this CPU/backend
configuration. The workflow itself is green; it retained negative episode
results rather than dropping them.

This is **not** a general '50% lift' claim: source demos originated on
PhysX CUDA, replay took place on CPU, and simulation backend mismatch can
affect task success. No hardware policy was evaluated.

## Why the code fix matters

The patch addresses two distinct errors in this conversion path:
1. NumPy/Torch mismatch: source trajectories are NumPy rows, while
   `clip_and_scale_action` uses `torch.clip`.
2. Wrong target controller chart: the source normalized delta is decoded to
   physical `Δq`, added to the current source qpos, then re-encoded into
   the target `PDJointPosController` native action space.

Neither aspect proves all controller conversions can succeed.

## Maintainer-facing proposal

Now that a real official RL episode reproduces baseline crash and the
two-file patch runs through eight episodes, the next external action is to
ask the ManiSkill #429 maintainer to review the minimal diff:

https://github.com/lindicaphxag-tech/ManiSkill/compare/main...fix/joint-delta-to-joint-pos-pr

Do not attach the large CST research code to the production bug-fix PR.

## Research boundary

Separate robosuite Panda OSC results demonstrate a different, complementary
problem: controller-owned nullspace memory can affect real low-level torque
even when goal targets are numerically equivalent. Those results are in
`REAL_OSC_CAUSAL_HANDSHAKE_2026_10_08.md`. Neither case yet demonstrates
a frozen VLA checkpoint retaining success rate under arbitrary controller
changes or any universal formal guarantee.

External CST maintained adoption remains **0** until an upstream merge or
independent use occurs.


## Extended 16-episode validation — reported conservatively

A separate three-arm ablation was initiated with identical official
PickCube-v1 `pd_joint_delta_pos` source data on CPU, with
source SHA256
`b05851319021c290ed5e5055c03c776b434af5c9af98e13db2ab9159752b89c8`.

The first public run:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713457042

- Untouched upstream: **TypeError**, no valid success denominator.
- Full semantic patch: **7/16 successful demos saved (43.75%)**.
- One-line tensor-conversion-only branch: did not finish because it
  exposed a second 2D-vs-1D tensor shape failure. It cannot be scored as
  zero task success, nor used for a fair effect-size comparison.
- A type-and-shape-only baseline retaining the original wrong target
  controller chart was then prepared in a **separate** follow-up run:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713849790
  (not classified as a valid comparator until the run finishes and its
  full logs are checked).

Until a valid type/shape-only baseline finishes, we may claim that the
full semantic patch removes real execution errors and completes 7/16
official-data CPU replays, **not** that semantic re-encoding causally
raises task success by 43.75 percentage points.


## DECISIVE three-arm 16-episode ablation (valid control)

Canonical publicly successful workflow:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713849790

All three arms use **identical** official RL source file hash
`b05851319021c290ed5e5055c03c776b434af5c9af98e13db2ab9159752b89c8`.

| Arm | Status | Successfully saved |
|---|---|---|
| Untouched upstream `main` | Runtime `TypeError` on episode 1 | Not a valid task-success denominator |
| Minimal type+shape correction only | Full replay | **7/16 (43.75%)** |
| Expanded target-controller semantics patch | Full replay | **7/16 (43.75%)** |

**The two runnable arms fail on exactly the same 9 episodes.**
No task-success improvement from expanded target-chart encoding was detected
in this fixed configuration.

Direct source check of `mani_skill/agents/robots/panda/panda.py` on
upstream main confirms Panda's destination `arm_pd_joint_pos` has
`normalize_action=False` (physical joint-position targets), whereas the
source `arm_pd_joint_delta_pos` uses normalized bounded delta actions.
Consequently, the target does **not** double-normalize physical positions
under the default Panda configuration, contrary to the earlier hypothesis.

### Correction to initial project hypothesis

The **real demonstrated upstream bug** in #429 is the NumPy/Torch type and
1-D-vs-batched shape mismatch; the 2024 issue author already described
a NumPy/Torch typing problem. This work provides a clean minimal patch,
CPU regression and now controlled end-to-end public RL reproduction.

Do **not** claim that the type/shape bug was newly discovered, or that
the expanded semantic encoder raised success from 0% to 43.75%.

An honest, smaller recommended upstream PR candidate is therefore:
https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/429-numpy-tensor-replay-minimal
(single conversion function edit + focused regression).

The original expanded research patch is retained for API-level action
chart investigations, but should **not** be promoted as a task-success
improvement without a target controller that really uses a different chart.

A separate exact-minimal-blob official replay is being validated on
https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/mani429-minimal-official-replay-20261008
before asking an upstream maintainer for PR approval.
