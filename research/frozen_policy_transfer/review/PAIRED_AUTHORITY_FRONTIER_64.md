# Frozen PPO controller-target authority: 64-state exact paired results and readback-cost frontier

**Author-run original ManiSkill PhysX, 2026-10-09.** Read-only **post-outcome analysis**, not 64 new simulator runs, and not an independently reproduced external laboratory result.

## Why a reviewer should look at this rather than headline task accuracy

A stateful destination controller may interpret one nominally valid `pd_ee_delta_pose` action relative to a prior *commanded target*, while the source policy expects achieved-pose-relative control. After a target-hold fault at simulation step 2 with an unobserved ACK, the adapter cannot simply equate executed commands with submitted actions. The two-state minimax policy has a concrete decision: either authorize a bounded action that is safe **under the specified setpoint-error chart assumptions only**, or make one *privileged* target-memory query.

The original method, seven matched controller arms, frozen published third-party ActionShift PPO weights and 64 new source seed population were fixed and executed previously. The experiment establishes performance under the source simulator's **one Panda robot/controller family**, not new hardware/policies or real network packet loss.

This document adds the exact statistical discipline missing from a shorthand “60/64 versus 57/64” claim.

## Reproduce on any stock Python 3.11+ installation, no pip, GPU or PhysX

```bash
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
python -m unittest discover -s tests -p test_new64_authority_frontier.py -v
python -m research.frozen_policy_transfer.review.authority_frontier_64 \
  --input-dir research/frozen_policy_transfer/evidence/robust_query_new64_142001_152032 \
  --output /tmp/authority_frontier_original64.json
```

Unlike reading just markdown, the verifier checks the `SHA256SUMS` of all **eight original JSON files**; reuses the source-frozen full-denominator independent audit of official frozen checkpoint hashes, complete reset-seed identity, all seven actual PhysX control-arm success flags and decision-readback accounting; then reports 32 PullCube and 32 StackCube **paired** outcomes separately before showing the pooled (but only two-model) 64-state description.

**Additional immutable manifest witness:** the verifier also checks that the `SHA256SUMS` manifest itself equals the previously public source Git blob `64c3b913a9afbdfbcd374f176c484ee7b6576f93`, which was present in the original archive before this retrospective statistical audit. A destructive regression changes one JSON and recomputes its manifest entry to keep the pair internally consistent: that attack must still fail. This prevents treating a mutable pair of files as an independently immutable scientific record.

Original native creator: [eight real simulator jobs, completed](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195). The code gives all duplicate/replaced/missing-shard, forged success/readback and incorrect sampling-counter negatives the same fatal error as a corrupted source artifact. **Running the verifier is NOT independent re-execution of PhysX.**

## Original 64-state, *same-seed paired* results

| Arm | Real original task success | Decision private-target reads |
|---|---:|---:|
| optimistic ACK assumption | 42/64 | 0 |
| valid-for-two-hypotheses bounded action, no query | 47/64 | 0 |
| **bounded command or one trusted readback** | **60/64** | **15** |
| mandatory one trusted target readback after ACK uncertainty | 57/64 | 64 |

The selective method has 60 successes, the mandatory 57. However the paired source-state table has **55 both succeed, 2 both fail, 5 selective-only wins, 2 mandatory-only wins**, giving **two-sided conditional exact McNemar p = 0.453125**. This is *not* significance and is **not** registered clinical/robotic noninferiority. Critically, there are two reset states for which the mandatory readback method succeeded and the proposed selective method failed. Hence the selective method does NOT dominate on every case.

Against **bounded/no-readback** (47 successes), selective has **13 selective-only wins, zero zero-query-only wins, 47 both succeed and 4 both fail**; two-sided exact paired p = **0.000244140625**. This contrast is expected to favor extra trusted information and **cannot** establish algorithmic superiority under an equal-information budget. You cannot casually pool it with the mandatory comparison.

Only two frozen pretrained PPO/task classes were exercised: **PullCube 32/32 selective, 30/32 no-query, 32/32 mandatory, 2 selective reads; StackCube 28/32 selective, 17/32 no-query, 25/32 mandatory, 13 selective reads**. Although these are 64 distinct seeded reset states, there are not 64 independent policy models, controller platforms or clinical interventions.

## Interpretable but explicitly post-hoc empirical query-cost frontier

Let one binary task success have unit utility and each *privileged controller target read* incur `λ` success-equivalent utility units:

```text
U_empirical(method; λ) = sum(success_per_original_state) - λ * sum(decision_target_readbacks)
```

The **purely empirical** pooled lines are:

```text
selective:       U(λ) = 60 - 15 λ
mandatory:       U(λ) = 57 - 64 λ
bounded no-read: U(λ) = 47
optimistic:      U(λ) = 42
```

For every `λ>=0`, *pooled observed* selective totals dominate mandatory in both task successes and privileged read count. **This is not a pointwise episode dominance or population guarantee**, as demonstrated by the 5-vs-2 discordances.

Selective beats no-read in these observed totals only while `0<=λ<13/15≈0.867`; a readback valued higher than that crosses the observed aggregate frontier. Across tasks the analogous crossings differ: Pull `(32-30)/2=1`, Stack `(28-17)/13≈0.846`. These are **retrospective score arithmetic**, *not* pre-committed deployment budgets, causal policy-value estimates or an optimized new online control algorithm. A confidence interval reported for the descriptive 15/64 query rate is not a deployment risk certificate.

## Explicit evidence and novelty limitations

- Fixed 0.05m/`0.05 rad` setpoint minimax budgets **only within a known two-hidden-controller-target model**. This is *commanded target geometry*; no end-effector tracking guarantee, collision check, uncertainty from dynamics, force limit, actuator latency or physical human safety is certified.
- One simulated controller zero-delta/target-hold at time step 2; **not real dropped TCP/ROS packets** or external resets. The policy and model architecture were frozen and taken from a **third-party** pretrained ActionShift release; no model was learned here.
- The two controller truth states and basic Chebyshev/geodesic midpoint construction are standard decision and geometric techniques. The contribution lies in a well-audited state-memory ABI mismatch and a conditional *action-versus-information* tradeoff in an actual frozen-policy closed loop; the geometry by itself is not a new theorem.
- Outcomes were produced by the contributor's own CI. For genuine external validation, an **outside investigator must execute the real PhysX in their own environment**, not merely rerun this Python audit.
- Now available for outside execution: [official public forkable seven-arm real PhysX workflow](../../../.github/workflows/external-selective-query-physx.yml), source [merged PR #84](https://github.com/lindicaphxag-tech/ManiSkill/pull/84). An investigator can fork, enable Actions, select **pull_cube** or **stack_cube** and eight investigator-selected, unreported seeds (at least 200001) in the workflow dispatch; execute on THEIR fork. **Do not simply reuse the workflow default 200001** for a seed-disjoint confirmatory claim: the author-run workflow [37831105250](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831105250) already executed PullCube 200001–200008. Another lab may reproduce identical seeds, but that is a protocol **replication**, not a new seed cohort. That interface has passed **contributor-owned** original-source native PhysX CI [run #37831105250](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831105250). It has **not yet produced an independent external research endorsement**.

**Review judgment:** A reviewer may validate these exact paired statistics and the information-use frontier without installing PhysX, and then take the next stronger step—execute the unmodified published PPO/controllers on fresh independent seeds using the forkable workflow. Only that latter step closes the external physics-replication gap.

## Strong existing prior art and the next nonredundant scientific comparison

The independent benchmark [ActionShift](https://github.com/Archerkattri/actionshift) already studies broad hidden robot action-interface contracts, with active probe families, belief adapters, fixed/entropy-driven calibration and matched information budgets on genuine ManiSkill. Its companion [ActionABI](https://github.com/Archerkattri/actionabi) analyzes equivalent controller contracts from logs and explicitly abstains when evidence is insufficient. Therefore **belief maintenance, probing and abstention are not unique inventions here**.

A future original methods paper would have to use the same true held-target vs executed-target fault worlds and original pretrained task policies to compare this *specific hidden previous-command-target memory* with ActionShift's active probe/belief baselines under an equal privileged observation, extra native actuation and wall-clock budget. Until that truly matched external comparison is run, the present seven-arm study supports a meaningful but narrow author-controlled engineering-science observation: source-command success versus number of privileged target-memory reads under the declared two-history model. Do not claim broad SOTA, actual communications faults or general system identification.
