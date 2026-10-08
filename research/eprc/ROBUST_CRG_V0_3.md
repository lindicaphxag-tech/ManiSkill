# Robust CRG — uncertainty-aware repairability certificates

## Problem

The nominal CRG uses a point estimate of the local physical repair map

\[
\hat G = \hat C \hat J.
\]

A nominally exact repair can still fail when counterfactual probes, controller
semantics, or local linearization are uncertain. Therefore a binary decision
from \(\hat G\) alone can be overconfident.

## Uncertainty set

Assume

\[
\|G_{\rm true} - \hat G\|_2 \le \epsilon_G.
\]

When separate bounds are available,

\[
\|C_{\rm true}-\hat C\|_2\le\epsilon_C,\qquad
\|J_{\rm true}-\hat J\|_2\le\epsilon_J,
\]

the capsule uses the conservative product bound

\[
\epsilon_G
\le
\|\hat C\|_2\epsilon_J
+
\|\hat J\|_2\epsilon_C
+
\epsilon_C\epsilon_J.
\]

## Three-way runtime decision

For a support-space radius \(r\), target correction \(d\), and tolerance \(\tau\):

### CERTIFIED_REPAIR

A candidate \(\xi\) is robustly valid when

\[
\|\hat G\xi-d\|_2 + \epsilon_G\|\xi\|_2 \le \tau.
\]

The left side upper-bounds the residual for **every** admissible physical map.

### CERTIFIED_IMPOSSIBLE

Let

\[
\hat\delta = \operatorname{dist}(d,\{\hat G\xi:\|\xi\|\le r\}).
\]

All admissible repair sets lie within Hausdorff distance at most
\(\epsilon_G r\) of the nominal set. Therefore

\[
\hat\delta-\epsilon_G r > \tau
\]

certifies that no admissible local physical map can repair the target within
tolerance.

### INCONCLUSIVE

If neither inequality holds, the correct action is not to guess. The runtime
must collect additional probes, reduce the perturbation, switch controller /
policy, or replan.

This is the central addition over nominal CRG: **uncertainty creates an explicit
abstention band around the repairability boundary rather than silently changing
a threshold.**

## Robust controller authority

For linear authority \(Ha\le h\) and uncertain action-support Jacobian

\[
\|J_{\rm true}-\hat J\|_2\le\epsilon_J,
\]

constraint row \(i\) obeys

\[
H_i(a_0+J_{\rm true}\xi)
\le
H_i a_0
+
\left(
\|H_i\hat J\|_2+\|H_i\|_2\epsilon_J
\right)\|\xi\|_2.
\]

This yields a robust support radius before physical repair is synthesized.

## Empirical versus formal bounds

The implementation can derive an observed operator-norm envelope from repeated
counterfactual probes. That envelope is explicitly labeled **empirical**; it is
not presented as a statistical confidence interval.

A paper-level formal guarantee requires the stated operator-norm bound to be
justified independently (for example by bounded sensing noise, a calibrated
finite-difference error bound, or a validated local model class).

## Decisive experiment

For held-out perturbations, compare:

- nominal CRG;
- robust CRG;
- generic controller projection;
- perturbation magnitude;
- controller headroom;
- raw Jacobian norm.

Primary quantities:

1. false-accept rate among predicted-repairable cases;
2. certified coverage;
3. inconclusive fraction;
4. recovery success conditional on certificate;
5. calibration of the zero-margin boundary.

The main claim fails if robust CRG does not reduce false accepts at useful
coverage, or if generic projection matches it.
