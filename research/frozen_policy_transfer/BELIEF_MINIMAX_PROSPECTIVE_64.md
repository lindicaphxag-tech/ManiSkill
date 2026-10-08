# Frozen PPO under unknown execution: prospective 64-case zero-readback midpoint falsification

**Status: Original eight-job, all-case true ManiSkill PhysX simulation, author-operated. Negative results included. Not peer-reviewed or endorsed by upstream.**

- **Prespecified BEFORE runner implementation and any of these outcomes:** [commit 495e76e5](https://github.com/lindicaphxag-tech/ManiSkill/commit/495e76e5d95ca0c309449f544b9c61c727b4bd22), immutable protocol Git blob `b5b2b03a45919d39aa37e38a20bf1ce2deb557a2`. Two third-party frozen ActionShift PPO models, their original model hashes, all 32 *unique* initial source states, the two paired fault conditions, fault step=2, comparator identities, and retention of all failures locked in.
- **Original eight PhysX CPU CI jobs all SUCCESS:** [run 37825781536](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536), exact evaluation commit `157c216deda38707a7f719368852d91964883d59`.
- **Denominator:** 32 unique seeds, each evaluated under BOTH fault conditions = 64 paired **task×seed×fault** records. They are **NOT 64 independent reset states**; treat seeds as paired clusters if carrying out statistical inference.
- **Actual intervention:** at timestep 2, action is physically applied or replaced by zero normalized arm delta via the official `env.step`, while the policy gripper action is unchanged; the adapter gets UNKNOWN acknowledgement in both conditions. This is a simulated native controller intervention, NOT real network packet loss, accidental physical hardware malfunction, or independent laboratory reproduction.
- **Robust candidate:** retain two possible previous target poses; midpoint their translations and SO(3) geodesic orientations, inverse convert desired source EE goal relative to this midpoint, bounded native project on out-of-range action, then advance *both* hypotheses on all subsequently acknowledged commands. **Zero private target readbacks during the decision loop**. It is a valid tested approximation rather than a universal optimal, exact, collision-safe or published-first controller.
- **Actual target audit:** all 64 robust episodes had two distinct plausible belief histories after the unknown ACK, and zero controller readback queries. Max closest-to-true terminal target position residual was **8.344650e-8 m**, measured **only after all actions**. Target belief inclusion does NOT bound achieved robot trajectory error or collisions.

## All-case actual native task-success flags

| Comparator | Paired task×seed×fault successes |
|---|---:|
| Unmodified frozen PPO on clean achieved-relative source control | 60/64 |
| Privileged live-memory target control, under fault | 61/64 |
| **ONE trusted target-state readback after unknown ACK** | **62/64** |
| ZERO-readback **optimistic** (assume executed) | 48/64 |
| ZERO-readback **pessimistic** (assume not executed) | 43/64 |
| ZERO-readback **two-target midpoint candidate** | **43/64** |
| No additional evidence: stop/refuse | 0/64 |

Actual fault target was reached on every registered episode/arm: **true**. One-readback uses strictly MORE controller information and cannot serve as matched-information superiority proof against zero-readback methods. The strictly refusing method stops with zero task completions and is not a recovery method.

Midpoint vs **optimistic** paired discordance: 11 midpoint-only / 16 optimistic-only. Midpoint vs **pessimistic**: 4 midpoint-only / 4 pessimistic-only. Midpoint vs **one-readback**: 0 midpoint-only / 19 readback-only. These disprove the simple idea that an SE(3) midpoint makes authoritative target memory redundant.

## Complete eight original preregistered subsets

| Task | Native fault | Seed chunk (8 each) | Source | Guess executed | Guess neutral | Midpoint zero-readback | One readback | Privileged oracle |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| pull_cube | Delivered | 0 | 7 | 7 | 4 | **4** | 7 | 7 |
| pull_cube | Delivered | 1 | 8 | 8 | 6 | **6** | 8 | 8 |
| pull_cube | Neutral hold | 0 | 7 | 6 | 8 | **8** | 8 | 8 |
| pull_cube | Neutral hold | 1 | 8 | 6 | 8 | **8** | 8 | 8 |
| stack_cube | Delivered | 0 | 8 | 8 | 1 | **3** | 8 | 7 |
| stack_cube | Delivered | 1 | 7 | 7 | 0 | **1** | 7 | 7 |
| stack_cube | Neutral hold | 0 | 8 | 3 | 8 | **6** | 8 | 8 |
| stack_cube | Neutral hold | 1 | 7 | 3 | 8 | **7** | 8 | 8 |

The *same midpoint method* behaves differently depending on whether the command was physically executed, even though it receives the same unknown acknowledgement. The negative result is mechanism-relevant: minimize geometric worst-case target error does NOT in general minimize downstream nonlinear task failure or interaction risk.

## All 64 original per-state records transcribed from original CI stdout

Official task success is the bool OR over simulator native `info["success"]` under the unchanged frozen horizon; projected actions are `NON_EXACT`.

| Task | Actual fault | Seed | Source | Optimistic | Pessimistic | Zero-read midpoint | One readback | Midpoint projected actions | True target contained error (m) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Stack | applied | 96001 | 1 | 1 | 1 | 1 | 1 | 1 | 2.98e-9 |
| Stack | applied | 96002 | 1 | 1 | 1 | 1 | 1 | 0 | 1.49e-9 |
| Stack | applied | 96003 | 0 | 0 | 0 | 0 | 0 | 0 | 2.38e-8 |
| Stack | applied | 96004 | 1 | 1 | 0 | 0 | 1 | 0 | 2.38e-8 |
| Stack | applied | 96005 | 1 | 1 | 0 | 0 | 1 | 0 | 2.38e-8 |
| Stack | applied | 96006 | 1 | 1 | 0 | 0 | 1 | 0 | 2.38e-8 |
| Stack | applied | 96007 | 1 | 1 | 1 | 1 | 1 | 2 | 2.38e-8 |
| Stack | applied | 96008 | 1 | 1 | 1 | 1 | 1 | 2 | 5.96e-9 |
| Stack | applied | 96009 | 1 | 1 | 1 | 1 | 1 | 1 | 2.38e-8 |
| Stack | applied | 96010 | 1 | 1 | 0 | 0 | 1 | 0 | 2.38e-8 |
| Stack | applied | 96011 | 1 | 1 | 0 | 0 | 1 | 0 | 2.38e-8 |
| Stack | applied | 96012 | 1 | 1 | 1 | 1 | 1 | 2 | 7.45e-9 |
| Stack | applied | 96013 | 1 | 1 | 1 | 1 | 1 | 1 | 2.98e-9 |
| Stack | applied | 96014 | 1 | 1 | 1 | 1 | 1 | 1 | 1.49e-9 |
| Stack | applied | 96015 | 1 | 1 | 1 | 1 | 1 | 0 | 2.38e-8 |
| Stack | applied | 96016 | 1 | 1 | 1 | 1 | 1 | 1 | 1.49e-9 |
| Stack | held | 96001 | 1 | 1 | 1 | 1 | 1 | 1 | 2.98e-8 |
| Stack | held | 96002 | 1 | 1 | 1 | 1 | 1 | 1 | 1.49e-9 |
| Stack | held | 96003 | 0 | 0 | 1 | 1 | 1 | 1 | 8.85e-9 |
| Stack | held | 96004 | 1 | 1 | 1 | 1 | 1 | 2 | 1.49e-9 |
| Stack | held | 96005 | 1 | 0 | 1 | 1 | 1 | 1 | 4.47e-9 |
| Stack | held | 96006 | 1 | 1 | 1 | 1 | 1 | 1 | 7.45e-10 |
| Stack | held | 96007 | 1 | 1 | 1 | 1 | 1 | 1 | 5.36e-8 |
| Stack | held | 96008 | 1 | 1 | 1 | 1 | 1 | 0 | 5.96e-8 |
| Stack | held | 96009 | 1 | 1 | 1 | 1 | 1 | 0 | 2.38e-8 |
| Stack | held | 96010 | 1 | 0 | 1 | 1 | 1 | 2 | 3.54e-9 |
| Stack | held | 96011 | 1 | 0 | 1 | 1 | 1 | 0 | 2.38e-8 |
| Stack | held | 96012 | 1 | 1 | 1 | 1 | 1 | 1 | 5.96e-9 |
| Stack | held | 96013 | 1 | 1 | 1 | 1 | 1 | 1 | 1.49e-9 |
| Stack | held | 96014 | 1 | 1 | 1 | 1 | 1 | 1 | 2.98e-8 |
| Stack | held | 96015 | 1 | 1 | 1 | 1 | 1 | 0 | 2.38e-8 |
| Stack | held | 96016 | 1 | 1 | 1 | 1 | 1 | 0 | 5.96e-9 |
| Stack | applied | 97001 | 1 | 1 | 0 | 1 | 1 | 1 | 5.96e-9 |
| Stack | applied | 97002 | 1 | 1 | 0 | 0 | 1 | 0 | 2.24e-8 |
| Stack | applied | 97003 | 1 | 1 | 0 | 1 | 1 | 3 | 2.98e-8 |
| Stack | applied | 97004 | 1 | 1 | 0 | 0 | 1 | 0 | 5.36e-8 |
| Stack | applied | 97005 | 1 | 1 | 0 | 0 | 1 | 2 | 2.38e-8 |
| Stack | applied | 97006 | 1 | 1 | 0 | 0 | 1 | 1 | 2.38e-8 |
| Stack | applied | 97007 | 1 | 1 | 1 | 0 | 1 | 1 | 2.11e-9 |
| Stack | applied | 97008 | 1 | 1 | 0 | 1 | 1 | 1 | 5.40e-9 |
| Stack | applied | 97009 | 1 | 1 | 0 | 0 | 1 | 1 | 5.96e-9 |
| Stack | applied | 97010 | 0 | 0 | 0 | 0 | 0 | 0 | 5.96e-9 |
| Stack | applied | 97011 | 1 | 1 | 0 | 0 | 1 | 1 | 1.42e-8 |
| Stack | applied | 97012 | 1 | 1 | 0 | 0 | 1 | 1 | 1.49e-9 |
| Stack | applied | 97013 | 1 | 1 | 0 | 1 | 1 | 1 | 1.19e-8 |
| Stack | applied | 97014 | 1 | 1 | 0 | 0 | 1 | 0 | 4.47e-9 |
| Stack | applied | 97015 | 1 | 1 | 0 | 0 | 1 | 1 | 6.71e-9 |
| Stack | applied | 97016 | 1 | 1 | 0 | 0 | 1 | 0 | 3.09e-8 |
| Stack | held | 97001 | 1 | 1 | 1 | 1 | 1 | 2 | 1.43e-8 |
| Stack | held | 97002 | 1 | 0 | 1 | 1 | 1 | 0 | 2.72e-8 |
| Stack | held | 97003 | 1 | 1 | 1 | 1 | 1 | 1 | 2.98e-8 |
| Stack | held | 97004 | 1 | 0 | 1 | 1 | 1 | 1 | 2.38e-8 |
| Stack | held | 97005 | 1 | 1 | 1 | 1 | 1 | 1 | 8.94e-9 |
| Stack | held | 97006 | 1 | 0 | 1 | 0 | 1 | 0 | 8.34e-8 |
| Stack | held | 97007 | 1 | 0 | 1 | 1 | 1 | 1 | 9.81e-9 |
| Stack | held | 97008 | 1 | 0 | 1 | 0 | 1 | 3 | 5.96e-9 |
| Stack | held | 97009 | 1 | 1 | 1 | 1 | 1 | 1 | 8.01e-9 |
| Stack | held | 97010 | 0 | 0 | 1 | 0 | 1 | 1 | 5.96e-8 |
| Stack | held | 97011 | 1 | 0 | 1 | 1 | 1 | 0 | 1.34e-8 |
| Stack | held | 97012 | 1 | 1 | 1 | 1 | 1 | 1 | 1.49e-8 |
| Stack | held | 97013 | 1 | 1 | 1 | 1 | 1 | 1 | 8.20e-9 |
| Stack | held | 97014 | 1 | 0 | 1 | 1 | 1 | 1 | 1.08e-8 |
| Stack | held | 97015 | 1 | 0 | 1 | 1 | 1 | 1 | 1.49e-9 |
| Stack | held | 97016 | 1 | 0 | 1 | 1 | 1 | 1 | 6.71e-9 |

## Eight independently inspectable original artifact bundles

All eight include original per-state JSON, complete original console log, and `pip freeze`. GitHub Actions artifacts expire under repository retention rules: links below are the original source, **not guaranteed permanent raw-byte archives**.

- pull_cube applied_no_ack chunk 0: [original source artifact 11570699800](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11570699800)
- pull_cube applied_no_ack chunk 1: [original source artifact 11571381892](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11571381892)
- pull_cube neutral_arm_delta_no_ack chunk 0: [original source artifact 11571377018](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11571377018)
- pull_cube neutral_arm_delta_no_ack chunk 1: [original source artifact 11571555845](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11571555845)
- stack_cube applied_no_ack chunk 0: [original source artifact 11570758921](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11570758921)
- stack_cube applied_no_ack chunk 1: [original source artifact 11570844354](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11570844354)
- stack_cube neutral_arm_delta_no_ack chunk 0: [original source artifact 11571720650](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11571720650)
- stack_cube neutral_arm_delta_no_ack chunk 1: [original source artifact 11571940412](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37825781536/artifacts/11571940412)

## What would justify a high-tier paper rather than a new self-merged PR?

1. Independent third-party execution or maintained benchmark integration, with a genuine second robot/controller ABI and unmodified data/ckpt provenance.
2. Delayed, reordered, lost or corrupted action receipts in true distributed control with independently authenticated target readback; compare no-query, fixed-query and budgeted active-query baselines with **identical information and compute**.
3. Measure task-level success AND setpoint error, achieved joint/EE trajectory, contact/collision, intervention latency, saturation and authorization false positives. Do not call exact target tracking a safety guarantee.
4. Compare meaningful learned/adaptive/robust baselines, not just guessing, and preregister frozen independent holdouts without changing acceptance rules after this negative result.
5. Explicit baseline compatibility with ActionShift's existing contract-belief and delayed-control work: target-memory synchronization is the gap, not a claim that history/belief/SE3 midpoint or action adaptation is newly invented.

**Final falsification:** even though belief propagation retained the true controller target in all cases, this model failed to outperform its matched zero-readback baselines in pooled task success. This is an important negative conclusion and should not be hidden behind cherry-picked neutral-hold gains. Contributor-fork merge is NOT external upstream endorsement.
