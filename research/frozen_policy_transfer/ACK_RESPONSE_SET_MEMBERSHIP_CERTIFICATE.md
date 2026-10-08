# When an achieved-pose probe may actually identify a lost ACK

**Conditional, model-level set-membership certificate — not a new universal theorem, accepted paper, real-robot method or PhysX success result.**

## Why the naive nearest-target guess is scientifically weak

The current [preregistered 32-condition real PhysX probe study](https://github.com/lindicaphxag-tech/ManiSkill/pull/81) tests a simple nearest-hidden-commanded-target rule after one zero native-delta arm probe. The nearest target need not be the true history: actuator inertia, controller tracking rate, saturation, contact or grasp dynamics may make a physically correct achieved pose closer to the WRONG historic setpoint. Setting an arbitrary 2 mm margin cannot prove the label correct.

The existing [new 64-state holdout of bounded-or-query recovery](https://github.com/lindicaphxag-tech/ManiSkill/pull/80) validates a different mechanism: trusted privileged readback is sometimes useful, but can be costly. It does **not** establish that public achieved pose alone reveals target history. The current experiment asks exactly which public motion evidence could make readback unnecessary.

## Physically constrained response model and decision

Let the physically observed end-effector XYZ immediately before the probe be `x`, and after one confirmed *native zero-delta target* step be `y`. Two candidate hidden commanded-target histories predicted **from the same pre-fault acknowledged action history** are `M_applied` and `M_held`. Assume that an **independently calibrated** controller-and-scene contract establishes the following effective one-step response:

```text
y = x + alpha * (M_actual - x) + e
alpha in [alpha_min, alpha_max],   0 <= alpha_min <= alpha_max <= 1
||e||_2 <= eps,                   eps independently bounds all sensor/model errors
```

Here `M_actual` is one of the two candidates, and `e` includes model mismatch, not just sensor noise. **No implementation can infer that this response law or its residual bound is valid merely from its own predicted pose.** The contract is invalidated by unbounded acceleration, contact or unknown gain, unsupported frame, or unverified probe application. In those conditions, do not dispatch a follow-up action based on this certificate.

For each hypothesis `h`, compute the minimum Euclidean distance from the public `y` to the line segment swept by its admissible alpha interval:

```text
d_h = min_{alpha in [alpha_min,alpha_max]}
        ||y - x - alpha * (M_h - x)||_2
alpha_hat = clip(((y-x) dot (M_h-x)) / ||M_h-x||^2,
                  alpha_min, alpha_max)
```

The zero-length-segment case is handled independently. `h` is compatible only if `d_h <= eps + numeric_guard`. If exactly one history is compatible, label it; if both remain, **ABSTAIN_OVERLAP**; if neither remains, **REFUSE_MODEL_FALSIFIED**. If the response contract or zero command delivery are not independently attested, **REFUSE_UNATTESTED_DYNAMICS**. The returned distance from the incompatible model's envelope is a geometrical identification margin, **not** a probability of safety.

### Elementary soundness claim, conditional on an attested envelope

If the *real* response obeys the declared model, then for the true history there exists an `alpha` in the interval and an `e` with norm <= `eps`. Its distance to the corresponding predicted response segment is therefore <= `eps`, so the true history cannot be excluded by the test (apart from finite precision, handled by the positive numeric guard). An *authorized* unique-history decision cannot then label the wrong history. If the model is wrong, the theorem says nothing; a wrong or untrusted error bound can produce **confidently incorrect** labels.

This is elementary classical set-membership identification, **not a new mathematical theorem**. Our research hypothesis is whether it can be integrated with real command-history ACK uncertainty and a frozen policy such that **attested geometry produces meaningful task benefit at a lower readback cost** compared with equal-probe, equal-information alternatives.

### Structural inability to distinguish

If the two predicted physical-response segments, each dilated by its maximum error ball, intersect, **some possible public measurements are consistent with both** histories. No deterministic achieved-XYZ-only classifier can guarantee the correct ACK history on all measurements in that intersection. Making the target states more distinct is insufficient if the plant's alpha interval includes 0: the pre-probe pose `x` may be feasible under both.

A useful response-identification experiment must therefore **measure and separately report**:
- coverage of uniquely identifiable probes;
- fraction of wrong authorizations on all attempts (including classifier abstentions as abstentions, not failures);
- genuine fault/probe exposure;
- the externally established response envelope and its holdout calibration;
- official task success, additional probe time, inexact action projections and trusted goal-state query count.

## What has been implemented and tested

- [Source implementation](../ack_probe_set_membership.py) is standard-library only; no private controller targets, learned model, or Python simulator dependencies.
- [Adversarial unit suite](../../tests/test_ack_probe_set_membership.py) checks applied/held, overlap, invalid dynamics provenance, model falsification, alpha endpoints, no-motion ambiguity and a deterministic **1,200 synthetic** in-envelope sampling challenge. Synthetic tests **cannot** establish that ManiSkill physically obeys this envelope.
- Independent continuous integration on Python 3.11 and 3.13 verifies source syntax and contract tests. **No special alpha/noise interval has been empirically calibrated for the target controller; native PhysX task success of THIS certificate has not been measured.**

## Minimum hard gate before integration into an L8/L9-style study

1. Predeclare an independent physics calibration cohort to bound `alpha_min, alpha_max, eps` without seeing any future fault-truth labels. Capture contact and actuator limitations; permit an explicit `MODEL_UNSUPPORTED` rate rather than inventing a convenient low noise bound.
2. Freeze the calibration and run fresh disjoint task/fault states, matched one-step probe budgets. Compare this set-membership rule against nearest-goal heuristic, optimistic, pessimistic, a learned observation-to-ACK classifier and single trusted readback.
3. Count **wrong confident authorization** separately from task failure, refusal/coverage and reaction time. No interpolation or retuning after results.
4. Repeat on a **different independently maintained controller and robot**. Third-party task reproduction and a real external upstream maintainer review are still missing.

This research must not be described as a proven general method for robot action delivery, physical safety, VLA policy transfer or arbitrary contact-rich dynamics.
