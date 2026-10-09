# Three flagship gates — audited state, not completion

**Date:** 2026-10-09. **Status:** author-operated systems research; neither peer review nor independent external execution is claimed.

## A. Learned frozen-policy cross-embodiment task success — OPEN

Native Panda and xArm6 Robotiq controller-target correction has been demonstrated under PhysX. That is **not** the same as official frozen learned-policy task success on xArm6. Existing released PullCube/StackCube PPO experiments are Panda-family evaluations.

Acceptance requires a real, task-competent, independently published xArm6-robot matching frozen checkpoint with pinned model SHA256, verified observation ordering/normalization, gripper semantics, native controller chart and clean-task performance. Any mismatch must fail before physics. Run new source-frozen paired task rollouts with applied/held ACK truths, official success, original actions, complete faults, reads, public observations and all negative rows. Do not label a scripted native target correction as learned-policy transfer.

## B. Faithful and information-budget matched ActionShift-style comparator — OPEN

ActionShift DualABI adapts latent action-contract grammar via task-directed bounded probes and belief updates. Current method knows its controller chart and treats missing command execution status as latent. Relabeling the contract belief algorithm as an ACK-history adaptation baseline is **not faithful**.

Acceptance requires a precommitted physically executed comparator with the same initial reset, frozen task policy, fault truth, controller chart, time horizon, task-success scoring and source/hash. Charge per algorithm: private target-memory reads, extra public XYZ or rotational observations, physically actuated probe steps, probe displacement, task reward/termination and calibration data. Compare paired task outcomes and information-cost Pareto frontiers at the same vector budget. Offline reclassification of existing JSON cannot substitute for new native PhysX task trials.

## C. Outside-operator independent native PhysX reproduction — OPEN

An actual independent investigator must fork the public repository, select previously unused reset seeds before viewing results, and execute the pinned outside-disjoint-mixed-ack workflow from their own GitHub account. The 8-reset workflow runs real native ManiSkill physics with full negative records, model hashes and operator provenance, and checks first ACK applied/held while second is held. It is not the full 2x2 physical truth experiment. Report the outside-fork CI URL, seed choice, task success vector, faulty world exposure, public/privileged reads, confident wrong history labels and raw JSON SHA256. Author-operated CI is not independent replication.

Outside fork workflow: https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/outside-disjoint-mixed-ack-physx.yml
Outside-investigator invitation is in research PR #141: https://github.com/lindicaphxag-tech/ManiSkill/pull/141 (Issues is disabled on this author repo).

## Completed: source-locked 2x2 cost accounting (NOT new physics)

Source original real PhysX: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37919576643. Exactly 64 task/reset states, 8 per task and t2/t3 physical truth stratum, nine individually stepped control worlds per reset. Strict exact-refusal arm stops before the shared neutral probe, so do not claim all nine arms receive the probe.

An independent standard-library **source-only** re-aggregation in PR #141 validates public 55/64 successes and 50 private reads; task-aware 56/64 and 59 reads; fixed 57/64 and 64. The public controller uses 128 recorded XYZ observation events, obtains 14 confident full histories and zero observed incorrect labels. Paired success: 54 both, seven neither, one public-only, two strong-only. Unadjusted exact paired p=1.0 is not a proof of equality or noninferiority.

Declared observation-cost sensitivity, excluding hardware timing and calibration: public = 50*C_private+128*C_XYZ; task-aware = 59*C_private. Public wins on this **observation-cost-only** criterion when C_XYZ/C_private < 9/128 = 0.0703125, while still having one fewer successful task. No device-level latency or safety claim follows.

**No 'all three complete' claim until Gates A–C have genuine outcome and third-party provenance evidence.**