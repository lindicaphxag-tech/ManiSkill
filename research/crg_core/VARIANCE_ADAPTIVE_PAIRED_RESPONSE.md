# CRG: bounded, variance-adaptive sequential policy-response evidence

**Implementation status:** candidate with synthetic CPU regressions. It has NOT
been validated against new real Diffusion/VQ-BeT trajectories or deployment
safety. Preserve the two already published negative studies unchanged.

## Why this mechanism

The original CRG directional probe uses an any-time Hoeffding confidence
ball sized by independently verified **hard controller output ranges**,
not observed stochastic variance. In such a design even *identical*
policy responses can be unverifiable at a fixed query budget.

Now `execute_directional_probe_budget(..., confidence_method="empirical_bernstein")`
can instead use an empirical-Bernstein confidence sequence for the
**matched-seed, four-query-per-round central secant**. The legacy
`confidence_method="hoeffding"` is still the default and unchanged.

For each coordinate `j` at independent seed pair `i`:

```
Z_ij = (A(+eps*h, seed_i) - A(-eps*h, seed_i)
        - B(+eps*h, seed_i) + B(-eps*h, seed_i))/(2*eps)
W_j  = (range_Aj + range_Bj)/eps   (precommitted hard support width)
```

Within each policy the matched `+/-` seed can cancel *shared*
stochastic terms. Independence is required **between** the complete
paired-seed blocks, not between dependent +/- calls.

We apply the **established** Maurer--Pontil (2009) empirical-Bernstein
inequality to each coordinate and both signs at every `n>=2`.
With `delta_(j,sign,n) = alpha/(2*d*n*(n+1))`, the union bound over
coordinates, tails and optional stopping is at most `alpha`.
The coordinatewise radius is

```
b_j(n) = sqrt(2 * unbiased_sample_variance_j * log(4*d*n*(n+1)/alpha)/n)
       + 7 * W_j * log(4*d*n*(n+1)/alpha)/(3*(n-1))
r(n)   = || b(n) ||_2.
```

For the stochastic **mean first-action** central secant gap, the same
geometric decision as the earlier CRG certifier is used:

```
upper = ||mean(Z)||_2 + r(n) + independently_trusted_locality_remainder
lower = max(0, ||mean(Z)||_2 - r(n) - locality_remainder)
upper <= tau -> CONDITIONAL_MEAN_TRANSFER
lower >  tau -> DO_NOT_TRANSFER_DISTINCT (NO transfer)
otherwise    -> CONTINUE or ABSTAIN at frozen budget
```

This is **not an original statistical theorem**. Primary sources:
- [Maurer & Pontil, Empirical Bernstein Bounds and Sample Variance Penalization](https://arxiv.org/abs/0907.3740)
- [Howard et al., Time-uniform confidence sequences](https://arxiv.org/abs/1810.08240)
- [Waudby-Smith & Ramdas, Estimating means of bounded variables by betting](https://academic.oup.com/jrsssb/article/86/1/1/7043257)

The submitted implementation uses the simple classical union approach,
*not* the latter two papers' improved betting confidence sequences.

## Honest algorithmic limitations

1. The hard controller action bounds must be **a priori, globally valid
   across all possible policy randomness**, and independently supported.
   Replacing them with observed minima/maxima would destroy coverage.
2. Each pair of stochastic seeds must be independent and identically
   distributed across rounds, and paired +/- inputs must share the same
   immutable physical chart and frozen stochastic policy.
3. The time-uniform confidence set covers the stochastic **mean secant**.
   A **separately justified** secant-to-full-request curvature/remainder
   bound is still needed before permission to transfer.
4. A mean-action authorization does not imply collision safety,
   rollout-level equivalence or policy task success.
5. Non-transfer DISTINCT decisions are NOT counted as successful transfer
   authorizations. Abstention counts remain in the denominator.

## Exact preflight

The additive width term cannot vanish even when sample variance is zero.
Before making policy calls, optional `transfer_only=True` checks whether

```
min_{2<=n<=max_pairs} ||7*W*log(4*d*n*(n+1)/alpha)/(3*(n-1))||_2
+ locality_remainder > tau.
```

If so, this specific empirical-Bernstein certificate can never authorize
transfer under the frozen budget; it returns
`ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE` with **zero calls**.
The default diagnostic mode still probes because DISTINCT may be useful.
This preflight never changes or weakens the statistical thresholds.

## Reproducibility and next disconfirming trial

The new test file
`tests/test_crg_variance_adaptive_paired_response.py`
checks exactly-zero paired variance, comparison with unchanged Hoeffding,
n=1 no-fake-variance, random high-variance abstention, physical-proof
gates, support violations, zero-query impossibility, and the fixed
budget. Everything is synthetic. Tests being green do NOT establish
an embodied-policy performance benefit.

For a genuinely independent future trial, **before running anything**
freeze new unseen restored state IDs (not any exposed 10+13),
checkpoint/runtime SHAs, both physical perturbations and groupings,
hard controller action ranges, locality evidence, error tolerance,
alpha, query budget, and baselines. The primary results should be:

- number of correctly authorized **actual transfers** (must be nonzero);
- false transfer authorizations, and false DISTINCT refusals separately;
- decision coverage / transfer coverage at matched budget and error;
- **actual** policy-call cost including zero-query preflight refusals;
- full physical **rollout outcomes**, separately from first-action means.

Never treat sample average stability or a source-code unit test as proof
of physical safety. A fully negative result remains publishable evidence
but cannot be advertised as new superiority or L8/L9 achievement.
