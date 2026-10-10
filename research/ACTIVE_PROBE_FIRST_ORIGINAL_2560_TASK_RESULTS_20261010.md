# When Active Probing Changes the Thing Being Inferred
**PhysX first registered controller-task experiment · 2026-10-10 · original source audit completed; not accepted or submitted to RSS/CoRL**

## Primary source provenance: actual physically stepped robot task outcomes
- Prospective source protocol registered BEFORE results in `research/ACTIVE_PROBE_TASK_ZERO_X_PREOUTCOME_20261010.json`, original Git blob `9cbe516f24de4c363eb4b6d5ec250d79e83a207a`. NEW seeds PullCube 4100001..4100016 and StackCube 4200001..4200016; same published externally trained PPOs; **four actually injected held/applied consecutive unknown ACK combinations**; t4 active action either known-delivered ZERO or normalized X 0.15.
- **32 independent task reset clusters**, each × four repeated ACK truths × two probe conditions = **256 task-mode/fault cells**, with 10 actual native ManiSkill CPU PhysX controller branches per cell = **2,560 physically stepped controller worlds**. These are NOT 2,560 iid training/test examples.
- Real original producer [GitHub Actions run 38014679801](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38014679801) **all 8 physical shards succeeded**, and every producer generated original source JSON plus per-shard SHA-256 manifests. This is a SOURCE-OPERATED frozen PPO task experiment, not hypothetical outcome splicing.
- Independent retrospective [source-only original archive audit run 38015149933](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38015149933) **PASSED**: downloaded the exact eight original archived artifacts from run 38014679801 without re-running the robots, checked **all 72 source JSON file SHA-256 digests**, paired all seeds/truths/probe modes, verified all 256 task source cells and 384 A/B/C task-outcome records, and computed task-stratified original-reset cluster differences. The verified audit output is in its permanent Actions artifact.
- **Audit amendment:** original [38014272258](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38014272258) failed when a **post-action** source check compared float32 0.15000000596 to Python 0.15 by exact equality; [38014613086](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38014613086) then failed stale source-hash preflight. The later successful physical run used a disclosed 1e-6 normalized-action tolerance and unchanged source weights, faults, probes, seeds and causal hypothesis. The independent audit also needed the identical FLOAT32 tolerance correction AFTER source results were available, and **reused original 8 archived sources**. **This is an amended first registered cohort, NOT an untouched independent confirmation.** Detailed timeline: `research/ACTIVE_PROBE_FIRST_RUN_FLOAT32_AMENDMENT_20261010.md`.

## Actually observed official frozen PPO task outcomes

Every row below has **64 correlated condition pairs per task = 16 independent task reset clusters × four repeated physical ACK truths**. Columns compare *physically executed zero* versus *physically executed X* probe under the same task/fault/control state. All A/B public sensor measurements are counted equally; C is a stronger getter-based comparison with a different observation budget.

| Task | Physically executed controller | ZERO task successes | X task successes | ZERO actual trusted getters | X actual trusted getters |
| --- | --- | ---: | ---: | ---: | ---: |
| PullCube | A: public unique complete-history authority or getter | 62/64 | **61/64** | 43 | 41 |
| PullCube | B: matched-public posterior threshold or getter | 62/64 | **62/64** | 61 | 62 |
| PullCube | C: matched native-action probe then always privileged getter | 62/64 | **62/64** | 64 | 64 |
| StackCube | A: public unique complete-history authority or getter | **47/64** | **38/64** | 47 | 52 |
| StackCube | B: matched-public posterior threshold or getter | **47/64** | **40/64** | 64 | 64 |
| StackCube | C: same actual native probe with authoritative getter | **47/64** | **40/64** | 64 | 64 |

**Total A** ZERO 109/128, X 99/128, **10 fewer task successes**, while ZERO needed **90** trusted state getters and X **93**. **Total B** ZERO 109/128, X 102/128, 7 fewer successes. **Total C** ZERO 109/128, X 102/128, 7 fewer successes. X-induced task harm persists even with controller state properly read; cannot attribute it all to incorrect latent-state classification.

**Actual paired outcome discordances**:
- StackCube A: 12 ZERO-only successes, 3 X-only successes (net −9/64). StackCube B/C: 10 ZERO-only, 3 X-only (net −7/64). PullCube A: one ZERO-only success and no X-only; B/C identical task success across modes.
- The **16 independent resets per task** are the statistical units, not the 64 ACK pairs; source-locked two-sided exploratory cluster sign-flip p for StackCube A = 0.015625, B/C = 0.03125, PullCube A = 1.0. These are **exploratory, unadjusted, conditional deterministic-pairing diagnostics**, not randomized assignment p-values or conclusive population statements. Confidence intervals are descriptive bootstraps by reset, not hardware safety certificates.

## Major discovered failure: incorrect full-SE(3) authority under active X

The original public-geometry authority A makes ZERO observed wrong confident complete controller-state authorizations under ZERO, but **4 wrong confident authorizations under X** (one at each of four independent task resets), even though A explicitly transports its latent-target hypothesis set across the known-delivered X action *before* evaluating public movement.

| Original task reset / actual t2,t3 ACK truth class | X-active wrongly chosen candidate vs audit-only correct | Incorrect target position L-infinity | Orientation SO3 geodesic error | A official task outcome / B,C |
| --- | --- | ---: | ---: | --- |
| PullCube 4100008, truth 1 | selected 3, actual 1 | **72.953 mm** | 0.03131 rad | **A succeeds**, B,C succeed |
| PullCube 4100016, truth 1 | selected 3, actual 1 | **91.674 mm** | 0.01992 rad | **A fails**, B,C succeed |
| StackCube 4200003, truth 3 | selected 2, actual 3 | **40.166 mm** | 0.04949 rad | **A fails**, B,C succeed |
| StackCube 4200004, truth 3 | selected 1, actual 3 | **26.734 mm** | 0.05637 rad | **A fails**, B,C succeed |

These four are *original source evidence labels* derived from privileged full-target getter ONLY AFTER the physical step, never used for online public authority. Error denominators: A ZERO public authorized 38/128, X authorized 35/128; ZERO 0/38 observed errors and X 4/35 observed errors. **Do not interpret 0/38 as guaranteed safe or 4/35 as the population risk**; the original independent units are clusters. B under X observed no wrong confident authorizations but barely authorized in X, typically paying all trusted reads.

**Three** of the four A wrong authorizations caused a physically observed X task failure against successful B/C matched-probe truthful getters, while **one** still finished the official task despite a 72.953 mm incorrect controller-state authorization. Official task success alone can therefore mask latent-controller semantic defects. An observed falsely authorized future target is not a measured hardware collision or motor safety failure.

## What counts as a real next-method improvement
1. **Intervention-aware response-model provenance**: `P(public y | commanded target h_after, action a, physical contact context)` must be specifically calibrated for the action family and controller chart. Reusing the ZERO envelope when X changes both target and trajectory is not a sufficient authorization certificate. Merely translating every hidden hypothesis by X does not repair the action-specific public response likelihood.
2. **Whole-task intervention cost and selective abstention**: actively choosing X must be compared against simply allowing residual servo convergence with ZERO, with equal public samples, step/time cost and independent task success / wrong-authority outcomes. Do not treat any generic positive information score as proof X improves the original task.
3. **Proposed research direction, NOT validated result**: a model-validity-aware passive/active/null-probe router, with identity-bound action-conditioned calibration and explicit readback fallbacks. Its action risk model must be trained on separate physical data and calibrated on independent task reset clusters, then frozen on truly new tasks and controller implementations. An always-ZERO or always-READ trivial strategy is a strong negative control, not a novel positive contribution.
4. Real gains must beat the **proper same-information ActionShift active-belief/probing comparator and a constrained action-conditioned POMDP**, not only a naive memory-blind arm; report errors as full target pose, official tasks, contact/latency/energy, getter and public sensor costs; require independent outside-lab rerun.

## Top paper comparison (no premature acceptance)
- RSS 2024 [TAMPURA](https://roboticsproceedings.org/rss20/p118.html): existing risk-aware partially observable action planning, physical validation.
- RSS 2025 [Map Space Belief Prediction](https://roboticsproceedings.org/rss21/p039.html): learned/calibrated belief update with real-world transfer.
- CoRL 2025 [Belief-Conditioned One-Step Diffusion](https://proceedings.mlr.press/v305/puthumanaillam25a.html): task-relevant sensing with real resource/energy accounting.
- Prior [ActionShift](https://github.com/Archerkattri/actionshift): substantive action contracts and active Bayesian adaptation on the same manipulation stack.

**Current scientific position:** a real, replicated-within-author-run, source-audited causal failure mode across two frozen-policy task families, not a validated new online adaptive method or an L8/L9 top main-track manuscript. The quality upgrade is exposing the counterexample and preserving every negative world, not inflating the paper's novelty.
