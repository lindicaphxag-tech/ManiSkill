# SO(3) invariance: analytic reset-template equivalence is a mandatory control

**Disclosed before reviewing the new heldout experiment outcomes, 2026-10-13.**

Let R0 be the public reset EE orientation (in SO(3)), Y the public measured EE orientation at the ACK decision point, and R_h the source-predicted persistent commanded target for a hidden ACK history h.

For a fixed normalized root-aligned controller action chart with known issued actions, the source forward recurrence is left composition; therefore

    R_h = D_h R_0

for a *known action-history-specific* rotation D_h (ordered compositions of the two frozen prefix and two possibly held actions). The combined D_h depends on h, the public variant command, frame and source chart, but **not** on the unknown reset orientation.

An SO(3) geodesic distance is invariant under common right rotation:

    d_SO3(Y,R_h)
      = || Log(Y R_h^{-1}) ||
      = || Log[(Y R0^{-1}) (D_h)^{-1}] ||
      = d_SO3(Y R0^{-1}, D_h).

Consequently, the proposed source-hypothesis rotation classifier

    argmin_h d_SO3(Y,R_h)

is **mathematically IDENTICAL** to a controller-variant-aware, *analytic reset-relative SO(3) template classifier* whose templates are D_h=R_h R0^{-1}. It is NOT necessarily identical to the preregistered empirical RESET_SO3_BY_VARIANT baseline, whose centroids are fitted from the noisy physically achieved orientation on only four training reset seeds.

This shows why **beating an empirical reset-relative baseline, even with real PhysX, does not establish that source reconstruction has more information than a properly command-aware analytic reset-relative model**. The latter uses the same issued-action/chart information in a different coordinate representation. The variant-matched empirical baseline remains a fair practical sample-efficiency comparator, but its inferiority would not confer a new mathematical information source on source reconstruction.

### Prospective and post-outcome reporting rules

1. Retain the **original** preregistered five methods and the frozen >=3/4-seeds, +0.01rad gate. Do not modify the planned source model, models, raw worlds or missing-case denominator.
2. In the independent post-outcome audit, add a NON-TUNED analytic equality check for every public measured Y and every fixed predicted candidate: compare both minima and full four-way angular distance vectors. This is a mathematical identity and not a sixth trained real physical policy.
3. If the empirical RESET_SO3_BY_VARIANT loses, make the narrow claim "source analytic model beats a 4-seed empirical reset template in this narrow simulation" only; if it ties/wins, report that failure as evidence against a unique source-derived advantage.
4. A genuinely distinctive method must handle **uncertain** source controller contract/motion dynamics/ACK belief, prove risk-sensitive abstention or query authorization against a *fully command-aware, task-aware* baseline, and succeed on independently heldout episodes/tasks. Mathematical parameterization changes are not a new physical information channel.
5. Neither a unit test nor a passed authored GitHub workflow is external academic peer review or an upstream merge.

This conceptual no-go explicitly follows from standard SO(3) bi-invariant geometry. No claim of original theorem priority.
