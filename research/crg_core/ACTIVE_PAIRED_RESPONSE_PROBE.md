# Live query-budgeted directional policy-response probing

**Status: a small runtime adapter, not yet real-policy-validated.**

## What actually changed

The public CRG main already implements and tests
[`directional_anytime_probes.py`](directional_anytime_probes.py):
four-response paired random-seed central secants, time-uniform confidence
bounds, and an obligatory trusted local secant-to-full-request remainder.
No new concentration theorem or entirely new certifier is claimed.

This contribution fills a *missing runtime pathway*:
[`active_paired_response_probe.py`](active_paired_response_probe.py)
takes an actual policy-query callback, a physical direction, a fixed random
seed list, a fixed budget, verified physical action bounds, fixed
response tolerance, and a previously justified local nonlinearity
remainder. For each seed, it **actually invokes four policy first-action
forward passes** at +/- the chosen physical direction and delegates all
arithmetic to the existing audited functions:

1. `paired_directional_secant()` validates all four output actions and
   rejects values outside the precommitted controller bounds; it does
   not silently clip.
2. `inspect_directional_samples()` computes the original time-uniform
   confidence bound over paired seed secants, adding the externally
   justified full-request locality remainder.
3. Continue only while the evidence is inconclusive and unused policy
   query budget remains. Stop early on conditionally similar/distinct
   means, or conservatively abstain when exhausted.

The result labels explicitly distinguish **conditional mean response
similarity permitting policy transfer**, **distinct means prohibiting
transfer**, query-budget abstention, and untrusted assumptions.

Each seed costs **four frozen-policy first-action evaluations**. Even
when an attempted four-call round returns invalid values, four calls
are charged to the budget conservatively. A real wrapper must still
record its true forward-pass count when an exception interrupts a round.

## Why this matters after two genuine negative studies

The [original frozen 20-pair study](evidence/pusht_cross_policy_20case_v2/)
**failed** DEC-distance transfer (rho 0.145 vs raw Jacobian 0.347).
The [fresh 13-state conformal pilot](evidence/conformal_fresh_13state_v1/)
spent 702 queries and authorized **0/8** transfers; Diffusion's
three-seed full-Jacobian stability gate failed **13/13** times, and the
calibrated interval radius **2.404** exceeded response tolerance 1.0.
All these records remain permanently public.

The alternative is a *concrete action-specific query process*, rather
than spending samples estimating an entire stochastic Jacobian even if
the user only requests one physical response direction.

A successful future result must show **nonzero** correct transfer
authorization at matched observation error and policy-query cost on
new, precommitted states. Existing failed states are development data,
not an independent confirmatory holdout. More policy queries may
still end in abstention: this would be an honest negative result.

## Important theoretical and deployment boundaries

The inherited central secant is **not** identical to the full-response
difference at a requested physical intervention. The existing math
therefore **requires an independently justified secant-to-full-request
nonlinearity remainder**. Without it, the adapter rejects before
making any policy queries; more stochastic seed samples cannot replace
proof of physical locality.

Time-uniform Hoeffding control requires IID paired seed draws and
a-priori trusted hard controller-action ranges for **all possible**
stochastic outputs, not empirical ranges from previously sampled draws.
An action outside those bounds is a **failed validity condition**, not
something the proof may silently clip away.

The output only bounds a **stochastic mean first-action response**
under these stated assumptions. It does not ensure any individual
random rollout is safe, validate actual camera calibration, guarantee
task success, or certify collisions cannot happen. Conditional transfer
is not an unconditional safety certificate.

**Prior-art honesty:** common random numbers are standard
variance-reduction methodology (see
[robot learning simulation review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9038844/));
variance control for noisy robotics policy gradients is studied in
[ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4f0a2a0b2ca6ffd5c8d5de26d3e8d54d-Abstract-Conference.html).
The expected contribution, if prospectively validated, is a useful
*query-budgeted policy response decision interface* after real
identifiability failure—not a new general concentration theorem.

## Usage and minimal independent tests

```python
from research.crg_core.active_paired_response_probe import (
    execute_directional_probe_budget,
)

result = execute_directional_probe_budget(
    query_paired_plus_minus_actions=policy_callback,
    physical_direction=[0.1, 0.0, 0.0],
    prespecified_iid_seeds=[...],
    probe_fraction=0.5,
    trusted_action_lows=[...],
    trusted_action_highs=[...],
    locality_remainder_bound=...,  # not obtained from the test outcome
    physical_response_tolerance=...,
    familywise_error_budget=0.1,
    max_policy_forward_queries=64,
    independent_seeds_verified=True,
    controller_bounds_verified=True,
    common_physical_chart_verified=True,
    controller_authority_verified=True,
)
```

The callback must return `plus_a`, `minus_a`, `plus_b`, and
`minus_b` actions. It must record exact frozen checkpoint/source
identity and ensure both +/- observations use the same frozen
physical state and matched per-policy random seed.

```bash
python -m pip install numpy pytest
python -m pytest -q tests/test_crg_active_paired_response_probe.py
```

The tests use **constructed, synthetic outputs only**; they do not
demonstrate variance reduction or authorization benefits on real
Diffusion/VQ-BeT. No external maintainer adoption or L8/L9 paper
performance is claimed.
