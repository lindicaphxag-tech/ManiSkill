# When the ACK goes missing: prospective two-sided frozen-policy transfer in native PhysX

**External research review packet · 9 October 2026 · contributor-owned public ManiSkill fork**  
**Status:** native source trials and original 32-state auditor **complete**. This is **not** an accepted paper, upstream ManiSkill endorsement, independent lab replication, or real hardware validation.

## The question (single sentence)

Can a robot keep executing the **same frozen learned manipulation policy** when a controller arm command might have been applied but its acknowledgement is unavailable, without silently assuming the wrong previous target state?

The original achieved-relative PPO policy has 7-D native actions. The destination accumulated-target-relative end-effector controller is a stateful action ABI: its next commanded target depends on the previous commanded target, not only the observed achieved end-effector pose.

If a command with a nonzero target offset is ACK-ambiguous, at least two previous-target histories can be consistent with what the adapter has been told. Merely choosing "probably applied" or "probably omitted" can be systematically wrong. The elementary two-history additive-setpoint indistinguishability bound is half the possible prior-target separation under the infinity norm. This is **known elementary control/estimation geometry**, not a new theorem.

## Source experiment: fixed BEFORE running any outcomes

- Exact frozen [prospective protocol commit](https://github.com/lindicaphxag-tech/ManiSkill/commit/3ead83ecbb68eb6a405cdf768a42c617f649ddc4), byte identity Git blob \`3a7273c1a02d13c19e93e618c74fc7068938c7e9\`. Both PPO checkpoints fixed by SHA-256 from external published revision \`6bdeb28810330ab5425ccd629bb561c58a56ff85\`; **zero PPO training or fine-tuning**.
- ManiSkill \`physx_cpu\` / \`state\` / \`50\`-step horizon, official native \`info["success"]\` flags, independent task states PullCube 94001–94008 and StackCube 95001–95008.
- **Two** predeclared ACK-ambiguous arm-fault **truths** for EACH task×seed: (A) the requested command **actually applied** but its ACK hidden; (B) at action index 2, the requested controller-native **arm delta replaced by an all-zero arm delta**, gripper preserved, real physics \`env.step\` still executed, ACK hidden. This is **not** real network packet loss.
- Six controllers with matched task reset seed: original native source PPO, repeated **privileged** live target read, **one** trusted privileged controller-target read after ACK uncertainty then source-aware action-history reconstruction, optimistic "applied" assumption, pessimistic "neutral/omitted" assumption, and fail-closed stop.
- All source binary flags, refusers and approximations \`NOT_EXACT\`, fault-reached counts, readback budgets, target-state residuals, and failures stored in original run-specific JSONs; all **32** task×fault states kept.

## Genuine original paired trial outcomes

| Frozen task | Actual arm fault truth (ACK unknown in all cases) | Source clean | Optimistic | Pessimistic | One privileged read + resume | Always privileged | Fail-stop |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PullCube, fixed 94001–94008 | Arm command **applied** | 6/8 | 6/8 | 5/8 | **6/8** | 6/8 | 0/8 |
| PullCube, same eight physical seeds | Requested arm delta replaced by **zero** | 6/8 | 7/8 | 8/8 | **8/8** | 8/8 | 0/8 |
| StackCube, fixed 95001–95008 | Arm command **applied** | 8/8 | 8/8 | 0/8 | **8/8** | 8/8 | 0/8 |
| StackCube, same eight physical seeds | Requested arm delta replaced by **zero** | 8/8 | 2/8 | 8/8 | **8/8** | 8/8 | 0/8 |
| *Descriptive total, not 32 independent policies* | two repeated truths per task seed | 28/32 | 23/32 | 21/32 | **30/32** | 30/32 | 0/32 |

**What the contrast actually shows:** the optimal fixed guess flips with the unobserved truth. In StackCube, blindly assuming execution succeeds **8/8** under applied truth but **2/8** under omitted truth; assuming omission succeeds **0/8** when execution occurred and **8/8** when it did not. A source-independent one-target-state-read strategy instead matches the repeatedly privileged memory controller's **task outcome count** in both cases. The observed outcome is a task-level success flag, not physical trajectory identity or certified controller/robot safety.

**Crucial information-budget and causal limit:** the one-read method has **strictly MORE target-state information** than optimistic, pessimistic and stop policies. Its accuracy cannot be interpreted as discovering hidden state solely from achieved pose or as a fair no-extra-information performance comparison. The continuously privileged oracle has even more state access. The result does **not** imply that requesting one read is novel, optimal, always available or physically safe. A policy with advance knowledge of the actual fault truth could select optimistic/applied or pessimistic/omitted and also reproduce the corresponding count. What matters experimentally is that the adapter DOES NOT receive that truth.

The PullCube no-command group has **8/8** recovered successes while the separate **clean source** has **6/8**. Do not describe this as new PPO improvement: skipping an early arm movement can incidentally change a particular trajectory and the official task outcome. Recovered's meaningful comparator is the faulted privileged target-memory arm and equal fault-state baselines.

## Reproduce & independently try to falsify

1. [Exact original run 37824078238](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37824078238), full 6/6 success, including four genuine PhysX task/fault jobs and original 32-state auditor.
2. [Original code and fixed pre-outcome runner #72](https://github.com/lindicaphxag-tech/ManiSkill/pull/72). No outcomes chosen to alter seeds, checkpoints or fault index.
3. [Permanent five-JSON original source archive](evidence/unknown_ack_prospective_32_94001_95008/) with all per-episode records, a source-generated full audit, and independent SHA256SUMS. This is present ONLY after the trusted-main archival workflow confirms writing the files. Use \`sha256sum -c SHA256SUMS\`.
4. Reaggregate all four original source JSONs from repo root:

\`\`\`bash
python -m research.audit_unknown_ack_physx \
  --input-dir research/frozen_policy_transfer/evidence/unknown_ack_prospective_32_94001_95008 \
  --output /tmp/independent-32-state-audit.json
python -m unittest discover -s tests -p test_unknown_ack_original_auditor.py -v
\`\`\`

The auditor **refuses** missing/duplicated seed-source rows, incorrect model/source SHA, omitted truth branch, non-executed fault, fake target-read budgets, mismatched summary, forged "exact" action claims, or stop-arm actions after the fault. It accepts scientifically meaningful null/negative performance without deleting trials.

## Relation to the earlier public-observation resynchronization

A **different prospective** [16-state unknown-ACK source experiment on PR #66](https://github.com/lindicaphxag-tech/ManiSkill/pull/66) fixes the fault truth to requested-arm hold/zero and tests an **even stronger availability model**: the subsequent native state observation includes the controller target field. After masked ACK, one public-observation target read recovers reference continuity without calling private \`get_state\`. On its own independent seed population, that prior study reported PullCube 8/8 and StackCube 8/8 resumed success versus optimistic 7/8 and 4/8 respectively. This is **not** evidence that images/achieved-only observations contain that field or that it remains trusted under a different controller ABI.

The current 32-state study deliberately uses one explicitly trusted **privileged** target read, rather than covertly equating those observation regimes. Together they establish conditional mechanisms but do not justify aggregating "48 episodes" as 48 independent policies.

## What would constitute genuine L8/L9 originality or external recognition?

- Recover a useful target belief **without trusted target memory telemetry**, on independently maintained controller semantics. Produce physical-identification evidence and demonstrate why competing state estimators are inferior under the same observation, actuation and time budget.
- Test **true missing/delayed/reordered commands** and both forward motion and inverse control under explicit channel latency; include acknowledged-but-not-applied cases and independently measured ground truth.
- Freeze fresh cross-controller task scenes on a DIFFERENT robot and evaluate native achieved trajectories, force/contacts, actuator saturation and task outcomes with the same protocol.
- Get an independent team to run a version-pinned bundle and openly report either matching or nonmatching results, with their own logs and outcome denominators. Publishing a contributor-owned fork and self-merging PRs is **not independent adoption**.

For researchers interested in proving this wrong, use the [public external falsification issue #67](https://github.com/lindicaphxag-tech/kaggle/issues/67) and post your own exact SHA, third-party pretrained model identity, unseen predeclared task seeds, full failures and every condition's raw trial outcomes.

## Related public upstream work

This fork also contributed EEG foundation-model integrations [Braindecode #1218](https://github.com/braindecode/braindecode/pull/1218) and [#1223](https://github.com/braindecode/braindecode/pull/1223), which were **actually accepted upstream**. They are independent EEG engineering signals—not third-party acceptance or validation of this robot-control research.

For controller action geometry, cite [SPACE (2026)](https://arxiv.org/abs/2606.24049), [TAM (2026)](https://arxiv.org/abs/2606.06218), and their stronger action-transport scope rather than claiming this is the first action-adaptation method. The current novel *hypothesis* is protocol-aware, evidence-gated state recovery across controller contract boundaries; proof of a general deployable method remains open.
