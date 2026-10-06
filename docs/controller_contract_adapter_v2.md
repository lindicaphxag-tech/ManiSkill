# Controller-Contract Adapter v2 — Migration Matrix

This note defines the compatibility surface of fork PR #12.

## Intended compatibility

The adapter targets normalized `PDEEPoseController` rotation mappings that are:

1. axis-separable;
2. non-zero gain on all three axes;
3. radially clipped to the normalized unit ball before physical scaling.

The converter measures the production controller mapping on basis actions instead of assuming a fixed sign convention.

## Migration matrix

| Controller behavior | Expected adapter behavior | Status |
| --- | --- | --- |
| historical negative rotation gain | invert measured negative gain | covered by CPU test |
| sign-preserving positive gain | invert measured positive gain | covered by CPU test |
| one-step requested rotation outside normalized unit ball | preserve >1 normalized action as the caller's retry signal; caller clips and performs residual correction | covered by CPU test |
| cross-coupled rotation mapping | fail closed | covered by CPU test |
| zero-gain rotation axis | fail closed | implementation guard |
| non-normalized controller | out of scope | existing converter precondition |
| non-`PDEEPoseController` rotation semantics | out of scope | type guard / existing structure |

## Why probing is preferable to sign hard-coding

A converter that hard-codes the historical sign becomes wrong as soon as the controller sign bug is corrected.

A converter that hard-codes the corrected sign becomes wrong on the historical controller.

The contract adapter instead asks:

> What normalized action does this concrete controller implementation map to the requested physical Euler delta?

This makes the converter robust to the specific sign migration represented by upstream #1472 without requiring a synchronized flag day.

## Saturation semantics

The controller constrains the normalized rotation vector to the unit ball.

If the exact inverse requires norm greater than one, there is no exact one-step normalized action under the current controller contract.

The adapter therefore:

1. detects this condition;
2. preserves the *unclipped* normalized action with norm greater than one;
3. exposes `saturated=True` from the private inversion helper;
4. leaves clipping and residual retries to the existing trajectory-conversion caller.

This ownership is important. The caller uses `||a_rot|| > 1` not only as a numeric clipping condition but also as a control-flow signal that additional residual-correction steps are required. Hiding that signal inside the converter can change execution semantics even when the clipped physical action is locally correct.

This is intentionally different from claiming one-step semantic equality for an infeasible target.

## Acceptance gates before upstream use

PR #12 should not replace upstream #1495 merely because unit tests pass.

Required evidence:

1. CPU controller-contract tests green;
2. direct converter→controller semantic fidelity green;
3. official-demo replay non-regressive against frozen baseline;
4. paired 100-demo audit if the 10-demo gate is not decisive;
5. only then policy-level training if still requested by maintainers.

## Claim boundary

This adapter addresses a converter/controller semantic migration problem.

It does not establish:

- learned-policy improvement;
- task-level superiority;
- physical safety;
- compatibility with arbitrary future controller nonlinearities.

If future controller semantics cease to satisfy the measured axis-separable contract, the converter is designed to fail closed rather than silently extrapolate.


## Saturation ownership regression

An earlier adapter draft radially clipped the normalized rotation inside the converter itself. That was locally reasonable but violated an existing caller contract: the replay loop interprets an out-of-range rotation action as a request to clip **and retry** the residual for up to four correction steps.

Internal clipping erased that control-flow signal and caused the caller to break after one step.

The revised adapter therefore treats the saturation flag as part of the boundary semantics:

```
requested normalized action > 1
        ↓
converter preserves out-of-range intent
        ↓
caller observes clipping condition
        ↓
caller clips + schedules residual correction
```

This is a concrete example of why semantic migration must preserve not only values, units, and frames, but also **authority over control-flow side effects**.
