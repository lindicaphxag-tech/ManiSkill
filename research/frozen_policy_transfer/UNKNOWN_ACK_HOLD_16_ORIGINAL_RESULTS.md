# Original prospective action-nonexecution fault — 16 real PhysX closed-loop state outcomes

**Original experimental runner, actual frozen third-party PPO. Contributor-operated simulation, not independently replicated or hardware validated.**

- Frozen protocol [CST_FAULT_ACK_PREDECLARED_V1.json](../CST_FAULT_ACK_PREDECLARED_V1.json), blob `592bb7df53e4b5e79f2e228e9cc56050b648708e`, committed *before any runner was implemented* at `1567bc725301ddd5561a6d78644e309e3cd6d56c`.
- Original successful exact CI [37823344819](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37823344819), tested source `bce51a1696e228cfd16139cb6d43e46eb23d09fe`. Both job conclusions are SUCCESS.
- Two earlier attempts at different commits failed **before the first physics episode** due solely to Python module resolution and canonical `TargetPose` class identity. These do not establish algorithm success or failure, nor add denominator. Precommitted seeds, fixed fault step and PPO SHA were never changed.
- PullCube seeds 102001–102008; StackCube seeds 112001–112008, all 16 original initial source observation SHA256 values logged (16 distinct: 16). Different from earlier target history studies.
- The **experiment is an arm command target-hold**, implemented by delivering a normalized zero 6D delta to target controller at step index 2 **while preserving original gripper action and advancing the physics time**. It is **not** real network packet drop, real actuator control fault, or sensing failure.
- Missing execution ACK to the belief gate is UNKNOWN, not a fictional true status; exact-authority refusal may harm task success. Adapter-specific privileged state access is reported below.

## Genuine official task success (8 seeds per task, paired arms)

| Task | Source no-fault | Translated no-fault | Privileged target getter + hold fault | Blind optimistic history + hold fault | One-shot PUBLIC observation resync + hold fault | Set-valued belief exact refusal + hold fault |
|---|---:|---:|---:|---:|---:|---:|
| PullCube | 8/8 | 8/8 | 8/8 | 7/8 | **8/8** | 0/8 |
| StackCube | 7/8 | 7/8 | 8/8 | 4/8 | **8/8** | 0/8 |
| Pooled descriptive only | 15/16 | 15/16 | 16/16 | 11/16 | **16/16** | 0/16 |

**Prespecified intervention integrity:** exactly one arm-hold fault occurred for each affected arm in every one of 16 episodes; all initial *source-to-target* physical/task observations matched to <=5e-4. The fault is a physically different command, not mere missing ACK. Source no-fault results cannot be called a fair success rate under the fault.

**Key causal intervention:** after a command target hold, the optimistic observer nevertheless integrates the intended command. The readback arm instead reads the existing **7-D `target_pose` field in the public ManiSkill state observation once**, immediately after the faulted step, then resumes its independently implemented target-history recurrence. This is **additional available controller-state information**, even though it is not a private getter. A real deployment without a valid observable/readback channel cannot infer the lost action outcome for free.

The optimistic observer's terminal commanded-target position error was up to `7.639995e-2 m`; the one-shot public-observation resync error up to `2.384186e-8 m`. These audit-only deviations use a privileged getter *after all policy actions are decided* and are **not** collision, tracking or hardware-safety guarantees. At 16 states the readback arm has **5 readback-only / 0 optimistic-only successes**. This is a small sample, not a statistically established universally superior method; randomized runner/initial-state sensitivity remains unexcluded.

Every belief uncertainty branch contained **2 plausible internal target states**. The strict exact-action gate refused further action for all 16; breakdown: AMBIGUOUS_PREVIOUS_TARGET 12, UNREPRESENTABLE_FOR_A_HYPOTHESIS 4. **No falsely authorized exact actions** were observed in these trials, but refusing everything is not a task-recovery algorithm or a safety certification. It is an authority lower bound for this registered scenario; robust bounded-error minimax with attested memory bounds is a stronger performance baseline for future work.

## Original per-seed data transcribed from CI logs

Each success cell is 1 or 0 from the original official `info["success"]` under the fixed 50-step horizon. Per-seed entries below are *derived directly from original CI `CST_FAULT_ACK_EPISODE` records*, not byte-identical copies of the originally uploaded JSON.

| Seed | Source | Target no fault | Private getter | Optimistic history | Public readback once | Belief exact gate | Gate reason | Optimistic final target position error (m) | Public resync final target position error (m) |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 102001 | 1 | 1 | 1 | 0 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 5.348e-2 | 2.384e-8 |
| 102002 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 3.889e-2 | 1.490e-9 |
| 102003 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 3.539e-2 | 2.980e-9 |
| 102004 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 2.742e-2 | 2.235e-9 |
| 102005 | 1 | 1 | 1 | 1 | 1 | 0 | UNREPRESENTABLE_FOR_A_HYPOTHESIS | 5.197e-2 | 2.384e-8 |
| 102006 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 7.640e-2 | 1.490e-9 |
| 102007 | 1 | 1 | 1 | 1 | 1 | 0 | UNREPRESENTABLE_FOR_A_HYPOTHESIS | 3.703e-2 | 2.384e-8 |
| 102008 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 2.698e-2 | 2.608e-9 |
| 112001 | 1 | 1 | 1 | 1 | 1 | 0 | UNREPRESENTABLE_FOR_A_HYPOTHESIS | 6.052e-2 | 2.980e-9 |
| 112002 | 1 | 1 | 1 | 0 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 4.126e-2 | 1.490e-9 |
| 112003 | 1 | 1 | 1 | 0 | 1 | 0 | UNREPRESENTABLE_FOR_A_HYPOTHESIS | 3.872e-2 | 7.451e-10 |
| 112004 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 3.297e-2 | 7.451e-9 |
| 112005 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 4.050e-2 | 1.490e-9 |
| 112006 | 1 | 1 | 1 | 0 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 3.890e-2 | 2.980e-9 |
| 112007 | 0 | 0 | 1 | 0 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 3.738e-2 | 1.490e-9 |
| 112008 | 1 | 1 | 1 | 1 | 1 | 0 | AMBIGUOUS_PREVIOUS_TARGET | 3.558e-2 | 5.960e-9 |

## Original artifacts (raw JSON, full logs, installed-package freeze)

- [real-physx-frozen-ppo-fault-pull_cube](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37823344819/artifacts/11570826343)
- [real-physx-frozen-ppo-fault-stack_cube](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37823344819/artifacts/11570476784)

The raw artifacts are subject to GitHub Actions retention; this derived Markdown record is permanently committed when this PR is merged. It is **not** an independent simulator rerun or signed byte archive of original raw JSON.

## Missing high-tier novelty/acceptance gates

1. True dropped/late/reordered command rather than injected native target-hold; independent hardware/controller-family semantics and authenticated readback.
2. Cross-run replication on new locked states and a fresh external executor, retaining all failures. Exact binary-success differences may be affected by PhysX numerical variability.
3. Strong equal-information, equal-compute baselines: actuator-state observer, robust minimax setpoint authorization, learned adapter, oracle target-state, and offline adaptive query.
4. Joint/EE tracking, collision/contact/saturation exposure, authorization false-positive/false-negative rates; **task success is not physical safety**.
5. Third-party adoption or accepted scientific review; owner-run fork merges count as **zero** upstream adoption.

**Originality positioning:** controller action-ABI observability under uncertain delivery and evidence-gated recovery, not first invention of action adaptation, belief-state estimation, or robust control.
