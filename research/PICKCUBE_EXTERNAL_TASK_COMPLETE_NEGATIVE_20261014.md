# PickCube third-task prospective native PhysX result — complete original NEGATIVE result

**2026-10-14 • No task-performance improvement • Public, inspectable simulator records • Not a peer-reviewed or independent-laboratory result**

## Source-frozen exposure and real output

Pre-outcome protocol: `research/PICKCUBE_UNSEEN_TASK_FROZEN_BEFORE_RESULTS_20261014.json`, commit **`2ecc0dfa2c6a78efda0ba702f2c27c024956dea1`**, predating the first PickCube run. No experimental seed, model weights, comparator definition or threshold was updated after observing outcomes.

[Original exact 32-reset, 160-physically-stepped-worlds run #38550286593](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38550286593) **SUCCESS** including 4 complete original eight-reset shards, a Python preflight and the all-denominator GitHub Actions auditor. PickCube-v1 was not used to design the Reachable-SO3 optimization; the **published PickCube PPO was trained on PickCube**, and this is not an unseen robot, learned zero-shot skill, VLA or actual network packet fault.

Third-party released policy SHA256 `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8` (ActionShift release `6bdeb28810330ab5425ccd629bb561c58a56ff85`). All five arms have the same original task/reset seed, with native zero target-arm holds t=2 and t=3 in faulted arms; 32/32 fault states hit both artificial interventions. Each arm physically ran; no test-label counterfactual splicing.

| Actual source-policy/controller | Official task success / 32 | *Decision-time* private target reads |
|---|---:|---:|
| Unfaulted PPO competence | 31 | 0 |
| Fully informed private-target diagnostic oracle | 26 | Continuous, never 0 cost |
| Corrected fixed-t4 authoritative readback | **26** | 32 |
| Prior finite-SO3 candidate robust/read-on-refusal | **18** | 26 |
| Reachable-SO3 native ball search/read-on-refusal | **18** | 26 |

New versus corrected fixed: matched discordance **1 new-only, 9 fixed-only**, exploratory unadjusted two-sided McNemar p=`0.021484375`. The preregistered joint task-and-read saving gate **FAILED**. New versus old: **0 discordant successes, 0 actual read saving**. Do not retrospectively retune gates.

### Original first-implementation and actual action trace verification

At the separate Pull/Stack *development* 64-reset study, the improved candidate search resulted in 45 versus 46 old task successes, 40 versus 41 original target reads, and 891 versus 865 bounded action authorizations. When interrogated at the source-action trace level, **only 2/64 original reset states changed any full native command** (both StackCube); PullCube 32/32 actions were exactly identical.

The new, independently locked PickCube native output shows **32/32 complete old-versus-new dispatched action traces exactly equal**, not just equal binary task success. Thus **94/96 historical+new unique reset states retained the original exact native actions**. The 96 total is a cross-task descriptive account; the 64 original method-development states must **not** be added to the 32 newly held-out PickCube states as if all 96 were a single prospective test population.

### Source-only task-outcome prediction follow-up (development, not new holdout)

Across 96 source resets, each corrected-fixed arm and each original reactive arm dispatched **identical actions for steps 0 and 1 (96/96)** before both simulated target holds. Accordingly, pre-fault source PPO native actions can legitimately be exposed to a *future* choice-of-controller-regime predictor without privileged target reads. Paired potential outcomes are separately actually executed, but any switching policy must make its choice by t=2 before the controllers diverge.

A development-only, source-action-feature LogisticRegression trained with leave-one-task-out evaluation over Pull, Stack and now already-exposed Pick tested C={0.01,0.1,1,10} and ten thresholds between 0.05 and 0.9. Of these 40 **posthoc diagnostic** settings, none reduced readbacks without net task-success sacrifice. No chance-level inference or impossibility theorem applies to all models; richer task-feature models may eventually perform differently. The fourth pretrained task PushCube has **not** been used for hyperparameter selection or exposed to this new critic's results.

## Gate classification

- [x] Model source frozen and SHA checked; pre-outcome seeds/arms frozen.
- [x] All four source trials, exactly 32 independent reset clusters and 160 genuine separate controller runs.
- [x] All 32 native fault interventions reached, no failed reset silently removed.
- [x] Corrected fixed-t4 and fully informed oracle comparator included.
- [x] Native action trace comparison reveals no improvement on new PickCube task.
- [x] Original complete Pubic CI archived; human author can independently recount source rows.
- [ ] Reachable search outperforms baseline: **FAILED**.
- [ ] New task-risk learning model gives validated deployment advantage: **NOT ACHIEVED**.
- [ ] Robot hardware safety, true network ACK fault, outside independent laboratory replication and external peer-reviewed recognition: **NONE**.

### Preserved original public evidence

[Original all-five-arm GitHub CI run #38550286593](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38550286593), including original 4 shard JSONs+logs and independent frozen final results `pickcube-32-original-full-denominator-all-five-arms`.

Independent review specification: `research/EXTERNAL_INVESTIGATOR_REPLICATION_PACKET_20261014.md`.

**Scientific decision:** Stop claiming pure geometry improves task recovery. Candidate next algorithm needs a target-test-blind task-controllability/value model, provenance and calibrated uncertainty, with an additional untouched task / robot and all strong information baselines under equal information and action-cost budgets. Mathematics of SO3 midpoint and standard logistic gating are PRIOR ART; neither standalone justifies main-track original-algorithm claims.
