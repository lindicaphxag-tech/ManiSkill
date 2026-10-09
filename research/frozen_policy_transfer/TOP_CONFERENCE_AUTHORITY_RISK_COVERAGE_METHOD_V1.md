# Can a frozen robot policy *reliably* authorize hidden controller memory?

**Method v1 · 9 October 2026 · runnable mathematics, NOT a validated new robot policy or accepted conference paper.**

## Concrete motivating falsifier

On 64 prospective, previously unused ManiSkill PhysX task resets (640 genuine frozen-PPO comparator worlds), a public end-effector-motion observer achieved 52/64 tasks with 48 true controller-target reads, compared with 52/64 and 64 true reads for fixed readback. But **one out of 16 confident, no-query full-target authorizations was wrong**. At PullCube seed 1760020, two ACK commands both truly executed and the observer selected candidate history 0 while true history was 3, with 67.6 mm position and 0.0536 rad orientation target mismatch—even as official task success was true. [Original SHA256 evidence](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/matched_public_bayes_original640_1760001_1770032).

## New exact statistical research gate

We distinguish two endpoints for a **fixed** public-info rule and task g:

- **Selective error risk** R_g = P(predicted complete history is wrong | authority granted, task g).
- **Nontrivial authority coverage** C_g = P(authority granted | task g).

Trivial always-read control has undefined/no selective errors but C_g = 0, and therefore FAILS the scientific method-promotion gate. Declaring that approach safe would be misleading.

The original public source gives candidate residuals r_i, prior frozen epsilon and competitor margin m. We freeze a source-only score s = min[(epsilon - winner residual)/epsilon, (second residual - epsilon - m)/epsilon]. The score is only evaluated if the ORIGINAL method had already authorized the winner: a stricter gate can revoke an old authorization, never create a new one.

Before new calibration outcomes, register task groups g and a finite threshold grid T = {0, .25, .5, 1}. For each threshold t, original task g has n independent calibration reset states, a(t) originally-authorized states with score >= t, and k(t) wrongly authorized complete target histories (true target is AUDIT-ONLY, not a decision-time input). Compute an exact one-sided Clopper–Pearson risk upper U_CP(k,a; eta) and authorization coverage lower L_CP(a,n; eta), where eta = delta / (2 * num_tasks * num_thresholds). A candidate t is eligible only if **for EVERY registered task** U_CP <= risk_cap AND L_CP >= minimum_coverage. Selection among eligible thresholds maximizes worst-task calibration coverage with a frozen tie break.

**Finite-sample justification:** conditional on independent identically distributed reset trials WITHIN each fixed task group, a frozen public score and a complete source-truth audit, each tail has its nominal CP confidence. Union bounding all 2 x tasks x grid thresholds guarantees at least 1 - delta simultaneous calibration coverage; choosing the best eligible threshold after examining calibration labels is then allowed without pretending the selection was free. The derivation is standard selective binomial inference, NOT a new mathematical theorem. No physical-safe-state guarantee follows under contact shift, unexpected ACKs, changed controller charts, reused seeds, or task distribution drift.

**Power gate:** For risk_cap=10%, delta=5%, 2 tasks and 4 tested thresholds, even with ZERO observed wrong labels, a task needs at least **55 independent confident calibration authorizations** to have a passing error bound. This is 55 authorized cases per task, NOT 55 total task resets or physical comparator trajectories. Existing 1/16 wrong is grossly underpowered for a strong safety claim.

## New predeclared truly unseen cohort, pending actual PhysX

[Pre-outcome frozen protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/risk-coverage-controller-authority-20261009/research/AUTHORITY_RISK_COVERAGE_PROSPECTIVE_V1.json):

| Stage | PullCube original reset IDs | StackCube original reset IDs | Count |
|---|---|---|---:|
| Independent calibration | 2110001–2110256 | 2120001–2120256 | 512 |
| Final locked test | 2130001–2130128 | 2140001–2140128 | 256 |

Both stages use all four actual applied/held double-ACK physical truth patterns, task frozen third-party PPO checkpoints, the original true target-controller chart, and a *physically identical native prefix* before choosing read/no-read. The project must count actual task successes, precise wrong full-target histories, true privileged getters, decision-visible public XYZ frames, neutral probe time, early refusal, and fault injection exposures. Any missing physical source or predecision mismatch invalidates the confirmation rather than being silently removed.

**This is an evaluation protocol, not completed experiments.** A mathematical risk/coverage gate with synthetic tests alone does not demonstrate real robot performance or a better trained VLA policy. If no threshold passes, continue by reading true controller state, but report the *research promotion as FAILED* and do not advertise zero-error authority.

## The top-conference main-track rejection checklist

1. **Novelty:** geometric SO(3) midpoint, binomial CP intervals, abstention and task-regret value of information are established prior art. ActionShift DualABI already performs task-regret-aware active probing and early stopping. The potential original domain problem is latent stateful target-memory transitions under UNKNOWN *execution* despite a KNOWN native controller mapping; demonstrate a new task-effective algorithm, not renamed statistics.
2. **Causal comparator:** match physically dispatched commands, achieved+target full SE(3), t4 known-delivered neutral probe and public observation events before any t5 privileged read. Check first complete raw physical actions, not source-only math. Do not claim same physical prefix for arms that terminated earlier.
3. **Statistical gate:** error CONDITIONAL ON authorization, coverage, missed fault injection, public sensing cost, and readback cost all matter. Report paired seed-level contrasts by task and each of four fault truth combinations. No noninferiority claim from coincident task successes.
4. **Generalization:** second truly independent policy-capable controller/embodiment, contact and sensor shifts, a task-tuned VLA in full closed-loop control (a checkpoint forward pass is insufficient), and an unaffiliated investigator's entirely new task initial states.
5. **Research provenance:** every original seed, simulator failure, calibration source checksum, fixed PPO checkpoint, control charts and exact study-overlap identity must be disclosed. The main algorithm cannot see calibration or audit-only true target at execution time.

## Runnable source artifact

- Method: [finite_risk_authority.py](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/risk-coverage-controller-authority-20261009/research/finite_risk_authority.py).
- Adversarial tests: [test_finite_risk_authority.py](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/risk-coverage-controller-authority-20261009/tests/test_finite_risk_authority.py).
- Cross-platform CI: [3 operating systems x Python 3.11/3.13](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/risk-coverage-controller-authority.yml).

Tests cover observed 1/16 wrong cannot certify, all-read degenerate gate, one bad task cannot hide behind another, finite-grid selection, preventing runtime access to truth labels, reset reuse guard, and 1024–4096 calibration sizes without binomial integer overflow.

**Claims boundary:** source-audited original failure plus executable prospective risk gate; no new prospective real-robot success, no official DualABI head-to-head, no real TCP packet-loss or force/contact safety proof, no independent third-party adoption, and no top-tier paper acceptance.
