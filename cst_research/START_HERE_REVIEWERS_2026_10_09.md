# Reviewer entry point — Controller-State Transport (CST)

**Revision 2026-10-09** · Public reproducible research prototype,
**not** a paper acceptance, formal hardware safety certificate, or
externally merged feature.

## One falsifiable claim

Moving a *frozen trained manipulation policy* between real simulator
controllers may require **both** (i) conversion of actions between native
controller charts and (ii) transfer/online reading of *controller-owned
goal history*. A controller can additionally make an otherwise valid
target **unrepresentable in one bounded control step**.

CST implements an execution-time state-aware action compiler. If the
desired command is outside the destination controller's representable
action set it distinguishes **REFUSE** (strict, preserves exactness
claims) from **APPROXIMATE_BOUNDED_PROJECTION** (changes the desired
action, keeps the closed-loop policy running, logs nonexactness).
The current geometry uses an elementary normalized-action
box/unit-ball projection. **Neither clipping, action-coordinate
conversion, controller-state machines, nor frozen-policy adaptation
is claimed to be invented here**.

### Strongest public discriminating tests

| Comparison (all real CPU sim) | Source | State-aware transfer | More direct negative control |
|---|---:|---:|---:|
| Frozen PPO / PickCube, one mode delta -> physical absolute, 32 prespecified initial seeds | 32/32 | 31/32 | Raw action copy 0/32 |
| Frozen PPO / PickCube, *previous-target memory* + bounded feasibility, **new 32 prespecified seeds 20001–20032** | 31/32 | **32/32** | Strict exact-or-refuse 5/32; raw copy 3/32 |
| Frozen PPO / PickCube, matched bounded projection but **previous goal replaced with achieved pose**, independent cohort | 31/32 | **32/32 memory-aware** | 2/32 memory-blind |
| Frozen PPO / PushCube, different public trained PPO, previous-target memory | 30/32 | **30/32 memory-aware** | 20/32 achieved-only |

All are **single-batch author-run**, closed-loop (policy acts on the
environment's own observations), physically stepped simulations with
public external pretrained checkpoints. Not hardware transfer and not
a multi-robot-family validation. The 32-seed pilot that returns
32/32 also includes **27 strict refusals** and **30 nonexact projected
actions**, so this is *not* a claim of exact trajectory reproduction.

**Evidence / scripts / raw CI:**
- [Frozen policy PickCube 32-seed delta->absolute CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505) and [failed seed 10014 preserved](FROZEN_PPO_32_SEED_HOLDOUT_RESULT_2026_10_08.md)
- [Stateful bounded feasibility 32-seed CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37814776505), [preregistration](TARGET_MEMORY_32_SEED_PROSPECTIVE_2026_10_09.md), [complete account of failures](FROZEN_PPO_TARGET_MEMORY_32_SEED_RESULTS_2026_10_09.md)
- [Previous-goal memory-only causal ablation CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751599480) and [results](FROZEN_STATE_MEMORY_ONLY_ABLATION_RESULT_2026_10_08.md)
- [Independent frozen PushCube PPO task CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37752524225) and [results](FROZEN_PUSH_CUBE_MEMORY_CROSS_TASK_RESULTS_2026_10_08.md)
- [Prior 48-seed stateful cohort CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37809684134) and [complete report](FROZEN_PPO_48_SEED_MEMORY_HOLDOUT_RESULT_2026_10_09.md)
- [Actual robosuite Panda Lift/Stack stateful OSC execution](https://github.com/lindicaphxag-tech/robomimic/actions/runs/37713698317), and [CPU reproducer](https://github.com/lindicaphxag-tech/robomimic/blob/validation/delta-actions-real-osc-20261008/research/reproduce_cst_cpu.sh)
- [Controller runtime state/rollback source](executable_osc_migration.py), [100-test public contract suite](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37714476522)

### Important counterevidence — instrumentation may affect the dynamics

The original minimally instrumented delta->absolute frozen-policy
holdout had a real failure on seed **10014**. In a separately published
test, original-source, isolated process repeats were **12/12 failed
on compiled target** with the same starting observation hash:
[unmodified repeatability CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37749366189).

A later *more heavily instrumented* diagnostic succeeded at seed
10014 on a separate run. This is **not** proof that the original bug
went away or that seeding was unreliable: read-only-looking calls
such as `get_qpos()` / TCP pose retrieval may alter lazy-state
synchronization. Dedicated independent-runner and getter-only causal
ablations are in progress:
- [multiple runners, same code/seed](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37815875425)
- [no getter vs joint getter vs TCP getter vs both](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37816366179)

**These runs must not be described as passed until their CI concludes.**
The original failure remains part of the scientific record.

## Relevant prior art and novelty ceiling

- [ActionShift](https://github.com/Archerkattri/actionshift)
  already offers frozen-policy action-contract adaptation, target,
  coordinate frames, lag, belief and bounded control. These are not
  sufficient novelty claims.
- [Demystifying Action Space Design for Robotic Manipulation Policies,
  ICML 2026](https://proceedings.mlr.press/v306/feng26ab.html)
  already demonstrates action-space design's large empirical impact.
- [LeRobot's current action representation definitions](https://huggingface.co/docs/lerobot/action_representations)
  already distinguish absolute, relative and delta actions, including
  temporal reference semantics.
- Bisimulation, controller-state mapping, fail-closed contracts,
  saturation and bounded projection are well-established ingredients.

The **remaining research hypothesis** is a reusable compiler that
extracts required runtime controller state from implementations,
maps a frozen policy's original observation/action ABI onto a new
implementation, explicitly certifies when exact one-step transfer is
possible, and authorizes *traceably nonexact* bounded repairs when not.
The current code is **specific to several known controller families**;
it is not yet a generally autonomous implementation-to-contract
compiler or a formal safety certification.

## Main external recognition opportunity

[ManiSkill #429](https://github.com/mani-skill/ManiSkill/issues/429)
exposed a real NumPy/Torch+shape bug in its
`pd_joint_delta_pos -> pd_joint_pos` replay. The verified *minimal*
upstream patch is [one commit and two files](https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/429-numpy-tensor-replay-minimal),
with [same-blob official 16-episode replay validation](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715715576).
The prior issue comment that hypothesized destination double-normalization
was incorrect for Panda's stock target mode; new evidence
**rejects that hypothesis**. The existing comment requires manual
correction (connector upstream write returns HTTP 403) before PR
submission under maintainer first-discussion norms.

The proposed upstream contribution is **not merged** and does not
prove the larger CST architecture has external adoption.

## What a skeptical reviewer should attempt

1. Reproduce seed 10014 with/without physical state accessors,
   including *identical* initial observation fingerprint and exact
   dependency versions. Report every failure.
2. Run the same bounded-memory compiler with held-out controller type,
   not just another random reset of Panda.
3. Hold identical observation adapter and action range when comparing
   live previous-goal memory vs achieved-only reference.
4. Report native out-of-range magnitude, action residual, refusal and
   projected success separately — never relabel a nonexact action
   as exact state equivalence.
5. Independently rebuild the environment and artifact, and submit
   counterexamples to the public [reproducibility thread #77](https://github.com/lindicaphxag-tech/lindicaphxag-tech/issues/77).

Maintainer approval, independent retention/replication, or peer-reviewed
publication must be reported as **unachieved until independently verified**.
