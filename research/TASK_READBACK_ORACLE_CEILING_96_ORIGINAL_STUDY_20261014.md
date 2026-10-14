# Why task-aware action recovery cannot be replaced by a better readback switch

**2026-10-14 — source-anchored original PhysX evidence and an EXACT but retrospective control-policy selection bound.**
**Not a peer-reviewed paper, not novel optimization mathematics, and NOT a new task-success improvement.**

## The central falsifier

A finite-history native SO(3) certificate can authorize a mathematically feasible commanded setpoint without ensuring the robot will complete the manipulation task. The new native-reachable variant exposed precisely this gap: `PullCube+StackCube` 64-reset original PhysX gave 45/64 success versus 55/64 corrected fixed readback; the strictly heldout `PickCube` 32-reset experiment gave 18/32 versus 26/32, **with exactly the same old/new native action sequence on all 32 PickCube resets**.

This rules out merely tuning SO(3) action feasibility as the next flagship research contribution. Prior learning-based adaptive robot state-memory, task-oriented information acquisition, and task-recovery value models also prohibit claiming that generic "task-aware sensing" is new.

## New quantified barrier: exact readback-policy switching ceiling

Let the two separately physically executed arms on original reset `i` be:
- `F`: corrected fixed t4 authoritative target-memory readback;
- `O`: finite-history bounded native action with one readback **only on refusal**.

Official simulator task success `y_i(F), y_i(O) ∈ {0,1}` and actual policy decision read counts `q_i(F), q_i(O)` are source records, not a new fitted model.

Define **retrospective outcome-aware** arm selection:
```
D_0(0)=0;
D_i(b)=max{D_(i-1)(b-q_i(F))+y_i(F),
           D_(i-1)(b-q_i(O))+y_i(O)}.
```
This exact finite 0/1 outcome DP finds the maximum number of successes a hypothetical omniscient chooser could obtain at **exactly** b spent privileged reads, but only from the two original actions/results actually executed on each reset.

| Physically executed source task | Source `F` success /32 | Source `O` success /32 | Source F total reads | Source O total reads | **Max** posthoc savings with success >= F |
|---|---:|---:|---:|---:|---:|
| PullCube (development, original run #38546430880) | 32 | 30 | 32 | 19 | 11 |
| StackCube (development, same original run) | 23 | 16 | 32 | 22 | 5 |
| PickCube (**task-external**, original run #38550286593) | 26 | 18 | 32 | 26 | **2** |

For PickCube a hypothetical outcome-aware chooser restricted to F/O spends at least **30** real readbacks to reach 26 total task successes. With **28 or fewer** reads, the maximum possible success is **24/32**. An F/O-only selector saving 4 reads and matching 26 successes is therefore **mathematically impossible on this fixed original 32-state bank**.

### Why this is important — and its STRICT scope

The failure is not just a weak learned router or unfortunate threshold. Even if a F/O router were told its exact future task success labels, it could not pass the **four-read savings target** without generating at least one new physical action/trajectory (or changing an action intervention other than a per-reset F/O choice).

**But this is NOT an impossibility theorem for robot recovery or for other policies.** It explicitly says nothing about a third controller, earlier reads/probes, other reset distributions, new robot morphologies or outcomes under rerun with altered actions. The oracle is **posthoc, noncausal for deployable decision making**; only the underlying paired results are genuinely physically executed. Do not compare oracle results to real online decision methods as if it used the same information.

## Source validity

1. Original first-generation 64 reset physical experiment, eight genuine shard logs: [run #38546430880](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38546430880), which **FAILED only in the post-episode summary** with `NameError PROTO`. All 64 trial receipts were emitted; the separate SHA-locked full-denominator source auditor **PASSED**, [run #38547796024](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38547796024). Neither retries nor edits are counted as new resets.
2. Third-task previously unseen PickCube physical experiment, first full 32 reset run [#38550286593](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38550286593): full original task, 4 successful physical shards + successful original 32 denominator auditor. The PPO checkpoint is an **existing PickCube-trained pretrained actor**, not zero-shot learning.
3. Separate [exact-query-budget Python DP and GitHub SHA-locked rerecount #38553643141](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38553643141) **all 3 CI jobs passed**, including Ubuntu and Windows exhaustive programmatic test and independent extraction from preexisting original GitHub workflow receipts. The 200 randomized DP-versus-brute-force tests are software comparisons, not 200 additional robots.
4. State independence: the denominator is 96 distinct original task/reset identifiers **across three tasks**; multiple parallel controller worlds per seed are repeated interventions on that reset, not independent humans or separate generalization tasks. Different task resets are not necessarily identically distributed.

## What *actually* constitutes next algorithmic research

A successor needs to **alter physical recovery behavior** and to outperform both F and a continuous true-target oracle on official task outcomes or on a jointly prespecified task-success/readback Pareto criterion. It must:
- use public task-scene geometry or a trained calibrated world/continuation model to estimate **downstream task viability**, not only geometric setpoint tolerance or hidden target disambiguation;
- learn and calibrate on disjoint training/reset cohorts, with prospective abstention when task-value reliability does not hold;
- produce at least one new, physically admissible, shared-source control action/probe trajectory that is **not** just a per-reset choice of F versus O;
- freeze the model/checkpoint, hyperparameters and full strong-baseline test before seeing unseen task outcomes; an undisturbed fourth task such as `PushCube-v1` exists, but is not yet validated for this new task-value model;
- compare against independently adapted task-regret-aware probe baselines, corrected fixed readback, continuously privileged target access, no-query and realistic paid query/actuation costs; treat changed robot/control contract as a separate external transfer test;
- obtain an outside group's independent source execution or academic reviewer response before claiming external academic recognition.

Generic POMDP lookahead, Chebyshev sets, and exact two-choice dynamic programming are established prior art. A new *name* around these alone is not a doctoral-level original algorithm.

## Scientific admission ledger

- [x] 3 task families genuinely executed with unique reset clusters, correct target-memory strong comparator, unchanged frozen actors.
- [x] Independent author-operated artifact hash audit and exact decision-budget DP, original negative cases retained.
- [x] Reproducibility release suitable for an external researcher to rerun.
- [ ] **New task-controllability algorithm beats correctly informed comparator:** NOT achieved.
- [ ] **Truly untouched extra task/robot validated under learned task-value method:** NOT achieved.
- [ ] **Independent scientific group reproduced accepted claim:** NOT achieved.
- [ ] **Peer-reviewed research paper or official upstream ManiSkill merge:** NOT achieved.

Suggested paper angle only after new positive evidence: *Task-Controllability-Aware Action Recovery Under Hidden Controller Memory*. An exact dual-policy frontier can remain a diagnostic supporting result but cannot be the central novelty.
