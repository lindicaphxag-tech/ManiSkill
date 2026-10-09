# BeliefBridge task-gated controller-memory authority — NEW 64-state REAL PhysX result

**Completed 2026-10-09; candidate original systems research, NOT a peer-reviewed paper, a merged third-party contribution, actual robot hardware safety, or independent external laboratory reproduction.**

## One-sentence externally inspectable contribution

When two consecutive commands have uncertain delivery, the controller's last *commanded target* is hidden memory rather than the visible achieved tool pose. A conservative multi-history bounded-action adapter may continue or pay for an explicit private controller-state readback. **On an untouched, source-preregistered 64-state follow-up**, selecting the *entire* controller query regime **BEFORE reset** solely from the task label preserved fixed-query task success (**58/64**) with **56 rather than 64 privileged reads** (**12.5% fewer**). This is a small real observed efficiency gain, not a learned general-purpose decision policy or proof of noninferiority.

## Direct unchanged-source evidence: audit what actually executed

- **Frozen design committed before any fresh result:** [TASK_GATED_MULTI_ACK_FRESH64_V1.json](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/task-gated-ack-outside64-20261009/research/TASK_GATED_MULTI_ACK_FRESH64_V1.json), originally committed `1c2f0dd73471e2c234775ba39615fe5f3d4f8c59`. Git object blob `b4dbd98d73d2a22d9960c5b510e09f3927d63c0d`.
- **Full original native PhysX execution:** [run #37904539256](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37904539256), **9/9 jobs passed**. Eight original source sharded datasets with 8 task seeds each; 7 independently stepped controller arms per source seed.
- **Audit from all eight true originally emitted JSON artifacts:** [run #37905030000](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37905030000), **SUCCESS** and [all 64 individual rows and SHA source checks (artifact #11603559765)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37905030000/artifacts/11603559765).
- [Original run script](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/task-gated-ack-outside64-20261009/research/run_task_gated_multi_ack_fresh64.py), [independent-of-simulator audit](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/task-gated-ack-outside64-20261009/research/audit_task_gated_multi_ack_fresh64.py).
- Original unchanged v3 native controller source Git blob `99836af14205fe3e95e52a2e0d68237c7c8a9045` from real source-frozen commit `b7670dd17037bbb94d208a40a1e068ce972b5484`; multi-hypothesis setpoint checker source Git blob `36707a177549104ba5b4bd9bcebc76518f0d2840`. The published ActionShift pretrained PPO checkpoints are SHA-256 locked, and no PPO was retrained.

## Method and pre-outcome split

Development-only previous native PhysX cohort [#37900209486](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900209486) had 64 states: the fully reactive strategy completed 45/64 with 44 privileged target reads, while the scheduled read strategy completed 55/64 with 64 reads. StackCube specifically was 13/32 versus 23/32. This negative result motivated, **but does not validate**, the following elementary task-only routing rule:

- **PullCube:** keep the certified common native action until evidence indicates the current four-history controller belief cannot authorize it; then spend at most one measured privileged controller target read.
- **StackCube:** while the finite belief remains valid, follow the same bounded-command controller, then perform the single scheduled privileged read at t=4 if alive.

**New untouched holdout:** PullCube original reset seeds `520001–520032`, StackCube `530001–530032`, all precommitted. Each executes SEVEN actual separate ManiSkill native PhysX worlds. The task gate picks one **entire actually executed** source world before reset; there is no mid-trajectory splice, no retrospective seed-specific arm switch, no oracle-labeled actions, and no outcome-specific threshold tuning.

Two native commanded-arm **zero/hold** interventions occur at steps 2 and 3 with unknown execution acknowledgments; gripper is unaffected. The method physically exercises four distinct controller target-memory hypotheses; it supports up to sixteen in the code, but that larger number is **not** claimed as PhysX-tested. No physical robot or real packet-loss middleware was used.

## All new held-out results — complete original denominator

| Frozen policy and query regime | PullCube /32 | StackCube /32 | Total successes /64 | Actual privileged decision target reads |
|---|---:|---:|---:|---:|
| Bounded and never query | 8 | 4 | 12 | 0 |
| Fully reactive certify-or-query | 32 | 15 | 47 | 39 |
| Scheduled one target read at t=4 | 32 | 26 | **58** | **64** |
| **Precommitted task-gated route** | **32** | **26** | **58** | **56** |

**Exact paired native task outcomes for task-gated versus always scheduled:** 58 both succeed, 6 both fail, **zero discordances**, formal exploratory two-sided paired sign-test `p=1.0`. This is an *observed equal count and identical paired task labels*, not a mathematical guarantee of noninferiority or equal performance in a new population. Reading cost decreases `(64-56)/64=12.5%`; in PullCube the routed controller needs **24 instead of 32** readbacks without observed task success loss. StackCube uses the fixed arm (32 reads), succeeding **26/32**.

Original physical ledger: **1,779 genuine after-dispatch controller-target tolerance checks** were accepted within each certificate plus the source-code `1e-4` audit tolerance; **192 attempted commands were physically masked/held** by the injected intervention and **not** counted as physically certified actions. This is a conditional **commanded setpoint** check, NOT a trajectory, obstacle, contact-force or human safety result.

## External acceptance gate, strongest next technical falsifier

**What is already externally accepted:** this author's separately maintained Braindecode model ports and upstream maintainer-reviewed integrations. Those are independent engineering contributions; they do NOT constitute external scientific acceptance of this new robotics algorithm.

**What remains missing before a top research representative claim:** evaluate 3+ task/controller families or a genuinely different embodiment with independently trained/checkpointed policies; compare with a strong **resource-matched**, state-aware query controller beyond the known task label; demonstrate an actual learned or principled task/phase-aware information-value rule under faults other than two synthetic holds; obtain an *independent researcher-owned PhysX execution* in their own fork. The unseen 64-state result must remain untouched and must not be reused as training/development data.

**Bottom line:** an honest, reproducible improvement from a source-frozen real robotics-simulator study — **58/64 unchanged task successes for 56 instead of 64 private reads** — but not yet a globally novel, learned, externally validated L8/L9 method or a peer-reviewed paper.
