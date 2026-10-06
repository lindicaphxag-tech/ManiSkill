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
