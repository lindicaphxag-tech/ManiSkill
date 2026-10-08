# Request-direction sequential policy probes (candidate mechanism)

**Status: algorithm implemented and synthetically tested, NOT validated on
fresh held-out Diffusion/VQ-BeT states and NOT an external adoption.**

## Why this is a different mechanism

Both completed, frozen cross-policy studies were **negative**:

- [20-pair global DEC-distance bank](evidence/pusht_cross_policy_20case_v2/):
  DEC Spearman 0.145, below 0.50 and below the raw Jacobian baseline.
- [13-state conformal pilot](evidence/conformal_fresh_13state_v1/):
  **0/8 actual authorized transfers, at 702 policy queries**.
  Diffusion failed its original stochastic-Jacobian stability proxy in
  13/13 states. The nine-state conformal error radius 2.404 exceeded the
  fixed response tolerance 1.0 even when the validity flag is disregarded.

The earlier probe *estimates full three-dimensional Jacobians* with central
differences across three seeds and then ranks global signatures. But an
actual transfer question is about **one physical request direction h**,
not all possible action directions.

This candidate probes the **directional central secant** using *four*
policy forward calls per RNG seed:

    Z(seed) = [A(s+eps h,seed)-A(s-eps h,seed)
               -B(s+eps h,seed)+B(s-eps h,seed)] / (2 eps).

The same seed is used within one policy's +/- pair to reduce random noise.
Seeds must be independent across rounds for the statistical guarantee.
This consumes 4n calls for n rounds rather than a full 3D Jacobian +
heldout responses. **Do not compare query costs across different numbers
of physical requests or pretend that plus/minus observations at the
actual heldout point would be an independent test.**

The *actual full-h response* remains unobserved during screening. A future
study must reveal it **only after** the decision and count it in the
prospective trial denominator.

## Statistically sound, deliberately restrictive stopping rule

For each physical command coordinate j, require an independently justified,
**precommitted** support range for each policy's command, with widths S_Aj
and S_Bj. Its paired secant has coordinate range width:

    W_j = (S_Aj + S_Bj) / eps.

Under identical physical charts, IID paired random-seed draws, frozen
policy checkpoints and bounded outputs, a union-bound time-uniform
Hoeffding radius at sample count n is:

    t_j(n) = W_j * sqrt(log(2*d*n*(n+1)/alpha)/(2*n)).

Because sum_{n>=1} [1/(n(n+1))] = 1, all coordinates and every n are
simultaneously covered with probability >= 1-alpha. Therefore the mean
directional central-sec ant norm lies in
[max(0, ||mean(Z)||-||t||), ||mean(Z)||+||t||].

**This theorem is standard Hoeffding plus a union bound, NOT new mathematics.**
The novel experimental *candidate* is the embodied-policy
request-direction probe plan and runtime acquisition/abstention design;
a real policy study is still needed to show that it works.

The full-h policy mean response is **NOT** the same as a central secant
if the frozen policy is nonlinear. To use the interval for an unseen
full-h request, also require an *independently validated*
secant-to-full-request nonlinearity/remainder envelope `ell(h)`.
It is not valid to set it to zero merely because the original DEC
Jacobian estimate was unstable. The decision interval expands by ell(h).

A transfer is only **conditionally statistically similar** when the
entire upper interval <= a caller-frozen response tolerance tau.
**Conditionally distinct** means refuse transfer, NOT authorize an action.
If neither statement is supported within a fixed query budget, **abstain**.
If bounds, chart identity, IID seeds or locality remainder are not
externally justified, **REJECT_UNTRUSTED_BOUND**.

### What can go wrong (intentionally not hidden)

- **Known physical action bounds may be wide:** rigorous Hoeffding intervals
  can remain vacuous at 16 or even 128 seed pairs. The pilot must call this
  zero useful coverage and not lower the bound post hoc.
- **Randomness is not a deterministic guarantee:** this is a confidence
  statement about *mean paired policy responses*, never individual
  stochastic action safety or collision-free robot execution.
- **Distribution shift / correlated seeds:** the IID confidence proof
  fails. Torch pseudo-seeds being distinct strings is not scientific proof
  of independent stochastic policy trials.
- **Counterfactual state rendering:** this method requires an external
  observation oracle for s+eps h and s-eps h. PushT supports this in the
  simulator, but live hardware normally cannot query the counterfactual
  camera observation without a validated world model. Do not present a
  simulator-only probe as deployable without one.
- **Output saturation / unknown action range:** no silent clipping is
  permitted. An observed command outside the trusted action envelope
  invalidates the certificate. Seeing all n samples inside a bound
  does not itself prove the population bound.

## Next prospective *engineering* gate

Predeclare untouched state seeds and randomized seeds, exact official
checkpoints, eps, n_max, static controller action ranges, tau, the
curvature/remainder protocol, and a rule for missing/invalid states
**before measuring outcomes**. Evaluate (i) nonzero genuine transferred
requests, (ii) false transfer authorizations, (iii) abstentions, (iv)
probe calls at matched real transfer coverage and (v) sensitivity
to independently measured nonlinearity. The prior 23 states of the
completed two studies are **development data, not fresh confirmation**.

This is a mechanism for targeted **information acquisition** and
potential query reduction, not a standalone proof of real-world safe
policy transfer or a top-conference research success.

## Usage

    python -m pip install numpy pytest
    python -m pytest -q tests/test_crg_directional_anytime_probes.py

`paired_directional_secant` validates four physical policy outputs.
`inspect_directional_samples` computes the confidence ball and one of:
CONDITIONAL_SIMILAR_MEAN_RESPONSE, CONDITIONAL_DISTINCT_MEAN_RESPONSE,
CONTINUE_PROBING, ABSTAIN_QUERY_BUDGET or REJECT_UNTRUSTED_BOUND.
