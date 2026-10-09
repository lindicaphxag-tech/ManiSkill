# Reviewer theory appendix v4 — Identifiability, abstention, and the model-validity gap

**Purpose:** rigorous *application* of established hypothesis-testing and conformal-prediction facts to the exact unknown-execution-ACK, commanded-target controller problem. These theorems are **not claimed original mathematical discoveries**. They specify which future algorithmic improvements can and cannot be certified. Source-authenticated author-run robotics experiments remain the separate empirical contribution.

## Precise random variables, fault contract and privilege levels

- \(H\in\mathcal H\): **true complete target-pose execution history** of the last two ambiguous commands, including all associated position and orientation transitions.
- \(B\subseteq\mathcal H\): target-history candidates built **without private target reads** using an already verified native target-relative action chart. *Belief completeness*, \(H\in B\), is a separate assumption from *sensor/model validity*.
- \(Z\): the full publicly measured, physically executed neutral-probe transcript, including before/after achieved end-effector XYZ; any additional optical, velocity, force or temporal signal must be separately priced and actually measured.
- \(Q\in\{0,1\}\): authorized private target-state query. The queried target is genuinely controller-private and must never leak into a public scoring branch.
- \(\widehat H\in B\cup\{\bot\}\): decision to select one intact complete history or abstain. On abstention the adapter spends the counted authoritative read or refuses, per an explicit budget.
- \(S(Z,h)\in\mathbb R\cup\{+\infty\}\): **frozen** public-response nonconformity score for candidate history \(h\), with lower scores denoting better empirical motion fit. Score must not be fit on prospective test outcomes.

These distinctions prohibit interpreting correct task completion as proof of correct hidden-history identification.

## Proposition 1 — Public indistinguishability forces a query/abstain-error tradeoff

Fix two actually possible histories \(h_0\ne h_1\) with equal prior probability. Let their induced public transcript distributions under any *fixed allowed experiment/probe policy* be \(P_0,P_1\). Any classifier outputting \(h_0,h_1,\bot\) satisfies

\[
  \Pr(\widehat H\ne H,\;\widehat H\ne\bot)
    +\tfrac12\Pr(\widehat H=\bot)
    \ge \tfrac12\big(1-\mathrm{TV}(P_0,P_1)\big).
\]

**Proof:** Map abstention to an independent fair random guess. The resulting ordinary binary hypothesis test errs with probability exactly \(e+\tfrac12q\). Under equal priors, its minimum achievable error is \((1-\mathrm{TV}(P_0,P_1))/2\), the standard total-variation two-point testing bound. This yields the inequality. For **exactly indistinguishable** public laws, \(\mathrm{TV}=0\), hence \(e+q/2\ge1/2\). In particular, demanding zero false identification forces full abstention/query for this pair. This is a standard Le Cam argument, not a novel impossibility theorem.

**Why this matters:** If zero-motion or contact-saturated responses from distinct target histories have overlapping physical observation distributions, no clever reshaping of the same measured XYZ can make history identity perfectly observable. A second observation helps only if its *conditional* distribution differs across histories and one actually measures it; correlated repeats may not help.

## Proposition 2 — Rescaling one residual cannot create a second physical witness

Let the original motion-residual vector be \(R=(r_h)_{h\in B}\). Let a purported independent confidence vector be deterministic \(W=g(R)\); for example \(w_h=\exp[-\tfrac12(r_h/\epsilon)^2]/\sum_j\exp[-\tfrac12(r_j/\epsilon)^2]\). Then

\[
  I(H;R,W)=I(H;R).
\]

**Proof:** Because \(W\) is a deterministic function of \(R\), \(H\to R\to W\) forms a Markov chain and \(H(W\mid R)=0\); the chain rule gives \(I(H;R,W)=I(H;R)+I(H;W\mid R)=I(H;R)\). This is an ordinary information-theoretic identity, **not** evidence of additional independent sensor information.

**Implication for our real method:** The new prospective 0.65 softmax-style residual-weight filter (if it finishes running) is an **additional rejection rule on the SAME public motion evidence**, not a two-sensor, independently corroborated model trust score. A higher empirical confidence cannot independently validate a misspecified response model merely because it passes both gates. If it removes wrong admissions, the resource/risk benefit must be demonstrated on untouched trials, and the method must be called *same-evidence gating* rather than *dual independent evidence*.

## Proposition 3 — Marginal false-authorization control for a properly calibrated set

Suppose a frozen nonconformity score \(S(Z,h)\) is calibrated on \(n\) source cases with **authoritatively known true histories** using data disjoint from the test source. Let \(R_i=S(Z_i,H_i)\), \(i=1,\ldots,n\), and let \((Z_{n+1},H_{n+1})\) be exchangeable with calibration cases. For a target \(\alpha\), form

\[
k=\lceil(n+1)(1-\alpha)\rceil,\qquad
q=\begin{cases}R_{(k)},&k\le n,\\+\infty,&k>n.\end{cases}
\]
\[
 C(Z)=\{h\in B:S(Z,h)\le q\}.
\]

Authorize a history **only when \(|C(Z)|=1\)**; otherwise abstain/query. Assume the true complete history belongs to the enumerated candidate set \(B\) almost surely. Then

\[
 \Pr(\text{authorize a wrong complete history})
    \le \Pr(H\notin C(Z))\le\alpha.
\]

**Proof:** A false authorization implies the true history is absent from \(C\): the accepted set contains exactly one *different* history. The second inequality is the standard split-conformal marginal rank/exchangeability bound applied to true-history nonconformity scores. Discrete ties only make coverage more conservative with the displayed \(\le\) rule.

If the candidate set fails to contain the true history with probability at most \(\delta\), the bound becomes at most \(\alpha+\delta\) provided the conditional score-exchangeability guarantee applies on representable histories. If the response distribution shifts, exchangeability is violated, the candidate set is misspecified, calibration labels are incorrect, or the rank quantile is recalculated from test trials, the claimed guarantee need **not** hold.

**Critical sample-size consequence:** With only **32** calibration histories and desired \(\alpha<1/33\approx 0.0303\), the above conservative split-conformal quantile is \(+\infty\); when all \(B\) histories have finite nonconformity, \(C=B\). For \(|B|>1\), the conservative correct policy must query *every such ambiguous trial* rather than promise impossible low error at high public authorization. A wide enough \(q\) can also create zero singleton admissions at more moderate error levels. Better risk–resource frontiers need *new independent physical evidence, richer motion score or additional calibration*, not a false empirical certificate.

**Do not conflate bounds:** This is a **marginal** bound on \(\Pr(\mathrm{wrong\;and\;authorized})\), NOT a bound on the conditional selective error \(\Pr(\mathrm{wrong}\mid\mathrm{authorized})\) or on safety-critical impact if the rare wrong authorization occurs. Selection-conditional guarantees require extra methods/assumptions. Nor does the event bound imply task success or collision/force limits.

Established background: A. Angelopoulos & S. Bates, *Conformal Prediction: A Gentle Introduction* (Foundations and Trends in ML 2023, DOI 10.1561/2200000101); *Theoretical Foundations of Conformal Prediction* (Angelopoulos, Barber, Bates, arXiv 2411.11824, rev. 2026); classic total-variation/Le Cam two-point testing bounds; basic data-processing identity. These are cited as **prior theory**, not credited to BeliefBridge.

## Adversarial empirical connection (do not erase the counterexample)

- Matched physical prefix + identical post-t5 compiler: 64 new sources, 576 actual native worlds; 53/64 official manipulation successes in both public-history and fixed-reader treatments, 48 vs 64 private reads; **0 wrong confident among only 16 public admissions IN THAT population**.
- A disjoint 64-new-source matched-public-information 640-world true PhysX experiment: **1 confidently wrong** history on the original public method (53/64, 48 reads), whereas a Bayesian-shaped posterior comparator consumes 62 reads and completes 54/64. This directly falsifies any unqualified empirical "always safe" statement.
- Calibration-widening baseline: an independently computed wider model-coverage threshold consumed **53 vs 51** private reads but did **not** improve a distinct 64-state new-population task success or observed error (58/64 in both; zero wrong in that one cohort). This is a **negative method** result, not evidence that a conformal-style marginal bound is empirically useless.
- Two correlated motion measurements gave no task gain (48/64 both) and two more private reads under a stricter test. This rules out naive duplication of a sensing channel as automatic epistemic gain.

## Main-conference advancement gates defined before claiming an advance

1. **At least one genuine new validity signal or estimator** whose reliability is distinguishable from a deterministic transform of the same XYZ residual; real physical measurements and source identity must be logged. No new physics signal can be invented by a spreadsheet or retrospective oracle.
2. **Prospective source-frozen holdout** after calibration/development, stratified by real t2/t3 applied/held faults, two task families and previously troublesome contact/geometry cases. Report the entire intention-to-treat denominator, all absent probes, every confidently wrong decision, each query and actual native task failure.
3. **Information–cost Pareto plane:** private controller-target reads **and** public XYZ observation events, native probe actuation, wall-clock delay, and if available end-effector path length. Compare to a task-specific Bayesian style gate under *exactly equal measured public/actuation information*, plus fully transparent fixed-read and zero-read floors/ceilings. Prove source comparator ABI parity or do not claim a causal method win.
4. **Out-of-distribution model validity:** raw true-history residual coverage and false-admission by task, fault truth, contact/geometry regime and response-gain scale. At \(|B|>1\), if trust support fails, fail closed and spend a counted query; never report an untested hardware safety guarantee.
5. **External reproduction:** a real independent outside investigator forks the exact source, picks unpublished seed/reset states, runs the *original native PhysX worlds*, publishes their own raw hashes and failures, and confirms/refutes the *precommitted* claims. An author-operated source-only audit is necessary, not sufficient.
6. **VLA native action semantics:** Released SmolVLA can close the loop on LIBERO (Task 1 4/4, Task 0 1/4 exploratory), but actually loaded robosuite OSC computes position goals from achieved \`ee_pos\`, **not accumulated commanded-target memory**. Original ManiSkill target-history uncertainty cannot automatically be transferred to this new ABI.

### Bottom line

A broad "safe robot recovery" or "novel probabilistic two-sensor inference" claim is premature. What is rigorously useful now is a **target-history observability and abstention frontier**, together with explicit evidence that query efficiency can coexist with *false confident authority*. The next genuine innovation must attack the **validity of the public response model** rather than rename an existing softmax or collect repeated correlated public samples.
