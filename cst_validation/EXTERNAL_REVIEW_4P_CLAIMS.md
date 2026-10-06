# Controller-Semantic Transport (CST)

## Four-page external-review claim package

**Working title:** Controller-Semantic Transport: Certifying When Robot
Action-Space Conversion Preserves What a Controller Actually Executes

**Status:** research prototype with green algebraic / trace-semantic CI.
Simulator task-level equivalence and external upstream adoption are not yet
claimed.

## 1. Problem

Robot-learning datasets and policies routinely move between action interfaces:
absolute joint targets, current-relative joint deltas, target-relative deltas,
joint velocity, and task-space actions. Existing conversion code often treats
these as vector representations. That can be wrong even when dimensions match.

A controller is stateful. For native action u, measured state x and controller
memory z, one control period produces more than an endpoint goal:

    (drive-target trace, endpoint goal, next controller reference)
        = F(x, z, u).

Two converted actions can therefore reach the same nominal endpoint while
issuing different low-level targets over the simulation substeps, or while
leaving different controller state for the next action.

The motivating public defect is ManiSkill issue #429, which reports 0% success
for pd_joint_delta_pos -> pd_joint_pos trajectory conversion. On the current
code path, an unbatched NumPy trajectory action is forwarded into a torch-only
runtime scaling helper. A separate minimal upstream patch is kept outside this
research branch.

## 2. Core distinction

CST separates three claims:

1. **Goal equivalence**: one converted action has the same canonical endpoint.
2. **Trace equivalence**: every low-level drive target within the control period
   is identical in the shared controller-command semantics.
3. **Compositional equivalence**: trace equivalence also preserves the
   controller-owned next reference needed by later actions.

The central negative example is simple but structural. An interpolating
joint-position controller and a hold-style joint-position controller can share
the same endpoint target q* while issuing different substep targets. Endpoint
matching alone is therefore not a certificate of controller-semantic
conversion.

## 3. Stateful Trace IR

For one affine controller region CST compiles

    trace  = T_u u + T_x x + T_z z + t
    goal   = G_u u + G_x x + G_z z + g
    z_next = H_u u + H_x x + H_z z + h.

The implementation currently has an exact constructor for the
PD-joint-position family with:

- absolute targets;
- current-relative deltas;
- target-relative deltas;
- normalized or physical native actions;
- interpolation on/off;
- finite native action bounds.

The certificate never claims plant/contact or task-success equivalence. It
certifies controller-command semantics only.

## 4. Action-level bounded compiler

For a concrete source action CST solves a bounded target semantic transport and
returns exactly one of:

- EXACT_TRACE;
- GOAL_ONLY;
- BOUNDED_APPROXIMATION;
- UNREPRESENTABLE.

The result reports trace residual, maximum per-substep target mismatch,
endpoint-goal residual, next-reference residual, target rank/nullity, and native
bound margin.

## 5. Whole-action-box compiler

For fixed source/target controller context, stack the complete semantic maps:

    M_s u_s + c_s = M_t u_t + c_t.

CST compiles an analytic morphism

    u_t = P u_s + q,

with

    P = M_t^+ M_s
    q = M_t^+ (c_s - c_t).

This produces two stronger certificates without sampling.

### Semantic identity

CST directly verifies

    M_t P = M_s
    M_t q + c_t = c_s.

If these identities fail beyond numerical tolerance, no affine exact morphism
is claimed.

### Whole-box boundedness

For source native box [l_s, h_s], CST propagates exact coordinate-wise bounds
of P u + q using coefficient signs. It therefore proves whether **every**
admissible source action maps inside target native bounds.

After compilation, an exact accepted transport is a matrix multiply; no online
optimizer is needed.

## 6. Current evidence

All of the following are CI-backed on the research branch:

- bounded affine Controller Semantic IR;
- semantic-morphism classifier using rank, image inclusion and nullspaces;
- stateful trace semantics;
- an analytic GOAL_ONLY counterexample: same endpoint, maximum substep drive
  target mismatch = 0.075;
- 200 randomized exact-family trace tests;
- whole-action-box affine morphism compilation;
- 500 random actions checked against one compiled identity without a runtime
  solver;
- structural rejection of interpolation-mismatched controller families;
- rejection when an algebraically exact morphism leaves target native bounds.

The most recent integrated CST workflow is green.

## 7. Claim boundary

CST does **not** currently establish:

- identical physical robot trajectories under contact;
- identical torque/force traces unless those quantities are explicitly part of
  the compiled semantic observable;
- task-success preservation;
- exact transport for arbitrary nonlinear controllers;
- cross-robot or cross-embodiment equivalence;
- maintained external adoption.

Those require separate evidence.

## 8. External validation ladder

The promotion order is frozen:

1. public issue base-fail / patch-pass;
2. clean upstream patch with no research code in its diff;
3. exact simulator-state comparison of source and converted controller command
   traces;
4. at least one nontrivial GOAL_ONLY case where endpoint matching would
   incorrectly overclaim equivalence;
5. second independent software stack (robomimic #270 is a maintainer-welcomed
   absolute/delta conversion opportunity);
6. maintainer-retained upstream adoption;
7. external double-blind review;
8. broader nonlinear / task-space extension.

A failed rung remains public evidence; thresholds or semantics are versioned
rather than silently retuned.

## 9. Research question for external review

> Can robot action-space conversion be treated as a semantic compilation
> problem, where the compiler proves whether a source controller command has an
> exact, goal-only, bounded-approximate, or unrepresentable target-controller
> realization before converted data or policy actions are executed?

## 10. Immediate 4-page experiment table

| Experiment | Question | Current status |
|---|---|---|
| ManiSkill #429 CPU regression | Is there a real public conversion defect? | base-fail / fix-pass harness available |
| Exact delta-current -> absolute | Can CST prove full trace equivalence? | supported in affine PD-joint family |
| Interpolate -> hold | Can endpoint equality hide command mismatch? | supported; GOAL_ONLY counterexample |
| Full source action box | Can one certificate replace action-by-action sampling? | supported analytically |
| Native-bound failure | Can CST refuse algebraically valid but operationally impossible mappings? | supported |
| Exact simulator trace | Do compiled semantics match host controller implementation? | pending |
| Second stack | Is the abstraction not ManiSkill-specific? | pending |
| Task-level replay | Does certified conversion preserve success empirically? | pending |

## Reproducibility

Research code lives under `cst_validation/`. The upstream bugfix branch is
kept separate so maintainers can review a minimal production patch without
research infrastructure.
