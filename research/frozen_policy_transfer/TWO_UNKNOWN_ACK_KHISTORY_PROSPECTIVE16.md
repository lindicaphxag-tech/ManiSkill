# Two consecutive unknown ACKs: full prospective native PhysX K-history result

**Author-operated, frozen third-party PPO, genuine ManiSkill PhysX.** TWO physically separate target-hold interventions (zero-based simulation steps **2 and 4**) with both receipts unknown to the adapter. The possible native commanded-target history branches to up to **four** candidates; an O(K) Chebyshev position command and conservative finite SO(3) native rotation candidates authorize a common action ONLY with predeclared commanded-target limits. The controller may spend up to two privileged target reads, accounting for each. This experiment is a targeted extension beyond the existing one-ACK, two-history comparison. The minimax geometry is standard, and the SO(3) finite search is NOT a globally optimal rotation solver.

**Source protocol fixed before any new task result:** [original frozen contract `research/MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json`](../MULTI_ACK_K_HISTORY_PREOUTCOME_V1.json), Git blob `4107c00a5359da78542bbaafa922e2f4196f11fd`, PullCube 230001–230008, StackCube 240001–240008, SHA-pinned third-party released PPO at revision `6bdeb28810330ab5425ccd629bb561c58a56ff85`. All original complete source evidence: [run 37835511954](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954) (two genuine native PhysX jobs, contract and independent all-16 audit all GREEN). A separate public run [37835549067](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835549067) likewise passed. These two CI runs can repeat the SAME registered original cohort; **they do not constitute independent fresh reset-state validation**.

## Original source outcomes (never exclude missed faults or task failures)

| Frozen native controller arm | PullCube /8 | StackCube /8 | Official task success /16 | Privileged target decision read calls |
|---|---:|---:|---:|---:|
| Same pretrained source PPO, no fault (context only) | 7 | 8 | 15 | 0 |
| Continuously privileged oracle target getter | 8 | 7 | 15 | Unlimited, flagged `-1`, not counted as 0 |
| Optimistic assume BOTH target commands were applied | 8 | 1 | 9 | 0 |
| Strict common exact-only, refuse otherwise | 0 | 0 | 0 | 0 |
| K-history common bounded action, refuse with zero authority reads | 4 | 3 | 7 | 0 |
| **K-history bounded-or-up-to-two-trusted-reads** | **8** | **7** | **15** | **9** |
| Mandatory one trusted target read after EACH fault | 8 | 7 | 15 | **32** |

**True same-seed matched task-success parity:** K-history bounded-or-query vs mandatory readback **both-success 15/16, both-fail 1/16, zero either-only wins**. Compared with zero-readback bounded, adaptive has **eight adaptive-only wins** and no bounded-only wins, BUT it used additional privileged state, so this is **not an equal-information comparison**. No-power claim from 16 states.

**Real physical intervention and claims audit:** the selective K-history arm physically underwent **both** interventions on **16/16** task states; the mandatory-readback arm also 16/16. The no-query bounded arm did **not** reach the SECOND physical intervention on **Pull seed 230007**, as it refused early; this is an explicit missed-fault exposure in that comparator, not an omitted task episode. The strict exact-only arm stopped before the second intervention in all 16/16 trials. They all remain IN the denominator and each missed-fault count is reported. At least one in-test multi-history log reached `K=4`. Certificates for an intended action which was physically suppressed at the fault step are NOT counted as actually dispatched bound-verification certificates. Only non-injected ACTUALLY dispatched actions can carry a retrospective real native target bound audit.

### Every original state (0/1 = official native task success)

| Task | Seed | Selective success | Selective private reads | Mandatory success | No-query bounded success | Optimistic success | Selective faults actually reached | No-query faults actually reached | Max logged selective K |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pull | 230001 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 4 |
| Pull | 230002 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 4 |
| Pull | 230003 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 4 |
| Pull | 230004 | 1 | 1 | 1 | 0 | 1 | 2 | 2 | 4 |
| Pull | 230005 | 1 | 1 | 1 | 0 | 1 | 2 | 2 | 4 |
| Pull | 230006 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 4 |
| Pull | 230007 | 1 | 2 | 1 | 0 | 1 | 2 | 1 | 2 |
| Pull | 230008 | 1 | 1 | 1 | 0 | 1 | 2 | 2 | 4 |
| Stack | 240001 | 1 | 0 | 1 | 1 | 0 | 2 | 2 | 4 |
| Stack | 240002 | 1 | 1 | 1 | 0 | 0 | 2 | 2 | 4 |
| Stack | 240003 | 1 | 1 | 1 | 0 | 0 | 2 | 2 | 4 |
| Stack | 240004 | 1 | 0 | 1 | 1 | 1 | 2 | 2 | 4 |
| Stack | 240005 | 1 | 1 | 1 | 0 | 0 | 2 | 2 | 4 |
| Stack | 240006 | 1 | 1 | 1 | 0 | 0 | 2 | 2 | 4 |
| Stack | 240007 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 4 |
| Stack | 240008 | 1 | 0 | 1 | 1 | 0 | 2 | 2 | 4 |

## Original readback source files, SHA provenance and critical boundaries

- [Original PullCube real PhysX job](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954/job/113511865912) · [original PullCube SHA-256 ZIP digest `7162936…`](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954/artifacts/11575791928).
- [Original StackCube real PhysX job](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954/job/113511865893) · [original StackCube SHA-256 ZIP digest `0b11fac…`](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954/artifacts/11576165507).
- [Both original unmodified source JSONs and independent `research/audit_multi_ack_khistory.py` aggregator](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835511954/artifacts/11575653108). They are permanent only after SOURCE file commit under `research/frozen_policy_transfer/evidence/two_ack_khistory_original16_230001_240008/` and successful author-fork trusted-main archive. Downloadable GitHub Actions artifacts have finite retention until then.

**Scope:** different information budgets in comparisons; simulated native target hold not real network packets, **one** Panda robot family and two frozen third-party PPOs; no independent laboratory reproduction, paper acceptance, global nonlinear trajectory guarantee, collision/force or human-safety certification. The correctness condition concerns commanded-target pose only when all prior-controller histories and root-left action chart assumptions actually hold. Active execution probe, downstream contact risk, and known robot hardware safety remain separate research questions.
