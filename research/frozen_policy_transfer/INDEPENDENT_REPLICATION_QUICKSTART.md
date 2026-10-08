# Independent external replication — 2-minute decision page

> **This is an independent contributor's ManiSkill fork, NOT the official ManiSkill project.** No ManiSkill/ActionShift maintainer endorsement or third-party scientific reproduction is claimed. This page is written for a skeptical reviewer: a successful source audit is *not* a simulator replication.

## What decision can you make?

**Technical hypothesis:** In a frozen third-party PPO controlling ManiSkill `pd_ee_target_delta_pose`, unknown actuation execution makes the previous-commanded-target state ambiguous. One can dispatch a bounded common command while a complete two-hypothesis target belief fits certified setpoint errors, and use **one trusted target-state readback only when such an action is not certifiable**.

**Original preregistered owner-run discovery (16 unique task seeds):** PullCube 8/8 successes with **zero** readbacks; StackCube 7/8 with **four** readbacks. Selective total **15/16 and 4 privileged decision reads**, fixed one-readback total **15/16 and 16 reads**; zero-readback bounded 11/16, optimistic unacknowledged execution 6/16, exact-only refusal 0/16. This is *not* proof of a general success-rate improvement, new POMDP mathematics, or safety. [All original source JSON and logs](evidence/unknown_ack_bounded_query_16/) · [Original full 4-job successful PhysX run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826881229) · [original pre-outcome protocol](../../UNKNOWN_ACK_BOUNDED_QUERY_FROZEN_V1.json).

**Serious negative control (32 unique seeds, two registered fault modes each = 64 conditions):** a different zero-query SE(3) midpoint approach achieved **43/64** tasks, versus simple optimistic **48/64** and one trustworthy target readback **62/64**. This limits any claim that geometric robust midpoint alone solves unknown actuation. [Immutable original negative outcomes](evidence/belief_minimax_prospective_64_96001_97016/).

## Option C: reproduce the exact SEVEN-arm flagship Certify-or-Query method on YOUR fork

**This is now the recommended reviewer option** if you want to test the novel research question, not just the earlier six-arm ACK baseline. The exact unmodified seven-arm source with selectable new seeds has itself passed [full original 8-seed native PhysX smoke CI 37831105250](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831105250): PullCube 8/8 selective with 1 privileged target read, mandatory 8/8 with 8 reads. This was contributor-operated, so it **is not third-party scientific replication**.

1. On your own GitHub account or research-organization account, fork [this contributor's public ManiSkill repository](https://github.com/lindicaphxag-tech/ManiSkill). Enable Actions if asked.
2. In **your own fork**, select **Actions → External one-click selective-query seven-arm genuine PhysX replication → Run workflow**. [Source of exact workflow](../../.github/workflows/external-selective-query-physx.yml) · [frozen 7-arm algorithm wrapper](../../external_selective_query_replication.py).
3. Choose `pull_cube` or `stack_cube`. Declare an **unused, consecutive 8-seed cohort** with first ID `>=200001` before starting; seed IDs must not overlap original 16+64 discovery/confirmation or the contributor's sample 200001–200008. A recommended fresh external starting seed is `220001` for PullCube or `230001` for StackCube, **only if you have not already used it**.
4. Two genuine GitHub jobs will check the original method/certifier Git objects (**same hashes as the successful discovery CI**), check five intentionally corrupt trial records fail, then load the published third-party frozen PPO in genuine ManiSkill PhysX and step seven physically separate controller worlds. The experiment includes source no-fault, continuously privileged oracle, optimistic missing-ACK, exact-only refuse, bounded no-query, **bounded then one query if needed**, and always-query. It preserves every official `info['success']`, failure, refusal, decision readback count, full original JSON, log, exact source SHA and Python environment.
5. Paste the run URL and zipped `independently-runnable-seven-arm-original-physx` artifact (including its `SHA256SUMS`) to [the falsification issue](https://github.com/lindicaphxag-tech/kaggle/issues/67). Please label who operated the fork; if your result disagrees with the original result, publish the disagreement without post-hoc seed exclusion.

**Important boundaries:** *fork-and-run* is **execution-independent** when a separate organization actually controls its GitHub runner, but it is not independent algorithm reimplementation. The simulator intervention **replaces a native arm target-delta with a zero/target-hold command**, not a true dropped network packet; the state read is privileged extra information, not a free RGB sensor. Error-bound contracts apply to **commanded targets** only, not collisions, force, physical-tracking safety or deployment. Please report all eight original episodes and keep source-policy competence as a separate endpoint.

**New full result to challenge:** on 64 preregistered *new reset states* with the exact same frozen method, **60/64** task success using **15** privileged decision reads vs mandatory read **57/64** using **64** (5 adaptive-only vs 2 always-only paired task successes). [All eight original raw JSONs and SHA256SUMS](evidence/robust_query_new64_142001_152032/) · [full original eight-job PhysX CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195) · [state-disjoint preregistration](https://github.com/lindicaphxag-tech/ManiSkill/commit/9ebb39ef01c06869c60f923cdba5d1e4e5626b1d). This does **not** establish population-level statistical superiority.

## Option A: verify published original evidence (no simulator dependencies)

```bash
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
python research/frozen_policy_transfer/review/verify_stateful_abi.py
python -m research.audit_belief_minimax_64 \
  --input-dir research/frozen_policy_transfer/evidence/belief_minimax_prospective_64_96001_97016 \
  --output /tmp/cst_source_check.json
```

This checks the identity and internal consistency of *existing original author-operated source records*; it is not an independent real PhysX reproduction and should not be called one.

## Option B: run a genuinely NEW ManiSkill PhysX experiment on your OWN fork (no local GPU needed)

1. **Fork** [lindicaphxag-tech/ManiSkill](https://github.com/lindicaphxag-tech/ManiSkill) into a separate GitHub account/organization and enable GitHub Actions for the fork.
2. Open your fork's **Actions → External one-click genuine PhysX ACK-fault frozen PPO replication → Run workflow**. The source workflow is [external-ack-frozen-ppo-replication.yml](../../.github/workflows/external-ack-frozen-ppo-replication.yml), and is present in the public `main` branch.
3. Select `pull_cube` or `stack_cube`, the `applied_no_ack` or `neutral_arm_delta_no_ack` condition, and a **new** eight-consecutive-seed starting ID `>=120001` that does not overlap published runs. Prefer freezing the seed list in an issue/commit **before** running.
4. The workflow installs **real ManiSkill PhysX CPU**, loads the existing externally released frozen ActionShift PPO, steps the official task, and saves all real outcomes, source SHA, dependency freeze, original stdout, and SHA256SUMS as CI artifacts. A workflow started on **our** fork is still author-operated; a workflow genuinely started and controlled on **your** fork is at least execution-independent.
5. Publish **every** success, failure, refusal and `NOT_EXACT` approximation. If outcomes disagree, provide the exact commit SHA, source/target controller modes, seed list, fault truth, the original ZIP artifact and failed raw rows.

[Prior author-operated one-click proof run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37827484496) showed both contract checks and actual physics jobs GREEN, but it does NOT replace a new external execution.

**Option B still refers ONLY to the earlier six-arm ACK experiment**. For the current flagship seven-arm selective bounded-or-query algorithm, use **Option C above**, which has its own tested fresh-seed workflow and exactly pinned model/algorithm source.

## Most important counterexamples we want

- Controllers that **do not expose** the previous commanded target, and *cannot* be reset/authenticated; do not mistake actual achieved joint/EE poses for target-memory readback.
- Unknown command delivery with delayed, reordered or duplicated instructions, without an artificially known `zero native arm command` control intervention.
- A second independently maintained control implementation with different target-update semantics, limited rotation geometry, or non-additive state.
- Matched-information alternatives: learned observer, interval robust control, active sensing with fixed observation cost, true no-readback policy, and explicit collision/tracking/force limits.

**Do not claim:** hardware-safe robotic execution, unmodified VLA policy, third-party adoption, model retraining, general optimality of SE(3) midpoint, or statistical acceptance for a population from 8+8 seeds.

## Sharing the independent result

Share a link to the **new fork CI run**, original artifact download, and the result of Option A in [the public falsification issue](https://github.com/lindicaphxag-tech/kaggle/issues/67) or [ActionShift opt-in benchmark discussion](https://github.com/Archerkattri/actionshift/issues/1) if genuinely relevant. Negative outcomes, implementation bugs and mismatches are as valuable as positive replications. Please be explicit whether you or the original author triggered the run.

_The original method is research evidence; this page makes its verification and nonclaims easy, not a request for endorsement._
