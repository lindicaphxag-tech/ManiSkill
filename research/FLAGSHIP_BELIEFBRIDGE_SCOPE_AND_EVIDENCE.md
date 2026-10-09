# BeliefBridge: Trust-Conditional Control under Hidden Target-Memory ABI (research flagship candidate)

**Evidence grade: original contributor-run frozen-PPO PhysX experiments, not a paper acceptance, real robot test or independent external reproduction.**

## One-sentence problem
A pretrained policy generates achieved-pose-relative Cartesian actions, but a deployment controller integrates actions around a *hidden previous commanded target*. One unobserved/unknown action acknowledgement turns the target memory into a belief over different poses. Blindly interpreting the command as executed is a semantic contract breach.

## What already ran and what is NEW
- **Original 1-ACK real native PhysX:** two frozen published ActionShift PPOs, 64 fresh matched task states, adaptive bounded-action/conditional target read: **58/64** task successes using **17** real privileged decision reads. Predeclared periodic fixed-time query: **47/64** success using **16** reads. [Full native evidence and original statistics](./frozen_policy_transfer/CERTIFY_QUERY_PERIODIC_PLACEBO_64_ORIGINAL_RESULTS.md).
- The 1-ACK result is *not* a matched exact query count (17 vs 16), learned active-sensing superiority, second-controller transfer, hardware safety or independent replication. The very limited two-PPO task family matters.
- **New 2-ACK / multi-history extension:** preserve up to 16 possible commanded target poses over repeated unknown delivery acknowledgements. Use exact axis-box translation minimax plus conservatively chosen orientation commands; then **check every physically realizable candidate target**, authorize only within the user-defined *commanded-setpoint* tolerance. Otherwise make one explicit privileged query or stop.
- The earlier **v1** real PhysX run [#37897829784](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37897829784) failed because a post-dispatch certificate audit incorrectly treated an *injected masked/held command* as executed. The auditor did the correct thing by failing hard. The v2 design preserves that failure as [explicit prior evidence](./COMPOUND_ACK_MULTI_HYPOTHESIS_PRECOMMIT_V2.md) and separates a requested-but-held action from a truly dispatched native action.
- [New multi-ACK source code](./frozen_ppo_compound_ack_multi_belief.py) | [Conservative K-history SE(3) certifier](./multi_ack_se3_bounded.py) | [Seven adversarial and randomized correctness tests](../tests/test_multi_ack_se3_bounded.py) | [original PhysX v2 workflow](../.github/workflows/compound-ack-multibelief-physx.yml).

## Why this could be original research rather than a geometric recipe
The *systems question* is when an unchanged learned motor policy can safely **continue without knowing which stateful actuator target actually exists**, and when it must obtain new external authority. The novelty claim, if supported, would be in the **closed-loop composition of a changing multi-hypothesis controller memory, representable robust native actions, and costed authoritative interventions**, rather than in existing two-point geodesic or Chebyshev midpoint formulas.

### Relevant prior work and how our precise scope differs
- Feng et al., [Demystifying Action Space Design for Robotic Manipulation Policies, ICML 2026](https://proceedings.mlr.press/v306/feng26ab.html): a systematic empirical study of action-space choices. Our target is *post-training, runtime ambiguity about private commanded-target memory*, not comparative imitation-learning parameterization.
- Lee et al., [SPACE: Enabling Learning from Cross-Robot Data Toward Generalist Policies, 2026](https://arxiv.org/abs/2606.24049): cross-robot Cartesian state-delta learning with adaptive command execution. We **do not** claim the general cross-embodiment objective or action-adapter concept as novel; only a specific hidden-ACK, stateful-controller memory belief and conditional readback intervention.
- This is not a general safe-robot-control theorem. There is no force/contact/collision safety proof, no real network packet loss, and the controller chart and full hypothesis set must be verified.

## Native experiment acceptance gates
1. **Source integrity:** previous single-fault runner and its exact 2-state certifier remain byte-frozen.
2. **Honest fault model:** both t=2/t=3 neutral/hold commands actually replace arm commands; gripper still executes; acknowledgement information is unknown to the adapting algorithm.
3. **Bounded actions:** every *actually dispatched* certified command is independently audited by the native simulated controller after stepping. Masked commands are labeled **not actually executed**, rather than counted as successful bound checks.
4. **Complete denominator:** both frozen-policy tasks and all eight new seeds/task included; seven matched controller worlds each; actual task success, priv-target decision reads, max belief width, fault counts and failures retained.
5. **Scientific win gate:** a favorable success/query frontier compared with never-read, mandatory-read and strong budget-matched alternate read policies on a second seed-disjoint cohort. If the new 2-ACK model does not exhibit >2 actual surviving beliefs, do not claim the four-state extension was exercised in real PhysX.
6. **External acceptance:** an outside researcher must run the real native PhysX and confirm the source hashes and outcomes independently. Our own GitHub Actions do not constitute outside acceptance.

## Graduate-admissions reviewer entry point
The model-integration competence is already independently externally validated by accepted Braindecode upstream work; the **original research claim must stand or fall on native PhysX evidence**, not the number of PRs or this page's prose. Open the [workflow logs](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/compound-ack-multibelief-physx.yml), inspect the source-frozen protocol, and check the *failed v1* as carefully as a successful rerun.
