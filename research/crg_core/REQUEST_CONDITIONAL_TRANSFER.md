# Request-conditioned transfer between frozen policy responses

**Status: conditional mathematical prototype, NOT evaluated on the failed
20-case prospective bank as a new method. No held-out improvement is claimed.**

The completed, immutable [negative 10-state/20-observation bank](evidence/pusht_cross_policy_20case_v2/)
falsified the original claim that a global DEC-signature distance would predict
cross-policy held-out physical responses better than the raw Jacobian baseline:
DEC Spearman 0.145 vs raw baseline 0.347 (threshold 0.50). All ten states
showed an unstable policy. We **do not** post-hoc tune that bank into success.

## A different *mechanism*, for a future prospective test

For a specific physically admissible perturbation h, let two independently
measured policy response maps be Ghat_A and Ghat_B. Require:

- a proven local admissibility gate for both policies and controller authority;
- externally justified operator-norm uncertainty envelopes eps_A, eps_B;
- valid finite local nonlinearity/remainder bounds l_A(h), l_B(h);
- a fixed application-level physical response tolerance tau.

The true response disagreement between the two policies is contained in:

    center = ||(Ghat_A-Ghat_B) h||_2
    radius = (eps_A+eps_B)||h||_2 + l_A(h) + l_B(h)

    max(0,center-radius) <= ||y_A(h)-y_B(h)||_2 <= center+radius

**Runtime decisions:** guaranteed similar if upper <= tau; guaranteed
distinct if lower > tau; inconclusive if the interval crosses tau; and
UNSUPPORTED_LOCAL_MODEL if either policy's evidence, support, or controller
authority is missing.

Unlike ranking complete Jacobians, the outcome depends on the **specific
physical correction direction** and available uncertainty evidence. It can
reject transfer even when point Jacobians appear similar, or tolerate large
Jacobian differences that are irrelevant to the requested direction.

The interval is a conventional triangle-inequality argument; the mathematical
inequality itself is **not claimed as a novel theorem**. The experimental
research question is whether physically justified, intervention-identified
uncertainty and locality gates can reduce **unsafe cross-policy authorizations**
at a useful policy-query cost.

## Strict interpretation boundary

- This module makes **no new policy query**, no repair execution, and no
  claim of real-world collision safety.
- The input booleans and uncertainty bounds are **assumptions from the
  caller**. The returned conditional certificate is **not** externally audited.
- An empirical q95 variability radius is **not automatically a worst-case
  operator-norm bound**. Substituting q95 for eps without a coverage guarantee
  can produce misleading "CERTIFIED" labels.
- For the completed 20-case bank, the correct retrospective model-validity
  response is to **abstain** on the unsupported states, not secretly apply
  this algorithm to rescue its failed frozen hypothesis.
- Any performance claim requires **fresh states and a separately frozen
  protocol before data collection**, with no parameter tuning on the failed
  20-case bank; report coverage, false authorization rate, calibrated
  envelope violations, query cost, and appropriate state-cluster uncertainty.

Run:

    python -m pip install numpy pytest
    python -m pytest -q tests/test_crg_request_conditional_transfer.py
