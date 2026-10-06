# Certified Closed-Loop Semantic Transport (CST)

**Research prototype — not an upstream ManiSkill patch.**

**Reviewer shortcuts**
- Start here: [REVIEWER_ONE_PAGER.md](REVIEWER_ONE_PAGER.md)
- Claim / adoption ledger: [EVIDENCE_LEDGER.md](EVIDENCE_LEDGER.md)
- Reproduction: [REPRODUCE.md](REPRODUCE.md)
- Novelty boundary: [NOVELTY_BOUNDARY_2026_10_06.md](NOVELTY_BOUNDARY_2026_10_06.md)

Latest full public suite: **59 passed**. External maintained adoption: **0**.

Question:

> If a frozen robot policy was trained/deployed with controller A, when can its
> actions be executed through controller B without changing the executable
> closed-loop behavior?

This branch separates two things deliberately:

1. **Upstream engineering fix:** ManiSkill issue #429 exposes a concrete
   `pd_joint_delta_pos -> pd_joint_pos` semantic conversion failure.  The
   proposed upstream fix lives on a separate minimal branch.
2. **Research generalization:** this directory studies when controller migration
   is exact, approximate, state-dependent, region-inconsistent, or impossible.

## Current components

### 1. Local closed-loop transport

For local source/target models

```
x' = A_s x + B_s u_s
x' = A_t x + B_t u_t
```

the compiler synthesizes

```
u_t = K_x x + K_u u_s
```

and checks whether

```
A_t + B_t K_x = A_s
B_t K_u = B_s.
```

If exact matching is impossible, the projection residual produces an explicit
unmatched physical direction witness.

### 2. Regional consistency + counterexample-guided synthesis

Point-wise exact adapters do not imply one deployable adapter works across a
state region.  The regional compiler fits one shared adapter over frozen
linearization samples and adds the worst violating sample as a counterexample.

Current claim: finite-pool certificate only, not continuous-region proof.

### 3. Controller-state handshake

For controllers with different internal memory dimensions,

```
s' = A_s s + B_s u
t' = A_t t + B_t v
```

the compiler jointly solves

```
t = H s
v = K_s s + K_u u
```

subject to

```
C_t H = C_s
A_t H + B_t K_s = H A_s
B_t K_u = H B_s.
```

This makes previous targets / integrators / filters part of the migration
contract instead of pretending action vectors are memoryless.

### 4. ManiSkill joint-controller bridge

The executable contract model covers:

- absolute joint targets;
- delta-from-current targets;
- delta-from-previous-target targets;
- normalized and physical action charts;
- physical range saturation.

The randomized migration matrix covers:

```
3 source modes
x 3 target modes
x 2 source normalization choices
x 2 target normalization choices
x 100 random states/actions
= 3600 migrations
```

and requires every in-range migration to reproduce the source controller goal
exactly.  Out-of-range cases are retained as SATURATED evidence rather than
silently declared successful after clipping.

## Evidence boundary

Supported:
- constructive exact/approximate/impossible local classification;
- minimum-norm stateful adapter synthesis;
- explicit exact-impossibility direction witness;
- finite-horizon error bound for the declared local model;
- finite-pool regional consistency and counterexample search;
- different-dimensional controller-state handshake;
- exact ManiSkill joint-position contract compiler;
- CPU-only deterministic tests.

Not yet supported:
- nonlinear continuous-region proof without an external Jacobian variation
  bound;
- automatic extraction of plant Jacobians from arbitrary simulators;
- real-robot safety claims;
- external maintainer adoption of the research method.

## Reproduce

From this branch:

```bash
python -m pip install numpy pytest
cd cst_research
python -m pytest -q test_*.py
```

## External anchor

ManiSkill issue #429 reports 0% success for one joint-delta-to-joint-position
conversion path.  A maintainer explicitly noted that fully accurate
action-space conversion is non-trivial and potentially conference-worthy.

The research claim is intentionally narrower than "all action conversion":
**controller migration should be compiled against executable closed-loop
semantics, and rejected with evidence when those semantics cannot be
preserved.**


## Independent LeRobot parity

CST's reference-ownership layer is validated against pinned public LeRobot source (`d40e8709...`). Across 500 random chunks (2,000 trajectories / 18,000 action vectors), CST reproduces LeRobot's chunk-relative absolute goals with maximum error `1.49e-7`; temporally stacked state selection matches exactly. A frozen counterexample also shows that numerically copying the same chunk into sequential-delta semantics changes the goal trace (max divergence 3.0).

This is cross-stack validation, not external adoption.


### 5. Causal deployability of action chunks

CST distinguishes a trace that can be converted after rollout from a controller migration that can be executed online. If a whole action chunk is emitted at query time but a target native action for future step t needs the future measured state or controller-owned target at t, exact conversion cannot be precomputed. CST therefore returns PRECOMPUTABLE, REQUIRES_STEP_HOOK, EXECUTABLE_WITH_STEP_HOOK, or REFUSE_MISSING_RUNTIME_STATE. The latest full public suite contains 46 passing tests.

## Bounded LeRobot -> current-state JIT migration

A pinned LeRobot source implementation is used as the source semantics. With relative offsets bounded to +/-0.2, CST migrates 2,000 random 9-step trajectories (18,000 action vectors) from CHUNK_ANCHOR semantics into CURRENT_STATE-relative actions at execution time.

- JIT max physical-goal error: `7.45e-9`
- JIT p95 per-trajectory max error: `7.45e-9`
- naive numeric-copy median per-trajectory max error: `0.555`
- naive numeric-copy p95: `0.852`
- naive numeric-copy max: `1.152`

The key point is causal: the target current-state reference for future steps does not exist when the source chunk is emitted, so exact migration must be performed at execution time rather than by copying or precomputing the whole target chunk.

Latest complete public research suite: **46 tests passed**.