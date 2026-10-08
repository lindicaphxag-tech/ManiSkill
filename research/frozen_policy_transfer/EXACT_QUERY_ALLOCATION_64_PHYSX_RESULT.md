# When to Query: exact original PhysX 64-state counterfactual allocation audit

**Scientific status:** *retrospective conditional analysis* of already completed, preregistered and SHA-archived original native PhysX results. NOT new PhysX runs, a previously registered randomization trial, a statistical population-level p-value, an externally independently replicated experiment, a learned controller, or robot hardware safety.

## Motivation: the strongest live research signal

The [pre-outcome 64-fresh-reset-state eight-arm placebo comparison](CERTIFY_QUERY_PERIODIC_PLACEBO_64_ORIGINAL_RESULTS.md) recorded two independent frozen third-party PPO/task families (PullCube 260001–260032; StackCube 270001–270032) in official native ManiSkill PhysX. The source robot uses achieved-pose-relative actions; the destination statefully accumulates previous commanded targets after one physically held command with UNKNOWN ACK.

At the same 64 original reset states, the unchanged evidence-triggered *certify-or-query* controller completed **58/64** using **17** privileged target readbacks, while a predeclared periodic **16-of-64** one-time query schedule completed **47/64** using 16. Matched discordances were 12 adaptive-only / 1 periodic-only, two-sided exploratory unadjusted exact p=0.00341796875. The result supports the *in-cohort value of deciding when to read actual commanded target state*, but the periodic schedule is not a strong learned active-sensing baseline and the query counts are not exactly matched.

We now ask a complementary precise question without further simulator compute: **what outcomes would a uniformly random, fixed-step-3 selection of exactly 17 target-read episodes obtain, conditional on all original same-seed potential response worlds?**

## What is *actually* identified by original simulator source

All eight originally executed source JSONs are checked byte-for-byte against their publicly archived SHA-256 hashes. Crucially the \`SHA256SUMS\` manifest is itself pinned to its preexisting public Git object \`8acf77293b4b576517d4bc4c6aa576cf0efbe39e\`, so modifying an original file AND replacing the matching manifest digest together is detected.

For each of 64 task states \(i\), original genuine PhysX already physically executed both:
- \(Y_i(0)\): bounded two-history continuation WITHOUT a privileged query
- \(Y_i(1)\): exactly one authoritative target-state read at step 3, before continuing

These matched *task outcomes* are not synthesized by machine learning. The previously preregistered periodic arm also physically executed \`seed % 4 == 0\` as the decision and the **exact per-state outcome of all 64 original periodic episodes** equals \(Y_i(1)\) when it queried, and \(Y_i(0)\) otherwise. This independent actual periodic-world check supports computing outcomes for other **fixed-step-3, seed-independent query subsets under the same deterministic simulator, task state and intervention implementation**. It does not establish equivalence for other probe times, different hardware, delayed observation sources or adaptive controller trajectories.

## Exact finite-population allocation calculation

There are 64 source states, and the original experimental task response to fixed-step-3 queries has:

| Physically verified query-effect class | Number of states |
|---|---:|
| Query helps (no-query fails, query succeeds) | **19** |
| Query changes nothing | **45** |
| Query harms (no-query succeeds, query fails) | **0** |

The no-query policy completes **41** tasks. If a uniform source-state-independent fixed schedule chooses \(B=17\) distinct states from the 64 to query, its outcome is exactly

\[
S(S_{\mathrm{read}})=41+\sum_{i\in S_{\mathrm{read}}} \big(Y_i(1)-Y_i(0)\big),
\qquad |S_{\mathrm{read}}|=17.
\]

Conditioned on this specific fixed original response bank, \(X=S-41\) follows a **finite hypergeometric allocation distribution** with population 64, 19 source success-beneficial states and 17 query allocations. The expected number of completed tasks is

\[
\mathbb E[S\mid\text{original fixed outcome bank}]
=41+17\cdot19/64
=\mathbf{46.046875}.
\]

An exact dynamic program (no RNG and no Monte Carlo) counts **all** \( {64\choose17}=1{,}379{,}370{,}175{,}283{,}520\) possible schedules. The maximum possible fixed-step-3 success count with 17 reads in these data is **58**, reached only if the schedule happens to select **17 of the 19** query-beneficial states. Exactly \( {19\choose17}=171\) uniformly sampled schedules do this:

\[
\Pr_{\rm hypothetical\ uniform\ schedules}(S\ge58
  \mid\text{these fixed original paired physical outcomes})
=\frac{171}{1{,}379{,}370{,}175{,}283{,}520}
\approx1.24\times10^{-13}.
\]

This fraction is an **exact counting property of a post-outcome hypothetical allocation family**. It is **NOT** a valid preregistered significance p-value comparing the adaptive algorithm against a real randomized experimental treatment; the uniform-random design was not the original randomized treatment and no other random schedules were executed in PhysX. The apparent extremeness must not be marketed as a top-venue inferential result without prospective randomization or strong causal assumptions.

## Nontrivial falsifier: the adaptive controller is NOT a fixed-query switch

A simplistic attempt to explain the adaptive output as \`read once at step3 if chosen, else never read\` is **false on two source states**:

| PhysX StackCube reset seed | No-read arm succeeds | Fixed step-3 read arm succeeds | Adaptive eventually succeeds | Actual adaptive read step |
|---|---|---|---|---:|
| 270005 | No | No | **Yes** | **6** |
| 270030 | No | No | **Yes** | **5** |

On these two states, delaying the privileged query until the verified bounded controller can no longer authorize its action changes the real native control trajectory. The user-visible controller may already have issued earlier safe bounded actions before its eventual query. Both fixed read/no-read arms failed on the same starting physical world. An invalid binary potential-outcome splice **cannot reproduce the adaptive path**, and this is why the code explicitly lists/retains the two exceptions.

This establishes *different observed closed-loop outcomes under different query timings in the same simulated source setting*, not that read timing alone is isolated causally from all intermediate policy observations, actions or contact evolution. The correct next independent study must vary query timing with a stronger matched-action/probe budget, compare a learned or expert state-aware querying baseline, and study unseen physical fault types.

## Evidence quality and reader workflow

- Original fully executed and preregistered 64-state native PhysX run: [Actions 37833053629](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629)
- Original state-independent placebo schedule frozen in [commit ee209f6](https://github.com/lindicaphxag-tech/ManiSkill/commit/ee209f6bc80e2bb280f9b00e6a9bafc330bdc799)
- [Eight actual source JSONs and original SHA256SUMS](evidence/certify_query_periodic_placebo_new64_260001_270032/)
- [Original physical source-level auditor](../audit_certify_query_periodic_placebo64.py)
- [New exact source-locked, full-distribution standard-library counterfactual](review/exact_query_allocation64.py), plus [destructive tests](../../tests/test_exact_query_allocation64.py).

Run on stock Python (3.11 or newer, **no PyTorch, simulator, GPU, downloads or extra packages**):

\`\`\`bash
python -m unittest discover -s tests -p test_exact_query_allocation64.py -v
python -m research.frozen_policy_transfer.review.exact_query_allocation64 \
 --input-dir research/frozen_policy_transfer/evidence/certify_query_periodic_placebo_new64_260001_270032 \
 --output /tmp/exact_fixed_query_allocations.json
\`\`\`

The verifier checks all 64 true task-state/fault/official success outcomes and source hashes, verifies the *physically executed placebo branch identity on every seed*, enumerates all \({64\choose17}\) candidate fixed schedules **exactly**, and separately reports two genuine adaptive rollout differences. The result strengthens a falsifiable original mechanism story but **does not substitute** for an external independent research-lab simulation or a matched prospective strong active-sensing benchmark.
