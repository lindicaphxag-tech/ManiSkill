# Flagship brief — Counterfactual Physical Repairability

## Question

A frozen robot policy changes its action when the physical scene changes.

The deployment question is not merely whether that derivative can be estimated:

> **When is the locally identified policy response actually admissible as a
> repair model, and what is the minimum additional physical evidence needed
> before executing or refusing a correction?**

## Proposed runtime decomposition

```text
counterfactual physical probes
        ↓
DEC identifiability
(repeated probes agree?)
        ×
scale locality
(map converges as perturbation shrinks?)
        ↓
local-model admissibility
        ↓
controller authority + CRG
        ↓
CERTIFIED_REPAIR / CERTIFIED_IMPOSSIBLE / INCONCLUSIVE
        ↓
certificate-directed next evidence
```

The central separation is:

[
	ext{repeatable local response} 
eq 	ext{valid local repair model}.
]

## Real frozen-policy evidence

Policy:
`lerobot/vqbet_pusht@390e5e4c079c880b22e873dad53ecfac706bc78a`.

At frozen PushT state seed 17:

- 5 repeated DEC probes: q95 signature radius **0.0**;
- RNG contribution to map uncertainty: **0.0**;
- coarse→fine scale drift: **3.0126**;
- fine→finer scale drift: **3.4500**;
- contraction ratio: **1.145 > 0.75**;
- robust CRG: **INCONCLUSIVE**;
- routed outcome: **REJECT_FIRST_ORDER_LOCAL_MODEL**.

So the method refuses to turn a perfectly repeatable derivative into an
unsupported repair.

Public runs:
- https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37460144227
- https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37460144187

## Prospective disjoint-state evidence

Five states were frozen before a richer response-jet gate was run:

`101, 211, 307, 401, 503`.

The jet hypothesis failed cleanly:

- jet upgrades: **0/5**;
- first-order-failure jet rescues: **0/5**;
- preregistered adjudication: **DROP_JET_FROM_FLAGSHIP**.

More importantly, the states populate all four combinations of the two
admissibility axes:

| state | repeated DEC | scale locality | runtime interpretation |
|---|---|---|---|
| stable | contracts | | ADMISSIBLE_FIRST_ORDER |
| unstable | contracts | | INFORMATION_LIMITED |
| stable | does not contract | | LOCALITY_LIMITED |
| unstable | does not contract | | REJECT_LOCAL_MODEL |

This is observed in one frozen policy/task family; it is not claimed as a
universal taxonomy theorem.

## Constructive component

For an admissible local model, CRG computes whether the requested physical
correction lies in the policy/controller-supported repair set.

A robust impossible decision may return a compact dual witness that an
independent verifier can check without trusting the repair optimizer.

When the bottleneck is information rather than locality, AMRC/certificate
identifiability chooses probes for the **current certificate**, rather than
uniformly identifying the entire Jacobian.

## Strong baselines that must win or kill the paper

The flagship claim should be dropped or narrowed if any of these match it under
prospective evaluation:

1. perturbation magnitude alone;
2. controller headroom alone;
3. one scalar uncertainty score combining repeatability and scale drift;
4. generic action-space residual correction;
5. generic controller-space projection;
6. dense/coded Jacobian identification at matched false-accept rate;
7. a simple “always re-query / always replan” policy at matched query cost.

## Decisive experiments

### A. Two-axis routing

On disjoint states, compare the two-axis router with scalar uncertainty
baselines on:

- wasted black-box policy queries;
- false repair authorization;
- fraction of states correctly routed to more evidence vs scale refinement vs
  rejection.

### B. Cross-policy physical contract

Run the identical PushT physical protocol on Diffusion Policy and VQ-BeT under
one runtime. Compare DEC with raw-Jacobian, support-overlap, and metadata
baselines against fresh held-out physical response.

### C. Closed-loop repair

Only states that pass model-admissibility and CRG gates are eligible. Compare
CRG repair with generic delta/projection and replan baselines. Failed gates stay
in the denominator rather than being silently filtered.

## Claim boundary

Not claimed as novel:

- Jacobians or Taylor expansions;
- equivariance;
- nullspaces;
- convex separation;
- active learning / optimal design;
- controller conversion;
- frozen-policy runtime recovery in general.

Current claim under test:

> **Physical repairability requires separate evidence for identifiability,
> locality, and controller authority; treating those failure modes separately
> can enable proof-carrying repair/refusal with fewer unsafe or wasted runtime
> interventions.**

## External promotion gate

Self-authored CI does not make this L8.

Promotion requires at least one of:

- result-bearing independent replication under the machine-verifiable gate;
- maintained robotics-runtime adoption/merge;
- independent comparison on another frozen policy/controller family.

L9 is reserved for sustained third-party implementation, comparison, citation,
or ecosystem use.
