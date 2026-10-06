# Certificate-directed locality refinement

This module implements the frozen
`VQBET_LOCALITY_REFINEMENT_PROTOCOL.md`.

It does not choose thresholds from the finer-scale outcome. It evaluates the
pre-registered three-scale ladder:

```text
0.50  ->  0.25  ->  0.125
 Gc        Gf        Gff
```

with

```text
D1 = ||Gc - Gf||_2
D2 = ||Gf - Gff||_2
q  = D2 / D1
```

and a frozen contraction gate `q <= 0.75`.

If the observed drift contracts, the smallest-scale map may be evaluated inside
the separately frozen trust radius `0.125`, using

```text
epsilon_refined = max(finer-scale stochastic radius, D2)
```

as an empirical uncertainty envelope.

If it does not contract, the runtime must not pretend that more first-order
same-scale samples solve the problem. The first-order local model is rejected
for that state.

This is a **model-selection / evidence-routing mechanism**, not a new Taylor or
finite-difference theorem. Its scientific value depends on prospective
multi-state evidence showing that this routing outperforms equal-budget
same-scale repetition without increasing false accepts.
