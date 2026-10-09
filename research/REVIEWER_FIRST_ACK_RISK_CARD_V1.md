# Independent Reviewer Packet — When Did the Command Execute?

**9 October 2026 · original research in progress · author-operated native PhysX, not a peer-reviewed paper, official upstream merge, hardware validation or third-party replication.**

## One-minute scientific claim

When a frozen policy sends a native controller-relative action without receiving a reliable ACK, the controller's **previous commanded target pose** becomes a latent state. A finite history of possible complete target poses can be maintained. Publicly observed tool motion can sometimes select a unique target-history hypothesis, saving privileged controller target-state reads. However, an **empirically calibrated** response envelope can be invalid under a new physical execution regime and lead to **confidently wrong** selections; repeating a correlated motion observation does NOT necessarily repair this.

The observed contributions are a real task-level *information-cost* finding plus a genuine counterexample to treating empirical observability as certified action authority. This is **not** a new identifiability theorem or proven robotics deployment safety.

## Three independently seeded research stages

| Source-authentic prospective cohort | Task-level finding | Most important caution |
|:--|:--|:--|
| Mixed first actual ACK, second HELD; [original 576-world producer + audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314) | New 58/64 tasks with 31 private reads vs task-dependent strong query 58/64 with 58 reads; always-held zero-read 43/64 | Not both ACK truths physically mixed, only Panda / 2 PPOs |
| Both ACK outcomes fully mixed; [first physical run (audit error openly preserved)](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37917629944), [successful original source-only auditor](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37918333602) | Public method 58/64 tasks, 46 reads vs preselected strong 57/64, 62 reads; **2/18 public histories confidently WRONG** on StackCube HA | Model assumption fails: wrong history was compatible and true history was OUTSIDE the old empirical error envelope |
| One vs two public neutral motion probes on ANOTHER new 64-state bank; [original 640-world producer + independent audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37921282989) | **NEGATIVE:** both 48/64 tasks; one probe 41 privileged reads, 23 labels; two probes 43 reads, 21 labels; both 0 wrong | Both share TWO native neutral extra steps, but second uses 128 EXTRA public samples; neither observed wrong on new cohort, so no empirical safety gain demonstrated |

**Do not pool different task populations or actuation timings.** All claim levels are on specific original 64-state cohort(s), not cross-robot universality.

## First things to audit, before reading the paper

1. Original [full model and data claim manuscript v1.6](../frozen_policy_transfer/WHEN_DID_THE_COMMAND_EXECUTE_MANUSCRIPT_V1_6.md). Each positive task-level finding is followed by its later falsifier.
2. [Author-run first-mixed true execution original 17 JSONs and SHA256](../frozen_policy_transfer/evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032/), all failures retained.
3. [Exactly 2 original incorrect confident target histories, source-only preservation](../frozen_policy_transfer/evidence/four_joint_truths_first_physx64_880001_890032/): source reset IDs **890005** and **890017**. Their actual target-history audit-only truth is candidate 2; empirical authorized choice was index 3.
4. [Independent source-audited NEW 640 PhysX double-probe negative files](../frozen_policy_transfer/evidence/dual_probe_vs_single_physx_original64_900001_910032/). Original source hashes, per-task binary success flags, private read ledger, four true ACK regimes and extra probe samples can all be recomputed using `python -m research.audit_sequential_two_probe_new64 --source-dir <original-16-file-directory> --output <output.json>`.
5. [Original preregistration before outcomes](../SEQUENTIAL_TWO_PUBLIC_PROBES_NEW64_PREOUTCOME_V1.json) and [actual frozen simulator policy code](../frozen_ppo_sequential_two_public_probes_physx_v5.py). Both were source-fingerprinted and checked before any new PhysX execution.

## Out-of-sample independent researcher replication, without inventing status

An investigator with an independent GitHub fork or native CPU PhysX environment can select **eight entirely new** resets 960001–989992, covering each of the four ACK execution combinations twice, then execute ten actual policy/controller comparators. No policy retraining. The original method source is Git hash frozen and refuses edits; the investigator commits choice before physical execution, and full source/failure outputs, checkpoints and actor/environment identity are saved.

```bash
# Checkout the published research branch in your own clone/fork.
git checkout research/sequential-two-probe-full-joint-20261009
# Install ManiSkill including official CPU PhysX dependencies, following pyproject.
python -m pip install -e . huggingface_hub
PYTHONPATH="$PWD:$PWD/research" \
  python research/outside_independent_dual_probe_replication.py \
  --task stack_cube --first-seed 960001 \
  --output outside_dual_public_new8
```

Alternatively use [outside investigator's own fork GitHub Actions interface](../../.github/workflows/outside-dual-probe-replication.yml) **after adding the workflow to their fork default branch**, which GitHub requires for manually dispatched workflows. A fork created or run by the original author does NOT satisfy independent laboratory replication.

The research remains **open for genuinely independent run results**, ideally from a researcher who selected seeds without seeing the answers. An outside researcher should publish their complete execution log, original source hashes, exact true ACK regimes and unsuccessful task episodes, not just a screenshot of green CI.

## Serious remaining reviewer objections

- **Model epistemic validity:** historical eps tolerances are empirical, not conditional worst-case physics response bounds. Contact, actuation delay, dynamics change and camera-estimated XYZ error require genuine OOD falsification.
- **External comparison:** [ActionShift](https://github.com/Archerkattri/actionshift) already evaluates frozen PPO, structured beliefs, probe actions and matched privilege. This research **does not** claim to originate active probing or benchmark SOTA, and has not run its full active-adaptation competitor under matched information, time and probe budgets.
- **Information budgets:** privileged native target reads and ordinary public achieved XYZ samples are different. No new neutral probe should be called free if extra `env.step` occurred.
- **Tasks and hardware:** two frozen PPO policies, PullCube/StackCube, one Panda robot family, simulated actual ACK truths. No human/robot hardware safety, true ROS packet loss, vision-to-action VLA, new trained end-to-end policy or noninferiority guarantee has been established.

**Scientific decision criterion:** the next method must reject genuinely false confident native histories on NEW physical/controller/contact conditions *while maintaining real frozen PPO task utility* and counting both extra public observation and native actuation costs. Absent that, submit the narrower information-economy study with its counterexample rather than inflate the claim.
