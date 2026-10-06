# Evidence-action routing for inconclusive repairability certificates

The first real VQ-BeT / PushT run exposed an important failure mode for active
probing:

- paired policy replay error: 0;
- five-RNG DEC q95 radius: 0;
- stochastic local-map radius: 0;
- fine-vs-coarse finite-difference scale drift: about 3.01;
- robust CRG: INCONCLUSIVE;
- six additional information-only AMRC probes: still INCONCLUSIVE.

This means the blocking uncertainty is **not missing repeated observations**.
It is observed locality/model mismatch: the finite-difference map changes with
probe scale.

A runtime that blindly reacts to every inconclusive certificate by collecting
more same-scale probes wastes policy queries and can become unsafe by repeatedly
intervening on a system whose local linear model is already falsified.

The evidence-action router therefore separates:

1. **TERMINAL** — the robust certificate is decisive; stop probing.
2. **INFORMATION_LIMITED** — AMRC predicts that a finite targeted probe set
   crosses a certificate boundary; execute only that set.
3. **STOCHASTIC_LIMITED** — repeated-probe variation dominates; improve
   randomness control / replication.
4. **LOCALITY_LIMITED** — probe-scale drift dominates and AMRC cannot resolve
   the certificate; do not spend more same-scale queries. Shrink the physical
   trust region or move to a validated higher-order local response model.
5. **MIXED_UNCERTAINTY** — separate scale and stochastic effects before acting.

## Claim discipline

This is not a new uncertainty-decomposition theorem. The research claim under
test is operational: **certificate failure should determine what evidence to
collect next**, and some failure modes should explicitly forbid additional
same-scale probing.

## Real-policy falsifier

The routing idea is useful only if locality-limited states are actually better
resolved by scale adaptation / higher-order local models than by additional
same-scale repeats at matched query budget. That comparison must be prospective.
