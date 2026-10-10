# Causal Authority Recovery — main-track scientific gate (10 October 2026)

**Status: runnable original-source reanalysis + exact FINITE MODEL reference, not a new high-performing robot planner.** Author-operated experiment archival source and subsequent reanalysis remain separate. This note deliberately keeps a research Draft PR open.

## 1. Falsifiable research question

When a controller acknowledgment is missing, the adapter's hidden state is its **previous commanded target/history**, not merely the public achieved end-effector pose. A probe intended to clarify the hidden history is itself a native controller action, and therefore can change the state whose identity the adapter wishes to recover.

A nonintervening public evidence model P(o|h) is not adequate for an active probe that alters the hidden commanded target. The minimal scientifically valid test model is

```
P(h_next, public_observation | h_now, native_probe_action)
```

If a sensor refers to *before-probe* controller state while repair must operate on *after-probe* state, a nominally correct historical label can still authorize an incorrect repair.

## 2. What was actually implemented and checked

**Code:** `research/authority_causal.py`. A small exact belief-space finite-horizon dynamic program jointly propagates public observation and next hidden state, choosing between terminal repair, authoritative native-state readback, and further registered probes.

- Costs and one-step failure/repair chance gates are **model conditional**; not calibrated physical safety bounds or cumulative trajectory risk.
- Before any native execution, the correct policy is checked against independent exhaustive observation-contingent policy-tree enumeration. Random seeded **60 finite transition models**, each at 0/1/2 horizons, are included.
- A standard, exact probabilistic bisimulation quotient merges states only when terminal repair losses, failure flags, and every outcome-conditioned transition probability into existing equivalence classes agree. The finite value of a valid quotient is checked against the unreduced POMDP.
- In a *synthetic* two-state counterexample, a probe observes the old target but forces the new commanded target to the second state. The correct causal repair has expected model cost **0.1** whereas the wrong old-state-labelled repair policy incurs **5.1**; perfect state readback costs **2.0**. **These are deliberately designed loss units, not PhysX measured performance or general algorithm superiority.**
- In a second synthetic counterexample, a probe reveals the OLD state perfectly but randomizes the NEW target independent of it; correct model-optimal policy declines the probe and reads native state. The active change is essential, not an auxiliary noise perturbation.

**Auditor:** `research/review_native_probe_marginal_value.py`. Separately checks SHA-256 of FOUR original heldout native PhysX JSONs, blind classification permissions, exact two fault truths per probe per independent reset, and reconstructs the paired public-motion response distance for zero/X/Y on original Panda/xArm6.

**Immutable source pin:** `876f0355b01250626cf25230f560f607f95dfa5e` from `evidence/low-signal-first192-permanent-20261010`. The relevant preexisting author-operated source has 96 heldout PhysX worlds, but only **16 independent robot/reset clusters** (8 Panda, 8 xArm6). This is an existing archived source, not freshly executed environments, independent outside-lab validation, a second learned VLA policy, or full on-policy task success.

## 3. Findings that REFUTE the common entropy/separation claim

Recalculated from heldout source, mean separation of public XYZ motion for applied versus held ACK, in millimeters:

| heldout robot / 8 independent resets | zero (mm) | X (mm) | Y (mm) | Correct ACK truths per probe |
| --- | ---: | ---: | ---: | --- |
| Panda | 2.964390 | 2.995960 | 2.962331 | 16/16 for all three |
| xArm6 Robotiq | 3.231968 | 3.267744 | 3.241898 | 16/16 for all three |

Relative to zero, X increases the *raw geometric separation* by just **0.031570 mm** on Panda and **0.035776 mm** on xArm6. The per-reset public separation changes consistently in the tested simulation seeds. But all classification decisions are already correct without a nonzero probe, hence **observed incremental classification gain is ZERO**. The author-run archived simulation did not evaluate total latency, probe contact/force/energy or native manipulation completion; those fields must not be invented.

The older stronger fully stepped controller test also fails to establish new-vs-strong superiority: **109/128 identical task-condition successes**, **94 vs 98** private state reads, plus matched 256 public XYZ samples, with exploratory reset-level p=0.289. This is an unfavorable but important comparison.

## 4. How this differs from already published top papers

- **TAMPURA, RSS 2024:** partially observable TAMP with risk, action effects, information gathering and two real-world tasks: https://roboticsproceedings.org/rss20/p118.html
- **Map Space Belief Prediction for Manipulation-Enhanced Mapping, RSS 2025:** calibrated belief updates, POMDP decision making and real-world zero-shot transfer: https://roboticsproceedings.org/rss21/p039.html
- **Belief-Conditioned One-Step Diffusion (B-COD), CoRL 2025:** task-relative just-enough sensing, model/learned uncertainty proxy and real-world resource measurements: https://proceedings.mlr.press/v305/puthumanaillam25a.html

All three have stronger **actual task evidence** than this current proof-of-concept. Our narrow application-specific question is whether command-target **authority** can be decided under action-induced memory changes without implicitly presuming that a public sensor observes a non-intervened state. Neither implementing exact POMDP dynamic programming nor standard probabilistic bisimulation alone is a publishable novel theorem.

## 5. Real acceptance gate for a flagship paper (do not silently waive)

1. **Native causal transitions:** independently learn/test P(h_next, o | h, probe) from *genuinely new* ManiSkill PhysX rollouts. At least three separate groups: train response model, independently calibrate safety/refusal, heldout untouched evaluation. Use exact source/seed manifests.
2. **Coherent counterfactual controls:** same native initial prefix, same public sensors, same action amplitude/energy budget. Include no probe/passive, fixed X/Y, task-aware active controller estimation, true native getter and an honestly implemented action-conditioned POMDP approximation.
3. **Actual task outcomes:** report manipulation-task success, wrong **complete SE(3)** history authorization, abstentions, native getters, public XYZ count, physical actuation steps, force/contact, measured time/energy and potential side effects. Do not reuse an archive with only ACK classification and call this task performance.
4. **Independent reset statistics:** 2x2 ACK conditions and parallel probe arms are correlated within one reset. Hold out robots, fault regimes and policies; cluster CI and prospective primary endpoint.
5. **Open falsifier:** if the exact information- and cost-matched POMDP strong comparator ties or beats a new approximation, report that outcome and demote the contribution, rather than retuning until positive.
6. **External reproduction:** unaffiliated group chooses fresh native simulator initial states and runs physics. Author-controlled GitHub CI audits are not outside-lab adoption.

## 6. Venue and timing decision

**2026 Nov–Dec:** target mature, independently audited EEG papers first; do not label a new robotics controller POMDP as RSS/CoRL-ready. **2027:** only after actual task-level gain across controls/robots and outside reproduction should this controller-memory line attempt RSS / CoRL / RA-L. No claimed acceptance probability or fixed official decision date.

**Repo-level validation:** `.github/workflows/authority-causal-physx-audit.yml` uses 6 Linux/macOS/Windows × Python 3.11/3.13 combinations for the causal reference and separately checks frozen archival source by exact commit + four file SHA256. Keep the branch a Draft while experimental gates are unmet.
