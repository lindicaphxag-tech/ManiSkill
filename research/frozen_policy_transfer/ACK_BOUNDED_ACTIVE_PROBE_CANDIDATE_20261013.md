# Bounded-response active ACK probe design (research candidate)

**Status:** source/test prototype; no new native PhysX experiment, original
task-success improvement, real-world sensor validation, or official upstream
ManiSkill adoption is claimed.

## Mechanism

For each hidden action-execution history h, a *common prospective candidate*
native probe has a predicted hidden target `m_h(a)`. Conditional on an
**independently validated** response contract, the publicly observed next XYZ
is in

`S_h(a) = { x + alpha (m_h(a) - x) : alpha in [alpha_min, alpha_max] } + B(epsilon)`.

Here `B(epsilon)` is a 3D model-and-sensor-error ball, **not an empirical
confidence interval**. For candidate action a, calculate

`gap(a) = min_{h != h'} distance(Segment_h(a), Segment_h'(a)) - 2(epsilon + guard)`.

If `gap(a) > 0`, the response sets are pairwise disjoint, so an observation
inside the assumed true-history response set cannot also belong to another.
Select only an admissible, pre-outcome candidate that maximizes
`gap(a) / action_cost(a)` under a frozen action budget. Otherwise abstain.

The exact finite-segment separation minimization is a convex quadratic over
two scalars in [0,1]. Its solution lies at an interior stationary point or on
one of four edges; the implementation checks both, including parallel,
collinear, and degenerate cases. Cost does **not** imply safe execution.

## Existing evidence / falsification

- Local CPU suite: 8 tests passed, including 100 independent dense-grid
  comparisons against the geometric minimizer, misleading-overlap
  counterexample, monotonic noise rejection, multiple histories, admissibility
  and strict-budget checks.
- This prototype **does not estimate** alpha, epsilon, actuator admissibility,
  action costs, or `m_h(a)` from real robot state. Caller-supplied attestation
  booleans cannot themselves authenticate those assumptions.
- Prior original native PhysX 1280-world factorial results are related
  motivation only, **not results obtained using this algorithm**.

## Mandatory prospective original-experiment gates

1. Precommit candidate native action set, physical cost units, matched
   two-policy/ACK histories, native dispatched action logs, and an
   independently estimated response envelope on disjoint calibration states.
2. Execute the SAME selected predecision action under every paired truth and
   comparator. Verify actual controller target + achieved SE(3) prefix match
   before attributing any post-probe difference to the new estimator.
3. Compare zero-probe, fixed nonzero-probe, arbitrary candidate, active
   geometric-margin selector, and authoritative target getter at equal
   public sensing, action, time and privileged-read budgets.
4. Measure exact wrong-confident history identifications, abstention, private
   target reads, contacts, full task success and cluster-aware uncertainty
   across disjoint resets. Report non-identifiable histories and failed
   envelope calibrations as explicit negative evidence.
5. No safety or generalization claim absent fresh cross-robot and held-out
   controller-policy validation.

The engineering goal is to transform observed *passive non-identifiability*
into a falsifiable **action-conditioned hypothesis separation method**; its
novelty and value must still be demonstrated against established active
system-identification and set-membership methods.


## CRITICAL prior physical negative control (must not be omitted)

A **previously completed and precommitted** Panda+xArm6 original PhysX study
ran 16 reset clusters x two actual hidden ACK truths x two executed probes
(zero versus fixed +0.15 native X), producing 64 test worlds.
Both probes recovered **32/32 correct histories**, with zero wrong-confident
answers, zero abstentions, and 32/32 corrected native target XYZ.
The nonzero arm increased average observed separation by only ~0.415 mm
(Panda) and ~0.444 mm (xArm6) and **did not improve any decision**.
Source: `research/frozen_policy_transfer/ZERO_VS_NONZERO_PROBE_PANDA_XARM6_ORIGINAL64_RESULTS.md`.
This is scripted native control, not learned PPO/VLA task success, and does
not independently calibrate a deterministic physical-response envelope.

**Null certificate added in this branch:** For
`y_h(a) = x + alpha*(m_h(0) + u(a) - x) + e_h` with fixed shared
`alpha`, history-independent common shift `u(a)`, and action-invariant
bounded noise support, every pair of response centers has separation
`alpha*(m_h(0)-m_k(0))`, independent of the probe. Thus an expensive
common probe cannot improve ideal observation-ball pairwise separation.
The module explicitly tests the common-shift assumption and refuses the
claim when the physical gain/noise assumptions lack external attestation.
This identity is elementary algebra **not claimed to be a new theorem**.
It does not extend unchanged to uncertain shared gain, contact dynamics
or history/action-dependent nonlinear response distributions.

**Scientific consequence:** A positive gain from the new method requires
an action that changes history-*relative* observability under a genuinely
measured response model, not an arbitrary translation of the targets.
Under the old high-SNR Panda/xArm6 task, there is no room to improve the
32/32 classification count. Any new experimental protocol must first
prospectively demonstrate nontrivial baseline ambiguity and equalize or
explicitly charge actuation magnitude, sample timing, sensing, energy,
privileged target reads, and repeated correlated reset states. If these
gates cannot be met, report a negative result rather than an L10 claim.
