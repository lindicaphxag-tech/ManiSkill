# Validity-First Target History Authority: A Calibrated Readback Contract

*Technical statement v0.1 · 2026-10-09 · pre-heldout result · not a novel probability theorem, deterministically certified dynamics model, or hardware safety guarantee*

## Why the conventional zero/hold adapter is not enough

A source-frozen robot policy emits an action, while the native controller maintains a remembered target pose. Two unacknowledged native commands generate a **finite complete target-history belief** \(H=\{h_1,\ldots,h_K\}\), with each candidate containing both target translation and target rotation. A known-delivered physically executed native zero target-delta at time \(t_4\) yields a public pre/post achieved-XYZ displacement. The observer's published scalar residual \(r_i(y)\) is the minimum public-response model error for candidate \(h_i\), under the **frozen** gain range \(\alpha\in[0,1]\).

For fixed \(0\le\epsilon<\infty\) and guard \(\gamma=0.002\mathrm{\,m}\), **authorize candidate \(i\)** only if its residual \(r_i\le\epsilon\) AND for every distinct \(j\ne i\) we have \(r_j>\epsilon+\gamma\). Otherwise query the authoritative native target getter **once** at the predeclared resynchronization time \(t_5\).

These are set-membership conditions, *not a learned prior on the physical likelihood of the hypothesis*. The full target orientation is an attribute of an identified discrete history; the XYZ measurement does **not** estimate a free, continuous orientation.

## Proposition 1 — False public authority requires true-model miscoverage

Assume **(A1)** one of the \(K\) candidates corresponds to the actual after-execution complete native target, let its index be \(h^\star\). Assume **(A2)** no hidden native target getter enters the decision; the decision is based only on the candidate residuals and fixed frozen envelope. Assume **(A3)** the algorithm accepts at most one candidate using the simultaneous winner-and-competitor margin rule above.

Then

\[
\{\mathrm{authorize}\ h_i\neq h^\star\}\subseteq\{r_{h^\star}>\epsilon\}.
\]

**Proof.** A wrong accepted candidate \(i\neq h^\star\) requires every competitor, in particular \(h^\star\), to have \(r_{h^\star}>\epsilon+\gamma>\epsilon\). Hence the true history necessarily lies outside the stated response envelope. □

This logical implication is exact **only for the native controller target and complete latent history represented by \(H\)**. It says nothing about collisions, actual executed trajectories, reaching/contact dynamics, observation calibration validity or next-step task success.

### Consequence: if an independent score calibration exchangeability assumption held

Let \(R_1,\ldots,R_n\) be **post-physical-step, private-truth-labeled true-history residuals from earlier, disjoint episodes** computed with the same frozen public response score. Suppose those \(n\) scores and one unseen future true-history score \(R_{n+1}\) are exchangeable and their joint distribution is continuous (ties can be conservatively included). Fix the decision threshold before the unseen outcome:

\[
\epsilon=\max\left(\epsilon_{\text{historical}},\ \max_{k\le n}R_k\right).
\]

Then, by rank symmetry,

\[
\Pr(R_{n+1}>\epsilon)\leq \frac1{n+1},\qquad
\Pr(\mathrm{confidently\ wrong\ native\ target})\leq\frac1{n+1}.
\]

For each of our two tasks, \(n=32\), giving **a nominal \(1/33\approx3.03\%\) marginal bound UNDER the assumptions**. This is the familiar extreme order-statistic or split-conformal rank argument, **not a novel theorem** or a high-probability certificate valid under arbitrary distribution shift. In particular, target-history completeness (A1), frozen score function, and true joint score exchangeability are empirical assumptions; errors in any one may destroy the guarantee.

### Why this is more useful than repeating an empirical probe

In [the first genuine four-joint-truth native PhysX study](frozen_policy_transfer/evidence/four_joint_truths_first_physx64_880001_890032/), all 32 PullCube true target-history residuals fell below the old \(6.944\mathrm{\,mm}\) response envelope, while **9/32 StackCube actual target residuals exceeded the old \(7.191\mathrm{\,mm}\) bound**. Two wrong confident StackCube HA authorizations occurred at original reset IDs **890005** and **890017**. Those cases provide a direct witness of \(\{r_{h^\star}>\epsilon\}\), exactly as Proposition 1 predicts. These are **DEVELOPMENT observations**, not independent confirmation.

A separate source-hash-pinned offline calibration [recomputes all 64 actual OLD training residuals](source_audit_prior_true_residual_calibration.py), fixing the next experiment's thresholds to:
- PullCube: \(\max(0.006944262561376447,\ 0.006776465613231219) = 0.006944262561376447\,\mathrm m\).
- StackCube: \(\max(0.00719087965534261,\ 0.02126739483653302) = 0.02126739483653302\,\mathrm m\).

The StackCube authority envelope is much wider, so **it may deliberately authorize fewer histories** and incur more authoritative queries. A wider threshold does not imply an improved task controller, let alone guaranteed safety. The pre-outcome research gate compares wrong authorizations, task success, public XYZ read count, and private target getter count on [64 entirely different registered reset seeds](VALIDITY_FIRST_PUBLIC_ACK_NEW64_PREOUTCOME_V1.json).

### What may falsify the risk statement in a genuinely new environment

- Model response scores can cease to be exchangeable in contact-rich phases, changed impedance/gain, latency, camera-only sensing, grasped-object inertia and different hardware.
- The actual target-history may not be in the hypothesized native set because the documented action chart, initial native target, actual acknowledgement count or input provenance was wrong.
- Even when the correct internal target is selected, the manipulator may still fail to track it, collide or fail the task. This proposition concerns **target state identification only**.
- A high private readback cost is a real limitation. In a hazard-sensitive use case, querying should be preferred unless the response model has independent evidence sufficient for the required risk standard.

## Three scientifically distinct test gates

1. **Calibration source authenticity.** 32 original prior true latent-target scores per task, byte-hash pinned; absolutely no new-seed true target labels enter the operational algorithm.
2. **Same-physics controlled comparison.** The original narrow authority and conservative calibrated authority each run their own full native PhysX policy world with the same fresh reset, two truly uncertain physical ACKs (AA/AH/HA/HH), the same physically executed known-zero motion step, and the same publicly observed XYZ samples. Readback at the same \(t_5\) step. Source auditor checks false confident target labels only using post-step native truth.
3. **Out-of-distribution external challenge.** A different controller family, contact regime or fully independent lab must run untouched source with its own new seeds and independently measured real response scores. Any evidence of model miscoverage breaks the nominal rank argument; do not silently substitute a safety claim.

Current scientific claim is **calibrated probabilistic selectivity under a declared score-exchangeability assumption**, *not* deterministic robot repair authorization, a general-purpose learned VLA, a real packet-loss benchmark, SOTA, or third-party-validated robotic deployment.
