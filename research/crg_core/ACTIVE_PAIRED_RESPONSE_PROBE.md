# Budgeted request-directed counterfactual response probing

**Status: implemented CPU-testable runtime mechanism; no positive official
Diffusion/VQ-BeT prospective performance evidence; no external replication.**

## Why this is a different intervention

Two completed frozen-policy studies are permanently archived:
[20-observation DEC transfer falsification](evidence/pusht_cross_policy_20case_v2/)
and [13-state calibrated transfer ZERO_UTILITY](evidence/conformal_fresh_13state_v1/).
The latter used **702 frozen policy calls**, yet permitted **0/8** real
transfers. Every Diffusion state failed the three-seed whole-Jacobian
q95<0.15 gate, and the calibrated response radius (2.404) was greater
than the fixed action tolerance (1.0). Neither outcome is disguised
as a success.

The first testable *mechanistic alternative* is to drop the requirement
to identify all physical support directions for one concrete action.
For a particular request h and one shared RNG seed z, measure four
policy outputs:

    X(z) = [policy_A(h,z) - policy_A(0,z)]
         - [policy_B(h,z) - policy_B(0,z)].

The desired random variable is the **mean contrast vector**
E_z[X(z)], and the actual decision criterion is ||E_z[X(z)]|| <= tau,
not E_z[||X(z)||]. The per-policy counterfactual observations must
be at exactly the same source state and physical chart; the same RNG
seed is paired across each policy's baseline/intervention pair.
This is common-random-number pairing, not a novel variance-reduction
theorem. Independent state resets, held-out disturbances and
independently drawn RNG seeds remain necessary for a genuine new test.

A runtime controller **makes real probe requests** through a callback,
counts four official policy first-action evaluations per RNG seed, and
stops once a precommitted anytime-valid bound allows one of:

- STATISTICAL_MEAN_SIMILAR: upper bound <= tau, *mean* response transfer
  may be statistically licensed, if all physical assumptions hold;
- STATISTICAL_MEAN_DISTINCT: lower bound > tau, **do not transfer**;
- ABSTAIN_BUDGET_EXHAUSTED: spend no more queries, do not transfer;
- REJECT_UNSUPPORTED_ASSUMPTIONS: never authorize when missing physical
  chart/authority, independently justified bounded contrast or IID draw
  assumptions, or when any observed contrast violates the asserted bound.

## Finite-horizon confidence sequence (conditional, not absolute safety)

Assume d response coordinates, N=floor(max_policy_queries/4) planned
unique IID seed draws, and an independently verified, **almost-sure**
population bound X_j(z) in [-B,B] for *every possible seed*. For each
t=1,...,N the union-bound radius is

    radius_t = sqrt(d) B sqrt(2 log(2 d N / alpha)/t)

and with probability at least 1-alpha across all t<=N,

    max(0, ||mean_t|| - radius_t)
        <= ||E[X]|| <= ||mean_t|| + radius_t.

The fixed budget is **four policy queries per random seed**. Because
the finite-horizon confidence sequence is simultaneously valid at
each t<=N, early stopping based on the current interval does not
invalidate the mean-coverage claim.

**Non-negotiable caveats:**

- Passing a range check on previously observed samples does **not**
  validate B as an almost-sure bound for all RNG seeds.
- Running these fixed numerical seed integers is not automatically
  equivalent to independently random draws; the caller explicitly
  attests the seed-draw design. A hidden model distribution shift
  invalidates the claimed coverage.
- The result only covers a **stochastic mean first action** in the
  same frozen state, not any one random rollout or actual robot
  collision or task success.
- The method still needs calibrated comparison at equal **nonzero
  transfer coverage** and query cost. Always-abstain obtains zero
  wrong transfers but also zero utility.
- Existing 13 archived states were viewed *before* designing this
  method. They are not independent confirmatory test data.
- Correct contrast bound B may be so large that the controller
  always abstains. That would be a valuable **negative outcome**.
- A single four-action callback may fail partway through: no
  decision is issued. The test harness charges a full attempted
  round to avoid understating the budget; the live policy wrapper
  must also record actual model call counts.

## Research novelty boundary and neighboring prior art

Common random numbers and statistical anytime bounds are established.
Policy variance control has direct preceding work: e.g.
[Robot Learning From Randomized Simulations: A Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9038844/)
and the ICLR 2026 paper
[Does “Do Differentiable Simulators Give Better Policy Gradients?” Give Better Policy Gradients?](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4f0a2a0b2ca6ffd5c8d5de26d3e8d54d-Abstract-Conference.html).
No first-ever CRN or confidence-bound theory claim is made.
The research hypothesis is **policy-query selection for a concrete
physical action after an observed full-Jacobian identifiability failure**.

A useful prospective result would need to show real Diffusion/VQ-BeT
paired response sensitivity variance reduction and nonzero mean-transfer
authorization **within fixed action error and query budgets**, versus
independent-random-seed difference probes and local-Jacobian baseline.
If such a result does not exist, the hypothesis is rejected.

## API

```python
result = probe_pairwise_mean_response(
    sample_four_actions=callback,  # policy A/B, base and intervention
    physical_request=[1.0, 0.0, 0.0],
    prespecified_iid_seed_draws=[...],
    hard_coordinate_contrast_bound=B,  # must be justified independently
    max_policy_queries=64,
    response_tolerance=tau,
    alpha=0.10,
    physical_charts_aligned=True,
    controller_authority_valid=True,
    population_bound_independently_justified=True,
    iid_seed_draw_design_attested=True,
)
```

```bash
python -m pip install numpy pytest
python -m pytest -q tests/test_crg_active_paired_response_probe.py
```

The included synthetic counterfactual examples verify the controller's
decision, early stop, input failures and query accounting. They do
**not** count as success on real frozen policies. No L8/L9
research achievement or external adoption is claimed.
