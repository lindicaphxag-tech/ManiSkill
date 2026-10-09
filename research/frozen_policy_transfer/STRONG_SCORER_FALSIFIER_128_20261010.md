# Matched-public strong-score falsification on the 128-cell PhysX archive

**10 October 2026 — retrospective source-verified reanalysis, NOT new closed-loop physics or a preregistered new method result.**

## Why this test matters

The [first source-frozen 32-reset / 128-ACK-cell factorial](WHEN_ROBOT_ACTIONS_LEAVE_NO_TRACE_FLAGSHIP_V08.md) found 102 vs 122 private controller-target reads for a complete-history set-membership rule A versus same-public score-only 0.95 B, all three arms with identical 104/128 successful individual tasks. However, the 0.95 threshold was conservative. It can exaggerate the apparent need for A.

This new **separate code branch** reuses *all existing immutable public residual records* and mathematically recomputes a stronger 0.60 score threshold previously explored on a different development study. Every original physical cell is included; the original source auditor must pass the complete native command, source SHA256, initial-state and full-posed predecision prefix checks before the analysis runs. New posterior weights are recomputed from original residuals and epsilon (and must equal original 0.95 weights); re-running 0.95 must exactly reproduce its original *physically executed* decisions and getter count.

## Result — no method superiority over this stronger same-public rule

| Comparison | Task success actually executed | Publicly authorized full histories | Wrong confident histories | True/private getter count | Independent reset clusters with at least one admission |
|---|---:|---:|---:|---:|---:|
| A: original set-membership/read, physically executed | 104/128 | 26 | 0 | 102 real | 20 |
| B: original score 0.95/read, physically executed | 104/128 | 6 | 0 | 122 real | 6 |
| **B' score 0.60/read, offline counterfactual on fixed public observations** | **NOT evaluated** | **25 hypothetical** | **0 hypothetical** | **103 predicted (128 - 25)** | **18** |
| C: original mandatory true target getter, physically executed | 104/128 | n/a | n/a | 127 real (one early stop) | n/a |

### Paired authorization decisions on the exact same 128 physical conditions

| Both A and retrospective 0.60 B' authorize | A only | B' only | Neither |
|---:|---:|---:|---:|
| **22** | **4** | **3** | **99** |

The **four A-only** conditions are one PullCube and three StackCube, while the **three B'-only** cases are all PullCube. These are *the same public observations*, not a rerun of the downstream native controller. This heterogeneous disagreement is not captured by the 26-versus-25 totals. No observed wrong-history labels occur for either method at these particular settings, but the small sample does not justify method risk superiority.

The paired decision-table gate and all 16 physical-source shards passed in [CI run #37960058430](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37960058430) on the revised exact analysis head.

The previous **20-read** advantage against B collapses to **only one predicted request** against B' with equal public measurements. This is not a proof that A is better than B': B' was not run in a separate physically executed closed-loop trajectory, did not execute its downstream native controller commands, and its result was not registered before the original 128-cell outcome. The historical 0.60 setting was previously tuned on separate development data but is *post hoc* as applied here.

The 25 B' admissions arise from 18 separate reset IDs (PullCube 15 condition cells; StackCube 10). Zero observed incorrect B' labels is not a population safety certificate: an illustrative one-sided 95% binomial bound for at least one wrong B' admission within an authorizing independent reset is ~15.3% under the restrictive cluster-IID assumption. A's 26 admissions arise from 20 clusters with ~13.9% analogous upper bound. The numerators being zero does not demonstrate one is safer. No total-energy/time or network/hardware utility improvement is established.

## What is independently executable and what is not

- **Author-controlled first-run code validation:** [successful GitHub Actions #37959616334](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37959616334) executes **5 adversarial non-GPU tests** and the **entire physical-source audit** before recomputing the two thresholds. The artifact preserves full descriptive JSON and logs.
- **Code:** [retrospective replayer](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/posthoc-strong-score-matched128-20261010/research/replay_strong_matched_public_score128.py) and [adversarial tests](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/posthoc-strong-score-matched128-20261010/tests/test_posthoc_strong_score128.py).
- **Original source:** [first-run 128-cell immutable archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/isolated-query-factorial-128-20261009/research/frozen_policy_transfer/evidence/isolated_query_factorial128_first_3010001_3020016).
- **NOT done:** no new physics, no new randomly chosen initial states, no actual B' controller commands or task-success comparison, no official ActionShift DualABI implementation, no external laboratory replication.

To reproduce the *source-only* check from this branch's root, run:

```bash
python -m unittest discover -s tests -p test_posthoc_strong_score128.py -v
python -m research.replay_strong_matched_public_score128 \
  --output matched128_posthoc_score_audit.json
```

## Scientific decision

The complete-history A rule still illustrates hidden-controller-memory failure modes and the information-versus-authoritative-read trade-off, but it has **no convincing meaningful private-read performance edge** over this simple, previously tuned same-public threshold. Do not use the 20-read gap against original B as a method novelty claim. A main-conference effort should pivot to a **validated, genuinely nonzero action-conditioned probe** and a separately registered, physically executed same-sensor/same-actuation-budget challenger; otherwise emphasize a controller-state audit and restricted public-observability evidence, not optimizer superiority.

This negative result is deliberately preserved even though it weakens the performance story. It does not modify the frozen protocol or the original archived PhysX evidence.
