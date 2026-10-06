# Scale-limit certificate for local repair models

A local Jacobian can be perfectly repeatable and still fail to approach a
well-defined small-perturbation limit. The public VQ-BeT PushT result is exactly
such a case.

This module separates:

- same-scale stochastic uncertainty;
- center-map drift across perturbation scales;
- robust evidence for or against geometric scale contraction.

For center maps G_k at successively smaller scales, define

    D_k = ||G_k - G_{k+1}||_2.

Each scale also has a repeated-probe operator envelope epsilon_k. Therefore the
true inter-scale drift is conservatively bracketed by

    L_k = max(0, D_k - epsilon_k - epsilon_{k+1})
    U_k = D_k + epsilon_k + epsilon_{k+1}.

For two consecutive drifts, a robust contraction ratio lies in

    [ L_{k+1}/U_k,  U_{k+1}/L_k ].

This yields three outcomes:

1. **NONCONTRACTING**
   Even the most favorable ratio exceeds the frozen q_max. First-order CRG is
   rejected.

2. **STOCHASTICALLY_UNRESOLVED**
   Noise envelopes or too few observed scale transitions prevent a robust
   convergence claim.

3. **CONVERGENCE_SUPPORTED**
   Multiple consecutive worst-case contraction ratios are <= q_max < 1.

For the third case only, the code reports a conditional unseen-scale tail bound.
If future differences continue to contract by q_max, then for the finest
observed drift upper bound U_last,

    ||G_finest - G_limit|| <= q_max * U_last / (1 - q_max).

The finest same-scale stochastic radius is added to form the local-map
uncertainty passed downstream.

This is standard Cauchy/geometric-series numerical analysis. The research claim
is not the inequality. The contribution under test is that **repair authority is
conditioned on evidence that the chosen local model class has an identifiable
scale limit**, instead of treating every repeatable finite-difference Jacobian as
physically meaningful.
