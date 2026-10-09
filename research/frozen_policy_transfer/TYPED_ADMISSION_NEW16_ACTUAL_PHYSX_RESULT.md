# Typed controller action admissibility before missing-ACK recovery — original NEW 16-state CPU PhysX result

**Author-operated original genuine ManiSkill CPU PhysX, 9 October 2026; public source freeze precedes results.** This is not independent outside-lab reproduction, peer review, hardware safety, or real lost network packets. It is not a rerun or positive reclassification of the separate **FAILED original hard-fault-exposure** 64-state study [negative results](STRICT_BUDGET16_NEW64_NEGATIVE_RESULT.md).

## Prespecified new-cohort decision

Predeclared source protocol: [typed-native new16 contract](../TYPED_CONTROLLER_ADMISSION_NEW16_PREOUTCOME_V1.json), exact Git blob `9f2ebf875412a0dce5a33c3e4dde6f03a76b734d` and commit `c4bdbafcdee54dd538cb32754a58c09cc42b410c`, **before** runner implementation or new PhysX outcomes. Two original SHA-256-pinned third-party ActionShift PPOs. NEW PullCube seeds **380001–380008** and NEW StackCube seeds **390001–390008**, one *actually delivered* native arm target-hold fault at zero-based simulator step **2** (ACK status hidden), seven additional control branches plus original reference. Unchanged native commanded-target error budget **0.05 m / 0.05 rad**, exact source pretrained policy, per-eight quota **2 target read tokens**, periodic read at `seed%4==0`.

[Original fully completed CPU PhysX nine-arm 16-reset-state run **37899357390**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37899357390) passed the separately committed pre-outcome hash freeze, both true external PPO task-world runners, and a standalone pure Python **all-16-denominator original-output auditor**. No executed episode was discarded.

**Hard validity gate PASSED.** All six required target-controller arms reached and genuinely physically executed the step-2 native target hold on **all 16 out of 16 actual task reset states**, with unknown ACK; the strict exact-only and continuously privileged oracle were also physically injected in all 16 original states. Thus this new intervention resolves the *evaluation cohort's missing-exposure problem* found in the earlier original study. It does **not** establish a general population guarantee that no further native action can ever be unrepresentable.

## Genuine PhysX results, every original outcome retained

| Controller arm | PullCube /8 | StackCube /8 | All original task successes /16 | Actual private target-memory reads |
| --- | ---: | ---: | ---: | ---: |
| Same frozen source model, no fault (context) | 8 | 6 | 14 | 0 |
| Oracle repeated target-memory accesses (context) | 8 | 7 | 15 | Unrestricted, encoded -1 |
| Optimistic assumed physical ACK | 7 | 5 | 12 | 0 |
| Exact common native action or refuse | 0 | 0 | 0 | 0 |
| Bounded common commanded-target action, never query | 8 | 5 | 13 | 0 |
| Uncapped evidence-triggered one trusted target query | 8 | 6 | 14 | 1 |
| **Precommitted per-eight quota, bounded-or-query** | **8** | **6** | **14** | **1 (max 4)** |
| **Fixed `seed%4==0` private target read** | **8** | **6** | **14** | **4** |
| Always one private target read at fault | 8 | 7 | 15 | 16 |

Crucial paired outcomes: quota-limited and fixed scheduling were **both successful on 13/16** cases; the quota method was uniquely successful at StackCube seed **390006** and fixed schedule uniquely at StackCube **390004**; both failed at StackCube **390008**. This is **1 versus 1** paired exclusive wins and provides **NO task-success superiority**; it does document a specific **fourfold reduction in the *count* of observed privileged state reads (1 versus 4)** at the same pooled official native task successes. Mandatory fault-time observation gains one extra successful task but requires 16 reads. Two original source-task failures without any fault occurred as well (source 14/16); do not state that every failure is due to an adapter.

## Real geometry-correctness result, not inflated by samples

The [actual typed native-action admission code and float32 physical-chart regression #104](https://github.com/lindicaphxag-tech/ManiSkill/pull/104) enforces the root-left controller action admissible product `[-1,1]^3 × {r: ||r||2≤1}`; checks a trusted native controller chart; refuses true rotation-ball excursions; and for only a tiny **2e-6** numerical overshoot may project into a float32-stable unit-ball interior, **measuring physical extra translation and SO(3) geodesic orientation distortion**. Each extra correction must lie at most within the predeclared **1e-5 m and 1e-5 rad** limits. If the action arose from a two-history **0.05 m / 0.05 rad** bounded certificate, this extra error must fit the *remaining* original target-error slack; otherwise the action is **refused rather than falsely certified**.

Across all nine native arms and time steps in 16 original episodes, the true runner logged **75 such small canonicalizations** and **zero typed native-action admission refusals**; these are **75 nested command events, NOT 75 independent experiments or model trials**. The main episode count is still 16; no real-robot trajectory, collision, motor force or controller dynamics safety is thereby certified. The source-policy frozen weights and normal observations were unchanged.

These numerical changes cannot be claimed to account causally for higher success versus the old separate 64-reset cohort: they were **different episodes**. The original old seed **370029** remains an auditable failed exposure; no posthoc substitution or “rescued 370029” claim is made.

## Reproduce and independently falsify

Source: [new exact nine-arm original model runner](../frozen_ppo_typed_gate_fresh16.py), [precommitted numbered protocol](../TYPED_CONTROLLER_ADMISSION_NEW16_PREOUTCOME_V1.json), [standalone all-case source auditor](../audit_typed_gate_fresh16.py), [genuine PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37899357390), and [full 16-case original artifact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37899357390/artifacts/11601855990). Raw original JSON and output file digests should also be permanently committed (byte-identical, not re-created) and their original GitHub artifact ZIP SHA-256 identities locked for outside verification.

Remaining serious science requirements: test **other controller chart semantics / robot embodiments**, independent outside-lab genuine PhysX execution on newly selected seeds, stronger ActionShift active-belief/probe baselines **at equal consumed information**, actual ack-delivery latency/drop/reorder mechanisms, model/task-stratified uncertainty and correctly certified physical interaction constraints. Do not label this work L8/L9 merely for source/CI count.
