# Local-model admissibility before CRG

A repairability certificate should not be built from a Jacobian merely because
the Jacobian is repeatable.

The public VQ-BeT PushT experiment produced a useful counterexample:

- five paired-RNG derivative probes were exactly repeatable;
- RNG stochastic operator radius was 0;
- coarse→fine drift was about 3.013;
- fine→finer drift increased to about 3.450;
- contraction ratio was about 1.145 (> the frozen 0.75 gate).

That is not an information shortage. It is evidence that the first-order local
model is not empirically admissible at the tested scale ladder.

## Gate

For coarse, fine and finer physical-response maps define

    D1 = ||G_coarse - G_fine||_2
    D2 = ||G_fine - G_finer||_2
    q  = D2 / D1

and an observed convergence order

    p_obs = log(D1 / D2) / log(scale_ratio).

The gate separates three cases:

1. **STOCHASTICALLY_UNRESOLVED**
   Repeated same-scale variation is large enough that scale convergence cannot
   be judged. More paired same-scale evidence is allowed.

2. **FIRST_ORDER_ADMISSIBLE**
   Scale drift contracts beyond the frozen threshold. First-order CRG is
   allowed to proceed.

3. **FIRST_ORDER_REJECTED**
   Same-scale probes are stable but the scale ladder does not contract.
   Additional same-scale queries are forbidden; runtime must requery/replan or
   validate a richer local model.

## Claim discipline

Richardson-style convergence diagnostics and empirical model-order checks are
not new mathematics. The contribution under test is architectural:

> frozen-policy repair is authorized only after the *local model class itself*
> has passed a prospective evidence gate.

This prevents a particularly dangerous failure mode: a perfectly repeatable
Jacobian can still be the wrong object for a piecewise, quantized, saturated or
otherwise non-smooth policy.

## Cross-policy prediction

The next paired PushT experiment uses the same physical intervention protocol
for DiffusionPolicy and VQ-BeT. The important question is not whether one model
has a smaller Jacobian error; it is whether **local-model admissibility itself
is policy-family dependent**.

No architecture-level claim is made until the paired frozen-policy result is
available.


## Stronger scale-limit gate

The three-scale admissibility check is a fast routing gate. A stronger claim
requires multiple consecutive scale transitions plus repeated-probe uncertainty
at every scale.

`scale_limit_certificate.py` therefore brackets each inter-scale drift by the
same-scale operator envelopes and only reports `CONVERGENCE_SUPPORTED` when
multiple worst-case contraction ratios remain below a frozen `q_max < 1`.

Only in that case is a conditional unobserved-scale tail radius exported to the
repair layer. If the favorable contraction bound already exceeds `q_max`, the
local model is rejected; if stochastic envelopes prevent the comparison, the
result remains unresolved.

This prevents `FIRST_ORDER_ADMISSIBLE` from being interpreted as a universal
smoothness claim. It is evidence at the observed scale ladder, with the stronger
limit certificate used whenever a downstream repair needs an extrapolation
toward smaller perturbations.
