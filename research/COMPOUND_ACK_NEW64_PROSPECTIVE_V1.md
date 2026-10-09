# 64-STATE PROSPECTIVE confirmatory frozen PPO multi-ACK benchmark — pre-outcome v1

**Precommitted 2026-10-09 BEFORE evaluating any of these new seeds.** This experiment reuses **unchanged v3 multi-history algorithm** after seeing the prior 16-case mixed results. No query threshold, geometry rule or source PPO weights may be tuned against this prospective test population.

## Source and reason
Development observations: initial single-ACK 64 states, followed by new two-ACK 16 states [#37898781176](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37898781176) showed four actual target-memory hypotheses, selective 11/16 with 11 private decision reads, fixed-t=4 13/16 with 16 reads, zero-read 2/16, and 384 auditable conditional setpoint checks. These 16 observations are DEVELOPMENT, **not** part of this confirmatory denominator.

## Frozen genuinely UNSEEN test states
- **PullCube:** consecutive source seeds 420001–420032, 4 exact eight-seed shards: [420001,420009,420017,420025].
- **StackCube:** 430001–430032, 4 exact eight-seed shards: [430001,430009,430017,430025].
- 64 distinct simulator reset states; each steps **seven matched actual physical controller worlds** (448 genuine ManiSkill native PhysX control runs if every shard completes).
- Physical fault is native target hold at BOTH steps 2 and 3 (commanded arm replaced by a neutral/zero arm action; gripper still actuates). Two unknown ACKs in policy memory. **Not real network transport packet loss**.
- Original third-party released ActionShift PPO weights unchanged; source/controller charts frozen.
- Data reporters retain true authoritative target readback count, each real/partial fault reach, max observed target-state belief width, counterfactual commands physically masked by injected faults, and after-*actual-dispatch* residual checks.
- Seven arm variants unchanged: source no fault; continuous privileged controller-target oracle; optimistic ACK; strict exact-action or refuse; conservative bounded no-read; one evidence-triggered private read; one fixed t=4 private read.
- No actions may silently use `controller.target_pose` private memory except the oracle, the explicitly logged/readback arms and postdispatch audit.

## Exact source freeze (prohibit post-outcome source drift)
- v3 original runner Git blob `99836af14205fe3e95e52a2e0d68237c7c8a9045`; multi hypothesis SE(3) bound checker blob `36707a177549104ba5b4bd9bcebc76518f0d2840`.
- Original unchanged 2-history runner Git blob `1dc653cdc44e422c8340475ad00f828b3a41eb4f`; 2-history geometry `bb5fd155b7291fb127f94138fca321201c8271c3`.
- Two third-party PPO checkpoint SHA256: Pull `74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7`; Stack `e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c`.
- Frozen controller-target setpoint budgets 0.05m position max-component error and 0.05rad geodesic orientation; any actually dispatched authorized command exceeding its recorded envelope +1e-4 measurement guard FATAL.

## Analysis fixed before unseen outcomes
- Primary descriptive table: official native task success /32 per task and /64 pooled for selective, fixed read, bounded no read, optimistic, oracle, no-fault.
- Private controller-target decision reads for each method and task, paired original-state contingency with exact two-sided McNemar sign-test for selective vs fixed, with per-task stratified reporting (no 64 independent PPO models claim).
- Physical fault reach, query timing, four-state belief prevalence; report every masked action separately from actual real afterdispatch error checks.
- **Non-inferiority / superiority is NOT assumed** and no p-value guarantees success. Compare selective against the same-timing fixed action as well as no-read with explicit information-cost caveat.
- At most two tasks and one Panda native controller; no hardware safety, independent outside-lab replication or general cross-embodiment claim. Do not exclude failures, rerun only favorable shards, or tune subsequent protocol against this prospective cohort.

## Go/no-go
If selective still underperforms fixed-read on StackCube or pooled tasks, record the negative result and stop advertising active-query task superiority. Any further modified method needs a NEW state-disjoint held-out population with a specifically frozen comparator. Source acceptance into a third-party library or a paper requires independent external study beyond author's GitHub Actions.
