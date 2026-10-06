# Regional CST and Counterexample-Guided Adapter Synthesis

A local controller adapter can be exact at every queried state while no single
adapter is valid across the deployment region.  This matters for nonlinear
controllers and controller state: silently recomputing a different converter
at every point changes the runtime contract.

For sample i, define

```
D_i = [A_s(i) - A_t(i), B_s(i)]
```

and require one shared adapter K:

```
B_t(i) K = D_i  for all i.
```

The implementation solves the stacked system over a frozen sample set and
reports the worst relative residual.  A nonzero residual means the sampled
local demands are mutually inconsistent with one shared stateful adapter.

The counterexample-guided routine starts from one sample, scans a frozen pool,
adds the worst violating linearization, and repeats.  This turns "converter
works on my nominal state" into an explicit adversarial search over the
declared evaluation pool.

Important boundary: this is currently a **finite-pool certificate**, not a
continuous-region theorem.  A continuous region claim requires an externally
justified Jacobian-variation / Lipschitz bound or interval model.
