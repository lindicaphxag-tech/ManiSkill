# Transfer-certifiability preflight: an executable query-budget obstruction

**Status: mathematical preflight integrated with the existing runtime adapter.**
This is not a new concentration theorem, not a newly validated policy experiment,
and not evidence of transfer-performance gains.

## Failure mode now prevented

The existing request-direction CRG algorithm builds time-uniform confidence
intervals on a bounded stochastic *mean central secant*. Its
`CONDITIONAL_SIMILAR_MEAN_RESPONSE` decision requires

\[
 \Vert \bar Z_n\Vert_2 + r(n) + L \leq \tau,
 \qquad
 r(n)=\Vert W\Vert_2 \sqrt{\frac{\log(2dn(n+1)/\alpha)}{2n}},
 \quad
 W_j=\frac{2(b_j-a_j)}{\epsilon}.
\]

Here `[a_j,b_j]` must be an independently justified hard action-coordinate
range for both policies; `epsilon` is the fixed +/- probe fraction, `L`
is an independently justified secant-to-full-response remainder,
`alpha` is the familywise error budget, and `n` is the number of
independent paired stochastic-seed blocks. Each block costs four
policy forward evaluations.

Since every possible observation has `||mean(Z)|| >= 0`, the **best
possible** confidence upper endpoint at a fixed budget `N` is

\[
 U_{\mathrm{best}}(N)=
    L + \min_{1\le n\le N} r(n).
\]

**If `U_best(N) > tau`, no policy samples — including perfectly matching
policy responses — can authorize a transfer under this certifier.**
This is an exact algebraic feasibility check of the existing certificate,
not an assumption about what the policies will do.

## New runtime choice

Call `execute_directional_probe_budget(..., transfer_only=True)`.
After its existing input/provenance/locality gates succeed, it computes
the above best-case endpoint from the frozen query budget.

- If impossible: return
  `ABSTAIN_NO_POSSIBLE_TRANSFER_CERTIFICATE`, **zero actual model
  calls**, **zero transfer authorizations**, with the algebraic cause.
- Otherwise: execute the original four-calls-per-seed policy loop
  unchanged. A possible certificate is *not* a guaranteed certificate.
- Default `transfer_only=False`: behavior is unchanged, because even
  if a positive-transfer certificate is impossible, a statistically
  **distinct** outcome (refusing a transfer) might still be useful.

No action bounds, `alpha`, budget, remainder, tolerance or policy
response values are changed, calibrated post hoc, or inferred from
test outcomes. This gate does **not** eliminate the requirement for a
credible independent curvature/remainder bound; missing proof still
rejects without sampling.

## Reproducible illustrative arithmetic, not real PushT evidence

Take two action coordinates; each policy has a hard span of 1 per
coordinate, `epsilon = 1`, `alpha = 0.1`, and `tau = 1`.
For `N=32` pairs (128 first-action forward calls), even **without
any locality remainder** the best possible time-uniform radius is
approximately **1.154**. Conditional similarity can never be
certified within this budget. With `N=64` pairs (256 calls), its
best-case radius is approximately **0.867**, which is only a
necessary possibility, not a predicted real-policy outcome.
These numbers use *illustrative* hard ranges; they are not estimates
of either policy's verified PushT controller support.

The CPU regression suite verifies this preflight against the original
`inspect_directional_samples()` radius on an exactly zero sample mean,
proves that impossible transfer-only requests spend zero callback
invocations, preserves nontransfer diagnostic mode, and rejects
untrusted action bounds and provenance.

## Next externally meaningful experiment

1. Record the **actual** controller hard action ranges, physical chart,
   policy checkpoints, and independent locality evidence before test
   outcomes. Do not use empirical observed extrema as hard bounds.
2. Freeze a new and distinct state bank, request directions, error tolerance,
   familywise alpha, total query cap and transfer-only vs diagnostic objective.
3. Publish *all* zero-query budget-impossible requests in the denominator,
   plus calls, authorized transfers, false transfers and distinct refusals.
4. Compare nonzero correct transfer coverage **at matched cost and
   decision coverage**, and evaluate actual downstream task execution
   separately from the mean first-action screen.

Do not reuse either the old 10-state DEC bank or 13-state conformal pilot
as fresh confirmatory holdout. Existing results are negative development
data. An absent or vacuous trusted locality remainder still prevents
transfer certification, even with this preflight.

**Scope:** This is a conservative optimizer of the existing mathematical
decision pathway. It does not prove robot collision safety or stochastic
single-action reliability, and cannot by itself constitute an L8/L9
research result or external upstream adoption.
