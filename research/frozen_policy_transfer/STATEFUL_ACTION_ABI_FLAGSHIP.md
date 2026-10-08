# Stateful Action-ABI Transport for Frozen Robot Policies (contributor research)

**Evidence-backed research representative · 2026-10-09 · owner-executed PhysX CPU simulation**

> A task policy may emit a valid 7-D action yet target a *different physical end-effector command* when moved between two operational-space controller semantics. We test whether recovering the **previous commanded target**, rather than simply converting scale and clipping, is necessary to transfer four frozen third-party policies without retraining.

**Status:** four task/checkpoint families with genuine closed-loop official ManiSkill task flags; **new PullCube and StackCube families were preregistered before outcomes**. There is **no external scientific validation, novel robot hardware study, universal VLA result, or physically certified safe control claim**.

## 1. The actual algorithmic object

The source policy is trained under `pd_ee_delta_pose`, i.e. intended displacement from the *achieved* end-effector pose. The destination `pd_ee_target_delta_pose` interprets a nominally similar displacement from its *previous commanded controller target*. These are different stateful action ABIs even when vector shape, dtype and legal numeric ranges coincide.

Given source action `a_t`, current achieved end-effector pose `X_t`, and destination controller's previous commanded target `G_{t-1}`, the compiler constructs the source's physical goal and solves the inverse destination command:

```text
source policy action a_t
        | exact source chart/normalization
        v
desired physical target = X_t ∘ decode_source(a_t)
        | compare to REAL G_{t-1}, not X_t
        v
destination-native action = encode_target(G_{t-1}^{-1} ∘ desired target)
        | explicit representability gate
        +-- representable --> EXACT-in-chart candidate
        |
        +-- out of target bounds --> REFUSE exact authority
                                   or bounded PROJECTION (NOT_EXACT)
        v
unchanged frozen policy, official destination PhysX rollout
```

The destination observation is also checked against actual controller state and projected back onto the original trained policy's observation ABI; the PPO weights never change. A bounded projection changes the desired physical command and is **never** mislabelled an exact geometric equivalence or a robot safety proof.

The matched **memory-blind intervention** retains the same frozen PPO, intended source physical goal, destination conversion, scaling and clipping, but replaces `G_{t-1}` by `X_t` *inside the inverse map*. The real destination controller still uses its true previous target. This isolates the value of correct target-history information **within this controller implementation**.

## 2. Actual four-task closed-loop findings

All rows refer to original official `info["success"]` task outcomes (up to 50 physical simulation steps) and **32 predefined source/task seeds per task**. The five arms are **paired within each seed**, not 5× independent samples. Every task uses a different public PPO checkpoint, with unchanged frozen weights.

| Native task / original task-state cohort | Source PPO | Direct action copy | Exact-only or refuse | Live target memory + bounded projection | Memory-blind + SAME bounded conversion | Exclusive wins, live vs blind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PickCube-v1, **22001–22032**, prospective mechanism control | 31/32 | 4/32 | 9/32 | **31/32** | 4/32 | **27 vs 0** |
| PushCube-v1, **41001–41032**, already exposed before the two-new-task extension | 29/32 | 21/32 | 28/32 | **29/32** | 20/32 | **11 vs 2** |
| PullCube-v1, **51001–51032**, prospective new task/checkpoint | 31/32 | 14/32 | 17/32 | **31/32** | 14/32 | **17 vs 0** |
| StackCube-v1, **61001–61032**, prospective new task/checkpoint | 28/32 | 0/32 | 11/32 | **30/32** | 0/32 | **30 vs 0** |

**Do not collapse the four tasks into one unqualified “128 independent policies” score.** They are four frozen policies in the *same ManiSkill Panda controller-family* ABI mismatch, with task-specific initial-state seeds and paired interventions. The PickCube row uses the dedicated third-cohort mechanism-ablation experiment, not its earlier exposed or confirmation numbers. PushCube is supporting evidence; PullCube/StackCube were the prospectively declared extension tests.

For the *two never-before-evaluated task/checkpoint families*, the frozen [protocol](https://github.com/lindicaphxag-tech/ManiSkill/commit/582e39206cedf3565217514b1fdc1872c1cffae7) specified **32 seeds per task, source policy competence ≥24/32, and live-memory vs blind net improvement ≥6/32**. Both families passed both gates without outcome-driven tuning. The actual selected source checkpoints, model SHA-256 and exactness/projection events appear in the original evidence.

**Known projection cost:** the PullCube corrected arm executed **15 NOT_EXACT** bounded projection steps and StackCube **33**; PickCube corrected control on its mechanism cohort executed **27**. The beneficial task outcomes do not mean exact source control was always reproduced.

## 3. Immutable evidence and reproducibility tiers

| Evidence | What is independently checkable | What it does NOT establish |
| --- | --- | --- |
| [PickCube mechanism CI 37814189680](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37814189680) | Genuine 32-state PhysX five-arm replay, frozen test and paired 27:0 discordants | A new robot-controller family or independent academic execution |
| [PushCube prospective run 37810502800](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37810502800) | Frozen-policy cross-controller results on an independent source-seed cohort | Unseen *task family* for the subsequent Pull/Stack experiment |
| [PullCube / StackCube original CI 37815152548](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37815152548) | Eight genuine 8-state PhysX jobs and one complete original 64-state auditor; **10/10 jobs successful** | Third-party replication |
| [Pull+Stack protocol and 9 source JSON SHA-256 values](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/action-abi-independent-pull-stack-replication-v1/research/ACTION_ABI_PULL_STACK_PROSPECTIVE_RESULT_V1.md) | Fixed cohort, signed model identities, raw source commitments, nonexact steps, failures | Proof that a future edited file equals its original without rehashing |
| [Permanent PullCube/StackCube nine-file source archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/pull_stack_new_task_64) | All nine original JSON bytes are now present on main after the [trusted-main archival commit](https://github.com/lindicaphxag-tech/ManiSkill/commit/45a81af78cb8fbd358f8aab7a0e0a2d417f46d0f), with SHA256 gates in [PR #60](https://github.com/lindicaphxag-tech/ManiSkill/pull/60) | Byte-level audit is not an independent rerun of the simulator or source-policy generalization |

**Repeat the exact source-run experiment, not a posthoc compressed summary.** The prior source commit `9ffa86c6d3a86d2cee44b6e13c560033a8b373cf` has the executable `research/frozen_ppo_target_memory.py`, four frozen chunks per new task, and the independent standard-library `research/action_abi_pull_stack_aggregate.py`.

After installing the original pinned ManiSkill runtime and external frozen checkpoints (the published Actions [workflow](https://github.com/lindicaphxag-tech/ManiSkill/blob/9ffa86c6d3a86d2cee44b6e13c560033a8b373cf/.github/workflows/action-abi-pull-stack-replication.yml) is the authoritative environment recipe), an independent reproducer can execute one original eight-seed subset from the repo root:

```bash
git checkout 9ffa86c6d3a86d2cee44b6e13c560033a8b373cf
ABI_TASK=pull_cube ABI_CHUNK=0 python research/frozen_ppo_target_memory.py
# For all original 64 task states, run task=pull_cube/stack_cube,
# chunk=0/1/2/3; preserve all 8 JSON files.
python -m research.action_abi_pull_stack_aggregate \
  --input-dir <directory-with-eight-original-jsons> \
  --output audit.json
```

Reusing the same seed numbers is a **code replication**, not an independent seed generalization. New seeds should be frozen *before running* and reported with every negative/aborted episode. Exact external checkpoint IDs and hashes are in the [protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/582e39206cedf3565217514b1fdc1872c1cffae7/research/ACTION_ABI_PULL_STACK_PREREGISTERED_V1.json).

**External reviewer invitation:** [public external replication and falsification issue #67](https://github.com/lindicaphxag-tech/kaggle/issues/67). An issue is an invitation, **not external endorsement**.

## 4. Where the scientific contribution may and may not lie

The possible contribution is **state-conditioned operational semantics at the policy/controller boundary**, with an executable inverse controller chart, exact/refusal/inexact authority distinction, and a controlled memory-deletion intervention on actual frozen-policy trajectories. Its strongest evidence is **the causal simulator contrast within each task**, not a generic claim that action spaces are important.

This is **not** the first robot action adapter. In particular, [SPACE (2026)](https://arxiv.org/abs/2606.24049) explicitly studies Cartesian action representations and robot-specific adaptation; [TAM (CoRL 2026)](https://arxiv.org/abs/2606.06218) learns a policy-agnostic torque adaptor and includes real-robot transfer. These cover broader aspects of controller/robot mismatch. Neither should be misrepresented as the same algorithm, nor ignored when claiming novelty. The current project only isolates a *known controller-chart and target-memory mechanism*, not hidden ABI discovery under uncertainty.

The **missing high-tier originality gates** are concrete:
1. Transfer into an **independently maintained, different controller implementation** with a distinct state/history convention. The present four policies do not cover that axis.
2. Compare to **strong source-aware adapters** (including a model-state observer, learned delta adapter and feasible exact conversion), with equal online information and matched compute/data budget, not only naive and intentionally memory-blind controls.
3. Report end-effector tracking deviation, contact/actuation-limit violations, refusal exposure and bounded-projection dosage, alongside official task success. Success ≠ safe robot motion.
4. Repeat with **fresh frozen seeds and independent executor**, preserving failures, source checkpoint hashes and output artifacts; demonstrate inability to reproduce if it occurs.

**Assessment boundary:** four real task families with unusually clear interventions make a credible **flagship research-engineering artifact** and a strong basis for a paper. It is not presently a peer-reviewed CoRL/RSS/ICRA method, a first-of-kind theoretical result, a VLA foundation model, a hardware-validated algorithm, or confirmed third-party adoption.
