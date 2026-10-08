# POST-OUTCOME diagnostic: exact 64-seed potential-outcome query-allocation distributions

**EXPLORATORY SECONDARY ANALYSIS — NOT A NEW PROSPECTIVE EXPERIMENT OR A POPULATION P-VALUE.** Exact code [`research/query_placebo_exact_allocation_analysis.py`](../query_placebo_exact_allocation_analysis.py), [completed source-locked stdlib CI 37835648927](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37835648927). Uses ONLY the eight original PhysX sample files independently SHA-archived in [`evidence/certify_query_periodic_placebo_new64_260001_270032/`](evidence/certify_query_periodic_placebo_new64_260001_270032/).

## Why full source PhysX controls enable a new counterfactual analysis

The eight-arm registered real native PhysX experiment [37833053629](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629) simulated **EVERY same task seed** with BOTH of the following actual matched control worlds:

- **No authority query:** use predeclared common bounded target action under two histories and refuse if a target goal is unrepresentable.
- **One IMMEDIATE target query at the first postfault decision:** use privileged target state and the original frozen source policy.

A third, truly **PREDECLARED** periodic-control world read an authority target iff `seed % 4 == 0`. The audited binary task outcomes of that periodic world match the appropriate **independently simulated** one-read or no-read world on **all 64/64 original states**. We can therefore calculate exact outcomes of *any hypothetical fixed seed-selection schedule* for those **two specific control strategies**. This is conditional replay from physically measured potential worlds, **not newly executed simulation and not extrapolation to learned policies**.

The 64 original task seeds contained:

| Counterfactual class | PullCube /32 | StackCube /32 | Combined /64 |
|---|---:|---:|---:|
| Reading once adds one native task completion | 3 | 16 | **19** |
| Reading once loses a completion | 0 | 0 | **0** |
| Succeeds either way | 29 | 12 | **41** |
| Fails either way | 0 | 4 | **4** |

For a schedule that makes *exactly K reads*, where the selected seed indices are uniformly sampled without replacement from all 64 registered states, the exact number of successes follows the coefficient of `z^K u^success` in:

```text
Product over 64 registered states i of
    (u^(no_read_success_i) + z * u^(mandatory_read_success_i))
```

This is computed by a fully exact **integer dynamic program** with total mass `binomial(64, K)`; no Monte Carlo, fitted model, or post-hoc success selection is needed. However **this entire secondary analysis and its success threshold were made AFTER the original outcome files existed**.

## What the completed exact enumeration shows

The actual existing evidence-triggered controller succeeded on **58/64** and made **17** authority target readbacks; the preregistered periodic placebo succeeded on **47/64**, made **16**; matched pair exclusive successes were 12 vs 1. Both are [original real PhysX outcomes](CERTIFY_QUERY_PERIODIC_PLACEBO_64_ORIGINAL_RESULTS.md), not predictions.

For uniformly choosing **17 readbacks among all 64** original registered seed indices, the exact fraction of fixed schedules that would obtain **at least 58 task completions** (using the physically measured IMMEDIATE-read vs zero-read native worlds) is `1.2396962255969624e-13`.

For a **different, retrospective schedule family** conditioned on allocating exactly the adaptive method's observed task-level read budgets (**3 Pull, 14 Stack**), the exact fraction of within-task uniformly chosen schedules reaching at least 58 total completions is `5.131888297595e-11`.

**These are NOT frequentist p-values of the adaptive algorithm**, and definitely not claims that a robot controller performs this well on a novel task distribution. They are finite-cohort combinatorial tail fractions under explicit, counterfactual uniform-query-allocation assumptions, computed after seeing the results. The original state sample, architecture family and robot are all fixed.

## A mechanistic complication that MUST NOT be hidden

The adaptive method **is not always equivalent** to immediately choosing the always-read world or the zero-read world based solely on its final query count. On **62/64** original states, that simplified binary mixture reproduces the task result. On the following **two original StackCube states**, it fails:

- **Seed 270005**: adaptive method succeeds even though the potential-outcome world chosen by its observed read/no-read count would fail.
- **Seed 270030**: same discrepancy.

The original selective method can execute several authorized bounded actions **before deciding to obtain an authoritative target read**. Therefore the state, contact and subsequent trajectory at the time of its read can differ from a mandatory *immediate* read. These are two genuine **closed-loop timing/trajectory effects**, not merely improved allocation of a fixed seed-level binary treatment. Do NOT use the above potential-outcome mixture to predict all counterfactual adaptive trajectories or identify its causal benefit on unmeasured worlds.

A next high-standard prospective study needs (i) a new precommitted cohort, (ii) random, learned and difficulty-stratified budget-matched query timing baselines, (iii) a second controller implementation and correct action chart, (iv) independently observed state/force/contact/saturation, and (v) an external laboratory/fork execution. Only then could the paper claim a general active-sensing innovation beyond a single simulated controller.

**Attribution:** the polynomial/exact enumeration is standard combinatorics and not a new theorem; the source-control instrumentation and two disclosed trajectory counterexamples are the empirical contribution. One contributor ran the original PhysX work. No official ManiSkill/ActionShift scientific adoption or hardware safety is claimed.
