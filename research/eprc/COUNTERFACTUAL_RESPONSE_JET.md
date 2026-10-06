# Counterfactual local response jet gate

A real VQ-BeT / PushT witness showed an important failure mode:

- repeated DEC probes were deterministic;
- fine/coarse finite-difference maps disagreed;
- shrinking the probe did not make the first-order map converge.

A plain Hessian extension is not the right explanation for centered-derivative
scale drift: even-order terms cancel in the symmetric derivative.

For a smooth response along one physical probe direction,

    D(h) = [f(+h)-f(-h)]/(2h)
         = J0 + C h^2 + O(h^4),

where C is the directional third-order coefficient divided by six.

## Fail-closed model-order upgrade

The capsule fits J0 and C using only coarse and fine scales, then predicts a
strictly finer scale that was not used in the fit.

The richer local model is authorized only if the held-out finer-scale result:

1. reduces scale-prediction error by at least 2x
   (`improvement_ratio <= 0.5`); and
2. has relative operator error <= 0.25.

Otherwise the runtime retains:

    REJECT_FIRST_ORDER_LOCAL_MODEL

and does **not** silently replace it with a higher-order repair rule.

## Novelty boundary

Taylor jets, Richardson extrapolation, and polynomial model-order tests are
standard mathematics. They are not claimed as new.

The research question is whether a frozen robot policy can use
counterfactual, request-local experiments to choose the *minimum justified local
model order* before runtime repair, while refusing to escalate when the richer
model fails an out-of-fit physical prediction.

## Evidence discipline

The already-observed seed-17 VQ-BeT witness may be used only as retrospective
mechanism analysis for this new jet diagnostic.

A publishable model-order claim requires a newly frozen, disjoint state set
whose finer-scale responses are not inspected before the gate and thresholds
are fixed.
