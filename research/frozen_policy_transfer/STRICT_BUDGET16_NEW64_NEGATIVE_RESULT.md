# Strict shared target-read budget — negative prospective 64-state PhysX study

**Original 2026-10-09 run. Status: ORIGINAL HARD INJECTION-EXPOSURE GATE FAILED.**
Author-operated ManiSkill PhysX CPU simulation, not independent reproduction, not a real physical dropped ACK, not a new CoRL/RSS research acceptance.

## Pre-outcome contract and transparent execution history

- Protocol **frozen BEFORE any new runner** at [commit a47fb2b7](https://github.com/lindicaphxag-tech/ManiSkill/commit/a47fb2b7eedcb90803bebe4845d47082b1a279da), Git blob `8394481a560ea3d0c538e9d2ebf46cc9c4949484`.
- Two original frozen external PPO checkpoints, original PullCube seeds `360001–360032` and StackCube `370001–370032`, each partitioned into **four ascending 8-seed shards**, 64 distinct original source reset states.
- Protocol holds source `pd_ee_delta_pose` and target `pd_ee_target_delta_pose`, frozen 0.05 m position and 0.05 rad rotation target-bound thresholds, forced **zero arm target delta at t=2**, up to 50 native PhysX steps, preserved gripper control.
- Two information policies share **two possible privileged target-read tokens per 8-state shard**. Fixed-state-independent schedule reads at `seed%4==0`, spending 16 reads across 64 states. Certificate-triggered new policy decrements one same-shard token only when no bounded shared command is certified; if none are left it refuses. This guarantees a **16-read maximum**, NOT 16 actual reads.
- [First raw implementation run 37895572472](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37895572472) **FAILED** with an uncaught `Unrepresentable target rotation` for a StackCube trial. The error was NOT deleted. The follow-up evaluator patch catches ONLY known impossible native translation/rotation actions, records exact refused action and flags task failure without stepping physically. No seed, observer error tolerance, action limits, frozen PPO, query tokens or fault timing changed. The patch was made **after the first error** and must be disclosed as such.
- [Fixed-evaluator first complete eight-shard source, run 37896670586](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37896670586), source head `9cc897f4738fbb8cc1b32d513bf73a66db5556a1`: all eight actual native nine-arm PhysX shards + independent full-denominator result auditor passed.

## What the fully retained original 64 task outcomes actually say

| Native genuine PhysX treatment | Original task successes | Actual privileged decision-time target reads |
|---|---:|---:|
| Unfaulted frozen PPO (competence reference) | 57/64 | 0 |
| Continuous true-target oracle during faulty execution | 61/64 | Repeated private access; not zero |
| Optimistically assume execution ACK arrived | 39/64 | 0 |
| Exact-common-action or refuse | 0/64 | 0 |
| Two-history bounded common action only | 41/64 | 0 |
| **Certificate-triggered bounded action, capped at 2 private reads per 8 states** | **50/64** | **10 (maximum 16)** |
| State-independent target read at frozen `seed%4==0` schedule | **44/64** | **16** |
| Certificate-triggered bounded action without cross-episode read cap | 56/64 | 19 |
| Mandatory once-per-fault target readback | 60/64 | 64 |

On the original 64 matched source reset states, capped versus pre-scheduled control recorded **nine capped-only task successes and three schedule-only successes**. Conditional exact two-sided binomial/McNemar value is **0.14599609375**, before adjustment for multiple follow-ups and **not statistically significant**. The observed read saving is `16−10 = 6` private target reads, with two independently fixed upper quota tokens per eight source states; it is NOT a per-trial matched 10-read budget and cannot be described as an exactly equal number of consumed observations.

Uncapped selective against schedule: **13 versus 1** exclusive successes, **56 versus 44** pooled successes, read counts **19 versus 16**, also subject to the failed original hard-fault gate. These numbers may be inspected descriptively, but are not approved prospective confirmatory evidence.

## Strong failure witness: target-chart *validity precedes history recovery*

At **StackCube seed 370029**, step zero (BEFORE frozen fault injection step two), the source-policy-derived target-native rotation delta satisfied some numeric chart operations but failed the strict action-history observer's SO(3) admissibility guard with `ValueError: Unrepresentable target rotation`. The **seven faulty-controller comparison arms** all refused at `t=0` and retained their unsuccessful official outcome. The source/no-fault reference can still run its own native action; those two facts MUST NOT be conflated.

Therefore the original strict scientific gate requiring **all 64 source states to encounter the intended fault** FAILED for seven original comparisons: only 63/64 relevant faults were physically injected. The full 64 intention-to-test reset-state denominator remains intact. Counting 63 actually fault-exposed conditions as 64, dropping seed 370029, or silently projecting a rotational action after seeing the failure would misrepresent what was tested. The auditor exposes `pre_fault_controller_refusal_witnesses`, `fault_exposure_counts` and `predeclared_primary_efficacy_inference_gate_PASSED=false`.

### Precision-level root cause (later diagnostic, NOT a post-hoc change to source episodes)

The illegal rotation was extremely close to, rather than far outside,
the unit ball. All seven original failure records independently print
`proposed_native_rotation_l2 = 1.0000009536743164` computed in
`float32`. The source converter's `normalized_target_delta`
has `TOL=1e-5` and allows marginal `amp<=1+TOL` without
executing its actual radial projection branch, whereas
`ActionHistoryObserver.prepare` converts the same transported action
to **float64** and refuses if the rotational Euclidean norm exceeds
`1+1e-6`. This is a *contract/tolerance/precision mismatch*, not
evidence the source converter entirely lacks rotation-ball clipping.

A fully deterministic minimal **mechanism reproducer** is the float32
rotation vector `[0.5773508548736572]*3`. NumPy's float32 norm is
`1.0000009536743164`, indistinguishable in the logged norm from the
real failure; casting its components to float64 before evaluating
the norm gives `1.0000010144344997`, which crosses the observer's
`1.000001` threshold. The original source JSON did **not** log the
three exact component values, so this reproduces the *failure
mechanism and printed float32 norm*, not an assertion of identical
unobserved original components.

The correct mitigation is not to raise both tolerances or relabel
the historical action as valid. Instead, test the actual float32
transmitted SO(3) radial domain before dispatch, explicitly project
INWARD if permitted, mark the command `NON_EXACT`, and **recompute
the true commanded target error across the full trusted history set**;
otherwise refuse. [Corrective typed-native prototype and six-OS/Python
CI](https://github.com/lindicaphxag-tech/ManiSkill/pull/103) is a
separate future method and has not repaired the original failed
frozen 64-state confirmation gate.
A deeper mechanism is visible here: the native normalized translational action may be constrained by a per-coordinate box, whereas the rotation-control chart/observer can impose a Euclidean **unit ball** on the three Euler-control coordinates. Componentwise clipping or separately testing `|a_i|<=1` **does not imply** `||a_rotation||_2<=1`, and applying a later native saturation without recomputing the controller-target error invalidates an exact target-memory promise. The failure does not prove a new optimization theorem, but motivates a **controller-typed representability-and-setpoint-error contract**. Any proposed repair or projector needs a newly preregistered cohort and a real matched simulator test, not tuning the current cohort.

## Research interpretation and external-review conclusion

1. **Scientific gate:** failed, so this is a **negative/descriptive** result. Do not use its conditional p-value as a confirmatory positive result or claim improved task success.
2. **Information cost:** a common 16-read *entitlement* was enforced. Only 10 reads were consumed by the quota-capped method; the comparator spent 16. The policies are not matched in realized observations.
3. **State/task units:** 64 separate reset states, but only two frozen pretrained task/PPO families on one Panda controller; each state has multiple correlated simulated arms.
4. **Hardware/task safety:** commanded-target bounds do not certify end-effector contact, collision, force, unmeasured ACK arrival, or hardware execution. At least one task source policy action became inadmissible before fault.
5. **Novelty and external adoption:** no independent research lab has rerun this nine-arm study; upstream ActionShift has belief/probe methods that remain competitive and are not yet matched against this particular fault with equal observation and action budgets.

### Reproduce the original negative evidence without any simulator

```bash
python -m research.audit_query_strict_budget64 \
  --input-dir research/frozen_policy_transfer/evidence/strict_shared_16read_quota_new64_negative \
  --output /tmp/strict_budget_new64_audit.json
```

Each raw original nine-arm, eight-seed JSON and eight source terminal logs are pinned by original SHA-256. In a separate no-GPU reviewer capsule, the unchanged original 17 files and checksum manifest can be verified before the archive reaches a trusted main branch. Running this audit checks arithmetic and provenance; it is **not** independently rerunning official PhysX.

**Next substantive experimental gate:** in a NEW frozen study, require source/target controller action chart representability before dispatch in *all nine arms*, with a documented rotation-ball projection and explicitly measured non-exact commanded-target error; compare matched queries at equal realized observation cost and count any noninjectable scene as a separate predeclared ITT failure rather than post-hoc removal.
