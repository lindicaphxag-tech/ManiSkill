# Reviewer decision page — controller memory authority under unknown execution

**9 October 2026 · evidence-only research note · author-controlled ManiSkill PhysX; not independently reproduced or peer reviewed.**

## One falsifiable question

After **two separate unknown arm-command acknowledgements**, a target-accumulating controller may carry **four distinct, physically plausible last-commanded target histories** even when a frozen policy's action numerically fits the target controller ABI. A robust common action can bound *commanded setpoint error* over all four histories but cannot guarantee **contact-rich manipulation success**. Is it better to defer a true controller-target state read until that bound fails, or to read earlier, before task-relevant motions?

## Hard negative that changes the project

The 64-real-state native PhysX study on PullCube 420001–420032 and StackCube 430001–430032 used identical frozen external PPO model weights and two actual target-hold events (`t=2,t=3`), not virtual action arithmetic. Reactive query-on-certificate-refusal completed **45/64** tasks with **44** real private target reads, whereas fixed early read completed **55/64** with **64** reads. Twelve... No: the exact pairwise discordance is **reactive-only 3, early-read-only 13**. An elementary source-independent root-frame isometry shows all candidate target-memory separation is invariant under *the same known common command*. Hence an authorized action does not intrinsically reduce uncertainty, nor certify task success.

[Original negative and transparent task-specific strata](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/ORIGINAL_64_STRONG_QUERY_TIMING_BASELINE_AND_INVARIANT.md).

## 64 NEW unseen state verification of the strongest simple control

From earlier development outcomes ONLY, we froze a deliberately trivial rule:

- On **PullCube**, use the source-frozen K=4 bounded action and query only when the target setpoint certificate refuses.
- On **StackCube**, perform the source-frozen one true target read at the first post-fault control step.

This route was selected **before seeing any outcome** from new PullCube 520001–520032 and StackCube 530001–530032. The pairwise original native-Panda study executed **seven separate PhysX controller worlds at every seed**; the router selects an entire actually executed original treatment based solely on known task ID. It is **not** an eighth physically executed fused controller, and it does not splice per-step counterfactual state.

| Actual prospective original treatment | Official successes | Privileged target-state decision reads |
|---|---:|---:|
| Reactive on both tasks | 47/64 | 39 |
| Early target read on both tasks | **58/64** | 64 |
| **Task-only preregistered route** | **58/64** | **56** |
| K=4 bounded control, no read | 12/64 | 0 |
| Original unfaulted source PPO | 59/64 | 0 |

Task-only routing matches **every individual binary success/failure flag** of early read, saves **8/64 = 12.5%** of the observed privileged target reads, and is not an untested paper algorithm. But 0 paired discordances on only two pretrained task families does **NOT** establish population non-inferiority or safety. The saving is modest; a novel complicated active query policy must beat it in prespecified task-success/readback-cost tradeoffs to justify its complexity.

## Three reproducibility routes

**No simulator or special Python packages:**

```bash
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
python -m research.audit_task_gated_multi_ack_new64 \
  --input-dir research/frozen_policy_transfer/evidence/task_gated_double_ack_64_520001_530032 \
  --output /tmp/new64_task_only_audit.json
python -m unittest discover -s tests -p test_task_gated_multi_ack_source_audit.py -v
```

These verify **all eight original source SHA-256 digests, 64 distinct reset states, 448 authentic source-specified native controller-world rollouts, four-history/fault exposure, correct task routing and no hidden free target read**; they do NOT physically rerun the simulator.

**Check original immutable physics:** [first eight-job official PhysX run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37904539256), [original complete files and SHA-256 manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/task_gated_double_ack_64_520001_530032), [independent offline audit and permanent archive](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37905586372). The original runner was later modified for another experiment, so the exact original controller source is additionally preserved **byte-for-byte** at [immutable frozen-source copy](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_sources/frozen_ppo_compound_ack_multi_belief_v3.py), Git blob `99836af14205fe3e95e52a2e0d68237c7c8a9045`.

**Do a genuinely new run in YOUR independent GitHub fork:** fork this contributor's research repo, enable Actions, select [External fork run — frozen 4-history dual-ACK task-gated original PhysX](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/.github/workflows/external-task-gated-k4-physx.yml), choose `pull_cube` or `stack_cube` and an **unpublished eight-seed block with first seed >=600001**, then run. The workflow pins the original source, records fork owner/inputs/actual PhysX environment before execution, steps all seven native arms and publishes unchanged source + reproducible per-state metrics. A tool action on the contributor's own fork does **not** count as third-party replication. The author-run preflight is green; no outside laboratory execution has been reported.

## Claimed novelty — and the strict no-go claims

The plausible research question is narrow: **authority/provenance of hidden stateful controller commanded-target memory after unknown actuation execution**, together with verifiable native action representability, a trusted/expiring ACK history set, explicit readback price and refusal. The interval Chebyshev center and SO(3) geometry are established mathematics. **ActionShift DualABI already uses task-regret-aware bounded active probes and early stopping**. Those experiments spend physical probe steps, not our privileged state reads; comparing raw costs as though equal is invalid. One Panda robot control family and two pretrained PPOs do not establish broad cross-embodiment transfer.

**Mandatory next study:** source-frozen matched-control integration of ActionShift's exact-belief/entropy/fixed/DualABI competitors adapted to execution ACK rather than unrelated hidden ABI mapping, with equally available public observations, equal target-private reads, equal physical probe duration and full success/failure denominators. Repeat on a second independently maintained robot/controller and let another research organization run the original test. Prior to these gates, no publication/safety/maintainer-adoption claim is justified.

## Independently actionable request

Please test the exact frozen source in your own fork, or identify a counterexample to controller-history completeness, query timing, action chart or task-only baseline. Publish ALL failed and successful original seeds. If the outside run disagrees, report the original SHA-256/seed manifest and let the discrepancy stand; do not discard it.

**Manuscript:** [When Should a Frozen Robot Policy Read Hidden Controller State? — working paper v0.5](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/WHEN_TO_READ_HIDDEN_CONTROLLER_STATE_WORKING_PAPER_V05.md).
