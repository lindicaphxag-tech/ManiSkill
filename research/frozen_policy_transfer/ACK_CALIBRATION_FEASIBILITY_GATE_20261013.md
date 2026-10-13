# Calibration-feasibility lower bound for binary ACK decisions

**2026-10-13 — Prospective design gate, NOT a new robot result or a new probability theorem.**

The [native Panda/xArm6 experiment](ACK_ACTIVE_NATIVE_48_PHYSX_FROZEN_NEGATIVE_RESULT_20261013.md) used **four independent reset clusters per robot**, both actual execution-history truths and three native probes. These observations are an original *negative fixed-probe response-gap pilot*. They are **not** independent calibration of the new active-readback decision policy, and 48 physical worlds are **not 48 independent reset clusters**.

## Exact best-case sampling constraint for the current method

We consider only the following *conditional* idealized binary setting:

- A fixed prospective family of **K** probes, frozen public binary signal thresholds and **two** true histories HELD/APPLIED.
- Exactly **n distinct IID reset clusters for each true ACK history** for every fixed candidate. Paired reuse of the same seed across probes/truths does not increase n.
- Known balanced prior `P(held)=P(applied)=1/2`, symmetric unit false-history costs, perfect observed separation (all HELD signals zero, all APPLIED signals one) and no new distribution shift.
- The **existing** two-sided Clopper–Pearson + Bonferroni calibration procedure with total family miscoverage `delta` allocated to the `2K` history-action binomial marginals.

The marginal interval level is `alpha=delta/(2K)`. At perfect observations, its opposite-class tail uncertainty is

`e_n = 1 - (alpha/2)^(1/n) = 1 - (delta/(4K))^(1/n)`.

For the frozen deterministic binary decoder in this symmetric toy model, the best *certifiable* worst-case classification risk under these intervals is

`R_best(n) = min(1/2, e_n)`.

A desired error cap `0 < r < 1/2` is therefore **impossible for this CP/Bonferroni certificate** even with perfect data unless

`n >= ceil(log(delta/(4K)) / log(1-r))`

per true history and per action, with exact boundary verification in code. This is a **necessary feasibility bound for this specific confidence procedure**, not a universal information-theoretic lower bound, a sufficiency guarantee or evidence of a physical risk limit. Other valid estimators/models may yield different sample requirements.

At `delta=0.05, r=0.05`:

| Frozen probes K | Required IID reset clusters n per ACK history | Best-case error certificate at n=4 |
|---:|---:|---:|
| 1 | 86 | 0.5 (chance-level) |
| 3 | **107** | 0.5 (chance-level) |
| 8 | 126 | 0.5 (chance-level) |

With **K=3**, n=8 (already invalid to naïvely pool unlike robot bodies without a common IID population) achieves a best-case bound of only **0.4959500282**. The actual pilot has n=4 **per robot**, and its observed separation was *not perfect*. Consequently the pilot cannot legitimately underwrite a low-risk active-ACK certificate under this procedure.

Even the most favorable three-probe follow-up would require 107 genuinely independently sampled reset clusters per robot domain for the symmetric 5% certificate, with two ACK truths and three action conditions per reset: **642 physically stepped worlds per robot** if every registered action-truth combination is collected. This counts physically executed conditions, not 642 independent reset clusters. Separate test cohorts, actual actuation/sensing costs, calibration independence, readback authority and full task-success comparisons are additional mandatory requirements.

## Implementation and tests

- `research/ack_finite_sample_signal_calibration.py`: `optimistic_perfect_signal_binary_ack_risk()` and `minimum_resets_per_truth_for_optimistic_ack_risk()`.
- `tests/test_ack_finite_sample_signal_calibration.py`: independent exact beta-quantile intervals, existing robust binary minimax decoder comparison, boundary counts over multiple K/r combinations and fail-closed invalid input tests.
- The existing ACK six-environment CPU CI workflow includes this test module; verify the **new head's CI** before claiming completion.

**Decision gate:** If the prospective n and independent physical calibration cannot be supplied, the scientifically defensible action is **READBACK / ABSTAIN or a rigorously labelled exploratory negative study**; it is not valid to convert a fingerprint, a passed unit test, or high training accuracy into a physical confidence certificate. This diagnostic strengthens experiment design only. It has not produced a new positive PhysX result or a verified external upstream merge.
