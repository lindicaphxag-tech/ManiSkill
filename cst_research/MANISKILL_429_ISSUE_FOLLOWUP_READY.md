# Issue #429 — reviewer/maintainer follow-up (manual posting required)

Issue: https://github.com/mani-skill/ManiSkill/issues/429

The GitHub connector could not write an upstream comment (403). Copy the
following into the official issue; **do not post it twice**.

---

Following up with a reproducible result on the exact conversion reported here.

I tested the unmodified upstream converter and a minimal two-file patch
against **the same first eight episodes** from ManiSkill's official PickCube-v1
RL demo archive (`pd_joint_delta_pos`, 997 source episodes). Both tests
replayed on `physx_cpu` using `--use-first-env-state`.

- **Unmodified upstream:** crashes on the very first trajectory with
  `TypeError: clip() ... got (numpy.ndarray, int, int)` from
  `gym_utils.clip_and_scale_action`. This is a NumPy/Torch API mismatch,
  so there is **no valid baseline task success rate** to compare.
- **Patched conversion:** replays all eight and saves **4/8** successful
  episodes without raising that exception.

The patch also fixes the controller-chart semantics by decoding normalized
source delta to physical `Δq`, composing with the current qpos, then
encoding the absolute target into the destination `PDJointPosController`
native action range.

**Full public A/B run, attached logs and machine-readable comparison:**
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37709660093

**Two-file patch branch:**
https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/joint-delta-to-joint-pos-pr

One caveat: the official source demos were generated on PhysX CUDA but this
public CI replay uses PhysX CPU; I would not treat the remaining four
unsuccessful episodes as proof of a converter bug without controlling backend
differences.

The candidate source file is byte-identical to the one that passed this
official-data validation.

Would this be an acceptable scope for a PR addressing #429? I can submit
the minimal diff and regression tests once a maintainer gives the go-ahead,
per the contribution guidelines.

---
