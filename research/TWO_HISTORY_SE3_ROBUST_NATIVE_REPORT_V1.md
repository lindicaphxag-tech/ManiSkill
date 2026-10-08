# Two possible target histories: a bounded common SE(3) command instead of unconditional refusal

**Scope:** actual native target-controller setpoint validity only. New *conditional* two-history certificate and four preregistered real PhysX target-state replays. Not a simulated network ACK loss, task-success study, hardware safety, independent reproduction or accepted robotics paper.

## Why this method is a meaningful additional control operation

Earlier unknown-ACK closed-loop experiments in this repository showed that a strict 'one common EXACT command or refuse' finite-belief gate refused all 16 affected episodes. Another separately tested arm recovered only after a privileged one-shot public/target-state readback. A realistic intermediate question is whether **the command can remain within specified nonzero error budgets for BOTH still-plausible target histories**, without making the unjustified claim that the ambiguous ACK has been resolved.

Fix two target-controller previous command states, `M_A=(p_A,R_A)` and `M_B=(p_B,R_B)`, whose completeness/provenance is assumed independently verified (a boolean parameter in code is NOT a cryptographic attester). For a source-intended physical commanded pose `D=(d,R_d)` and Panda destination chart

`p_new = p_old + u`, `R_new = R_u R_old` (root translation, root-aligned left rotation),

choose the following single physical command for both histories:

- **Translation, infinity norm:** let `c=(p_A+p_B)/2`, clamp `u=clip(d-c,[u_min,u_max])`. The exact worst-case target-position infinity residual is `max_i (|p_Ai-p_Bi|/2 + |d_i-c_i-u_i|)`. This is a standard interval Chebyshev-center formula, not a new mathematical theorem.
- **Orientation, SO(3) geodesic:** let `R_mid = R_A Exp[0.5 Log(R_A^{-1}R_B)]` on the shortest geodesic; issue `R_u=R_d R_mid^{-1}`. The worst-case geodesic orientation error after applying this same **left-multiplied** increment to either possible previous orientation is exactly half the original `SO(3)` separation, **provided the delta's exact Euler XYZ native representation is legal and no further native clipping occurs**. If the native rotational action norm exceeds its unit ball, or the chart is wrong, it refuses rather than silently projecting and mislabelling the bound.

Authorization requires explicit completeness and trust of both possible histories, freshness and a verified controller action chart. Each of the measured worst-case position/rotation residuals must be strictly inside independently set budgets with a numerical guard. A single candidate hidden history is a different problem (covered by the existing exact prior-memory inversion); this module intentionally does not assert a general many-hypothesis SO(3) minimax solution.

## Precommitted native validation (outcome unobserved when protocol frozen)

- [Frozen protocol commit `5461354`](https://github.com/lindicaphxag-tech/ManiSkill/commit/54613544ddd0bcffe248b495574e63244d10bdf5), JSON Git blob `dbc71a130a336fe9c37e3fcb1ec2b263d4d6e0b1`.
- Four original Pick/Push/Pull/Stack seeds 13077 / 14088 / 15099 / 16110, two genuine unmodified Panda PhysX environments per task.
- Same achieved EE pose and robot qpos; B's saved native prior controller target is **artificially** offset +0.02 m in x, +0.03 rad around root z via official `set_state`. The policy-intended common commanded target is A's prior commanded pose plus +0.005 m in z, original rotation.
- **The exact same normalized 6D action** must be sent through official `env.step()` to both worlds, without changing the target after dispatch.
- Predeclared budgets: 0.0105 m position and 0.0155 rad orientation; theoretical optimal residuals are 0.01 m and 0.015 rad; native records must be within 0.0101 m and 0.0151 rad, without any action saturation. Missing provenance, stale or incomplete hypothesis set, wrong controller, or inadequate translation/rotation budget must return no action before dispatch.
- CPU-only tests include 320 independent deterministic randomized two-quaternion target-pose pairs and 100 translation action-grid comparisons, in addition to trust, ambiguity, representability, finite-input and strict-boundary regressions.

## Scientific limitations essential for a credible paper

The geometric midpoint formula is elementary existing geometry. This method cannot infer two possible previous targets from images, guess dropped command delivery truth, certify a sensor signature, monitor physical actuator tracking or certify collision/contact safety. It assumes the controller follows the documented left-root rotation increment and exact target update, **not** general SE(3) body-frame dynamics; it does not handle three or more unrelated orientations. The optional trusted flag requires an external verifier of actual reset+ACK history to deserve the adjective 'trusted'.

Real task-level gains after *ambiguous or dropped* command acknowledgements require a separate fresh pre-registered rollout, and a fair comparison against strong equal-information belief observer, safe-stop, mandatory readback, oracle and learned adapter. No such gain is claimed here.

## Why this is a publishable direction rather than another success-rate ablation

The research question becomes whether the interface should issue **EXACT / BOUNDED / REJECT / QUERY** according to the known information and the task's error tolerance. The exact vs bounded condition can be checked before actuation, and adverse source histories are explicit. The next falsifier must test authorization errors and actual end-effector/contact outcomes under controlled ACK faults, not only the current one-step commanded-target semantics.
