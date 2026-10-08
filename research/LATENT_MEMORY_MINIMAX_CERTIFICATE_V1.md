# Latent Target Memory: setpoint-optimal transport and a refusal certificate

**Status:** original, narrow, proof-backed *robust commanded-position setpoint* subproblem; reusable CPU implementation + adversarial tests. **NOT** an accepted paper, first-known solver, formal hardware safety guarantee, or full SE(3) robot policy adapter.

## Why a second mathematical component is necessary

A frozen policy trained on **achieved-pose-relative** motion produces a desired physical next target d. A target controller using **commanded-target-relative** action instead computes

    next_target = previous_commanded_target + action.

If only the observed achieved end-effector pose x is accessible, two admissible histories can have **the same x and policy output** but different stored previous commanded targets m_A and m_B. The full-information inverted actions are `d-m_A` and `d-m_B`, and can differ while the observation tensor stays valid.

### Identifiability lower bound (before actuator saturation)

Any state-observation-only adapter outputs the **same** command u for both indistinguishable histories. By triangle inequality:

    max( ||m_A+u-d||_infinity, ||m_B+u-d||_infinity )
        >= (1/2) ||m_A-m_B||_infinity.

Thus even unlimited compute, a larger policy, or a stateless Cartesian coordinate transform **cannot** guarantee an error below that bound unless new information restricts the hidden previous target. This is an information limitation, not a statement that every learned history-aware estimator fails.

### Exact robust min-max command with an attested bounded hidden target

For each independent Cartesian position coordinate i, assume:

- the unknown previous target lies in `m_i in [L_i,H_i]`, independently **attested** by an appropriate controller/sensor authority;
- the exact target-control relation is additive `m_next,i = m_i + u_i`;
- physical command `u_i in [a_i,b_i]` is enforced *by the actual native controller*, with known sign, frame and physical units;
- desired commanded target `d_i` is given from a source policy decoder;
- no additional hidden saturation/conversion acts after this physical command.

The optimization problem is:

    min_{u in [a,b]}  max_{m in [L,H]} ||m+u-d||_infinity.

Let `c_i=(L_i+H_i)/2`, `r_i=(H_i-L_i)/2`,
`v_i=d_i-c_i`, and `clip(v_i,[a_i,b_i])` denote the componentwise projection onto the feasible controller command interval. The **closed-form minimax optimizer** is

    u*_i = clip(d_i - c_i, [a_i,b_i])

with optimal worst-case commanded-position setpoint error

    E* = max_i [ r_i + dist(d_i-c_i, [a_i,b_i]) ].

**Proof:** for a fixed u_i the maximum over either interval endpoint equals `r_i+|u_i-(d_i-c_i)|`; minimization under the action interval is exactly 1D projection, independently for each coordinate. Since the infinity norm is the maximum of the coordinatewise absolute errors, the global optimum is the maximum of these optimal per-axis errors. An endpoint of the worst axis witnesses error E* for the returned optimum. No simulation/sampling/heuristic is required for this particular boxed-additive model.

**Command authorization at tolerance epsilon:** if an independently verified, fresh controller-memory enclosure is supplied, and `E*` is **strictly below** the specified tolerance by a numeric guard, the physical *commanded target* error is bounded by epsilon under these explicit assumptions. If `E*>epsilon` (or within the conservative boundary guard), refuse. This is a **guarantee only for the controller's newly commanded SETPOINT**, not the end-effector trajectory, task success, contact force, actuator tracking, collisions or a target frame rotation.

## Reliable provenance is a necessary part of the logic

`research/latent_target_memory_cert.py` refuses when:

- memory bounds are not attested by a trusted independent source;
- the memory update is stale relative to the caller-declared allowable age;
- the actual native controller additive contract/units/frame is not independently verified;
- the robust minimax error cannot satisfy requested tolerance;
- bounds, dimensions, finite arithmetic or time provenance are invalid.

An attestation boolean is merely a *caller declaration*; a real deployment must verify the signed device/measurement proof rather than trusting a user-supplied boolean. Likewise a simple axis-aligned interval is not an empirical confidence interval without statistical assumptions. Never rebrand this certificate as physically safe control.

**Open-loop control cannot resolve hidden-memory ambiguity:** if both plausible latent targets receive the same additive action, the difference between their hidden states remains unchanged. Hence repeated actuator commands *without new target-memory sensing* do not improve this particular state-identification bound. A reliable controller target-state channel or a physically justified contraction/observation model is required.

## Relation to existing real-robot and benchmark results

Our separately frozen official ManiSkill simulated, contributor-run PPO evaluations on four distinct tasks showed a marked gap between **actual** previous-target-memory transport and a matched alternative that substitutes the currently achieved EE pose. In the separately held-out PickCube 22001–22032 cohort, both models had the same policy, spatial action chart and clipping logic: stateful bounded **31/32** vs blind bounded **4/32**. PullCube and StackCube (different published PPOs, 32 unseen seeds each) gave **31/32 vs 14/32** and **30/32 vs 0/32**. PushCube previous cohort gave **29/32 vs 20/32**.

- PickCube original preregistration and raw outcomes: https://github.com/lindicaphxag-tech/ManiSkill/pull/57
- PullCube/StackCube distinct source tasks + raw outcomes: https://github.com/lindicaphxag-tech/ManiSkill/pull/58
- Permanent original nine-file independent 64-state evidence: https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/pull_stack_new_task_64
- Request to the original ActionShift baseline author for voluntary independent scope review: https://github.com/Archerkattri/actionshift/issues/1 (no adoption assumed).

These task-success observations motivate the *latent-state* issue, but **do not test this new interval-memory minimax certificate**, provide actual trustworthy memory uncertainty bounds, or prove the certificate improves task success. Keep the evidence sets strictly separated.

## Originality limits / nearest neighbors

- The minimax midpoint and projection identity itself is standard robust optimization; it is **not** claimed as an original optimization theorem.
- SPACE (Lee et al., 2026; https://arxiv.org/abs/2606.24049) uses a learned online command adapter for state-delta cross-robot transfer.
- TAM (CoRL 2026; https://dongwon-son.github.io/tam-project-page/) applies a reusable learned torque adapter below the low-level controller.
- The potential original niche is **evidence-authorized stateful interface translation under partial target-memory observability**, with explicit indistinguishable-history rejection and exact model-conditional bounds, coupled to an actual maintained target controller. This has *not* been shown novel against all prior action-interface/robust-estimation literature.

## To make it a genuinely strong standalone robotics paper

1. Supply controlled, independently auditable target-memory uncertainty sets from a real/maintained simulator's controller execution and trustworthy sensor receipts; validate the low-level additive model against actual native control.
2. Prospective hidden-memory erasure/latency and stochastic tracking-error tests, with all false authorizations and unnecessary refusals reported, not just task success.
3. Distinct controller family/robot and non-additive/rotating target conventions; reject when the current proof assumptions fail.
4. Compare true-memory oracle, achieved-pose substitute, linear-history memory estimator, learned adapter and no-action gate on matched compute/action limits. Report robust setpoint bounds **plus actual trajectory, task and contact effects**.
5. Third-party independent reexecution and accepted upstream use. The author-side test suite and four related real PhysX tasks do not count as independent use of the new certificate.

## Testability

    python -m unittest discover -s tests -p 'test_latent_target_memory_cert.py' -v

Only Python standard library is required for the certificate/test. Tests challenge false proofs with mathematically indistinguishable hidden histories, action saturation, staleness, untrusted inputs, numeric boundary refusal, and 320 deterministic random adversarial sets of memory endpoints/feasible actions.