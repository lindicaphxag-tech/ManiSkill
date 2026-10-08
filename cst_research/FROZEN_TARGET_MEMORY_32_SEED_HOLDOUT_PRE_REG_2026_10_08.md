# Prospective: frozen PPO action-memory feasible-set holdout

Dated 2026-10-08, **before** starting the associated CI. This is a
new 32-initialization exploratory holdout, disjoint from the target-memory
development seeds [42, 270, 429, 2026] and the different controller-
translation seeds [10001..10032].

## Fixed cohort

**Seeds exactly 20001 through 20032 inclusive**, no replacement or
selective removal. Each trial compares four independently stepped
ManiSkill Panda/PickCube-v1/PhysX CPU environments with the same
registered reset seed and must verify exact *projected* initial 42D
policy observation equality. If the equality check fails, classify as
invalid and disclose, not a task failure.

## Fixed intervention arms

1. Source unchanged public PPO in achieved-relative `pd_ee_delta_pose`.
2. Target-memory compiler `pd_ee_target_delta_pose`, **exact** action
   only; refuse when prior target memory missing or required native action
   lies outside representable bounds.
3. Same target-memory compiler **with bounded approximate projection**:
   when exact target-relative delta is impossible, Euclidean-project
   translation native commands onto [-1,1]^3 and rotational native
   commands onto unit L2 ball. Every non-exact fallback is counted; don't
   present it as a semantic-equivalence certificate.
4. `pd_ee_target_delta_pose` **direct-copy** of frozen PPO native action,
   without controller-memory conversion.

All four policies share the *exact third-party frozen* weight SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`
under `kattri15/actionshift-baselines`; **no training**.
Every target policy input projects out the target controller's verified
extra 7-D pose memory while preserving the source's 42-D observation
layout. The runtime memory remains available to the compiler.
Each policy is evaluated on its own current state. Horizon: 50 steps.

## Predeclared outcome accounting

For **all 32 seeds**: record success_once for each arm, number of
controller action refusals, number of fallback steps, worst requested
normalized action amplitude and episode steps. Unconditional success
count includes any refusal as **not successful**; report refusal
counts separately. Only compare outcomes at a common fixed 50-step
horizon.

Compare bounded approximate vs exact and vs direct-copy, and
bounded approximate vs source as paired differences. Disclose any
seed on which approximation worsens performance. Do not report
post-hoc subsets of only source-success episodes as the primary metric.

A result of high success after non-exact clipping is an empirical
recovery tactic, NOT an exact stateful controller equivalence proof,
and not guaranteed safe in real hardware. We do not claim this
projection algorithm is prior-art novel without further review.

## Decision gate

External top-tier research must additionally show:
- an **independent second manipulation task/controller family**,
- policy competence under same observation ABI,
- an interpretable representability/refusal predictor versus real
  task success, beyond just plotting clamped actions,
- paired negative controls and exact hashes/environment versions,
- independent third-party reproduction or upstream acceptance.

All 32 outcomes including failures must be retained even if this
exploratory holdout contradicts the four favorable development cases.
