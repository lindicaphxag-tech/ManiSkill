# Flagship One-Pager — Closed-Loop Controller Migration

## Working title

**Can a Frozen Robot Policy Survive a Controller Swap?  
Closed-Loop Controller Migration with Stateful Adapters and Refusal Certificates**

## Problem

A robot policy does not act directly on physics. It emits an action into a
controller that owns:

- an action chart and normalization convention;
- physical bounds and saturation;
- a reference state;
- optional internal target / integrator / filter state;
- interpolation and control-rate semantics.

Replacing that controller can therefore change the executable policy even when
the policy weights and action tensor shape stay unchanged.

The research question is:

> Given a frozen policy and two concrete controller implementations, can we
> compile a migration layer that preserves a declared closed-loop physical
> behavior? If not, can we explain why exact migration is impossible?

## Proposed compiler contract

Input:

- frozen policy action interface;
- source controller implementation;
- target controller implementation;
- declared physical observable / behavior to preserve;
- optional local plant response.

Output:

- **EXACT**: state/action adapter plus equality certificate;
- **APPROXIMATE(ε, Ω)**: adapter plus validity region and finite-horizon error
  bound;
- **REFUSE**: constructive witness such as unreachable actuation direction,
  hidden-state incompatibility, or saturation.

## Mechanistic core already implemented

### Local closed-loop transport

For local models

```
source: x' = A_s x + B_s u_s
target: x' = A_t x + B_t u_t
```

synthesize

```
u_t = K_x x + K_u u_s
```

subject to

```
A_t + B_t K_x = A_s
B_t K_u = B_s.
```

Projection residuals provide a constructive unreachable-direction witness when
exact transport is impossible.

### Different-dimensional controller-state handshake

For source state `s` and target state `t`, jointly synthesize

```
t = Hs
v = K_s s + K_u u
```

with output and dynamics obligations

```
C_t H = C_s
A_t H + B_t K_s = H A_s
B_t K_u = H B_s.
```

### Reference-ownership impossibility witness

ManiSkill currently implements both:

```
current-relative: target = current_qpos + delta
target-relative:  target = previous_target_qpos + delta
```

The second form owns hidden dynamic state.  For two executions with identical
policy-visible `(q,d)` but target histories `r_a != r_b`, any shared
memoryless adapted action leaves the target goals separated by `r_a-r_b`.
At least one execution therefore has residual

```
>= ||r_a-r_b|| / 2.
```

A stateful adapter removes the obstruction exactly with

```
v = q + d - r.
```

This is the clearest current example of why flat action-contract metadata is
not enough for controller migration.

## Real-stack anchors

### ManiSkill #429

Real reported failure:

`pd_joint_delta_pos -> pd_joint_pos` replay has 0% success.

Current diagnosis:

```
normalized source action
-> physical delta q
-> physical absolute target q
-> target controller native action chart
```

A minimal two-file upstream patch and end-to-end regression already exist.
Official-demo trajectory A/B is currently the highest-priority evidence gate.

### robomimic #270

Maintainer explicitly invited an absolute->delta feature PR.

Prepared candidate:

- inverse robosuite OSC scaling;
- SO(3) inverse composition;
- recorded-state baseline pose;
- legacy/current controller layouts;
- explicit saturation evidence;
- clean one-commit PR branch;
- focused semantic CI green.

### LeRobot #3312

Maintainer explicitly invited ACT relative-action support.

Prepared candidate:

- opt-in ACT relative action pipeline;
- fixed action-chunk reference ownership while queue drains;
- excluded absolute joints such as gripper;
- one-commit final branch;
- focused tests plus formatting, typing and security checks green.

## Competitive boundary

Do **not** claim novelty for:

- hidden action-contract discovery;
- permutation/sign/scale/frame/lag identification;
- showing frozen-policy failure under hidden static ABI shifts;
- online probing to identify a hidden action interface;
- generic simulation/bisimulation relations or CEGIS.

ActionABI and ActionShift already occupy much of that space.

The candidate novelty is the **implementation-to-closed-loop migration
compiler**: controller-owned state, physical actuation feasibility, stateful
adapter synthesis, and proof-carrying refusal on real robot-learning stacks.

## Current evidence

Public CST full suite:

```
79 passed / 0 failed
```

Includes:

- exact / approximate / impossible local transport;
- finite-horizon bounds;
- regional shared-adapter consistency;
- frozen-pool counterexample-guided synthesis;
- controller-state handshake;
- ManiSkill runtime contract extraction;
- joint controller migration matrix;
- robomimic OSC inverse semantics;
- reference-ownership impossibility lower bound.

## Hard promotion gates

**L8 achieved only after:**

1. real ManiSkill trajectory A/B shows a meaningful baseline-fail -> fix
   recovery or produces an equally informative negative result;
2. at least one relevant upstream maintainer reviews / merges a CST-grounded
   integration;
3. second-stack integration survives upstream review or independent replay;
4. paper claim is explicitly differentiated from ActionABI / ActionShift.

**L9 requires more:**

- independent third-party use / reproduction;
- broad cross-stack validity rather than one or two hand-picked controller
  families;
- strong external paper-level recognition or maintained ecosystem adoption.

Current status: **L8-candidate, not L8 achieved. Not L9.**
