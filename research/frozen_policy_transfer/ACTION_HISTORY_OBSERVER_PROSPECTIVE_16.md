# Prospective action-history observer: original 16-state closed-loop evidence

**Research experiment; not a peer-reviewed, independently reproduced or upstream-adopted result.**
Original GitHub Actions: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37819111802
Original six-arm experiment head: `c2089461a8c3853220ce82f51efed6e75f622e6e`.
Pre-outcome protocol commit: `8084b681e9eca69046894d1e831746a44741cc35`.
Precommitted cohort: PullCube 62001–62008, StackCube 72001–72008; distinct from earlier 51001–51032 and 61001–61032 research cohorts.
Source frozen third-party ActionShift weights and two SHA-256 hashes in [protocol](../ACTION_ABI_HISTORY_OBSERVER_PREDECLARED_V1.json); no training or fine tuning.

## Measured results, no omitted episodes

| Task | Original PPO | Target memory exact/refuse | Target memory bounded | Action-history observer bounded | Memory-blind bounded | Direct copy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PullCube (8 seeds) | 6/8 | 1/8 | 6/8 | **6/8** | 5/8 | 5/8 |
| StackCube (8 seeds) | 7/8 | 2/8 | 7/8 | **7/8** | 0/8 | 0/8 |
| Pooled descriptive count (not an independent n=16-policy claim) | 13/16 | 3/16 | 13/16 | 13/16 | 5/16 | 5/16 |

For **all 16** original task states the action-history observer and true-target-memory adapter have equal **binary task outcomes**; this does NOT establish physical trajectory identity, conditional safety, or universality. The observer needs the correct initial achieved EE pose and an acknowledgement for each issued action, but does not read `_target_pose` / `get_state()` during decision making. It uses a delayed `get_state()` only after a trial ends for audit.

The maximum **final target-memory reconstruction discrepancy** across this full cohort was `2.3842e-8 m` (position max component) and `6.5006e-7 rad` (relative SO(3) angle), evaluated against destination `get_state()` only at trial termination. Tolerances were preregistered at 3e-5 m and 3e-4 rad.

There were **12 observer non-exact bounded projection steps** (PullCube 5, StackCube 7). Do NOT call all transported actions exact. The strict refusal baseline was much less task capable on this cohort, but refusals are not task successes. These 16 seeds are a small new sample; no performance improvement over live-target access is claimed.

## Per-seed original CI log extraction

1 = at least one genuine official `info["success"]` within up to 50 simulation steps; 0 = not achieved. All arms are paired by the same task/seed. Values are transcribed from original `FROZEN_TARGET_MEMORY_EPISODE` lines, which remain accessible in the run. This table **is derived from the logs**, NOT an assertion that its Markdown bytes match the original downloaded JSON artifact.

| Seed | Source | Live bounded | Observer bounded | Blind bounded | Exact/refuse | Naive | Observer NOT_EXACT steps | Target position max error (m) | Target rotation error (rad) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 62001 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 2.38e-8 | 1.26e-8 |
| 62002 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 7.45e-9 | 8.14e-9 |
| 62003 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 4.47e-9 | 1.44e-8 |
| 62004 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1.49e-9 | 9.13e-9 |
| 62005 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 3.35e-9 | 1.29e-8 |
| 62006 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 3.73e-9 | 1.37e-8 |
| 62007 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.38e-8 | 4.91e-8 |
| 62008 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2.38e-8 | 8.00e-9 |
| 72001 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 6.71e-9 | 2.09e-7 |
| 72002 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 5.96e-9 | 2.87e-7 |
| 72003 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1.49e-9 | 5.89e-7 |
| 72004 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 9.69e-9 | 1.80e-7 |
| 72005 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1.19e-8 | 2.95e-7 |
| 72006 | 1 | 1 | 1 | 0 | 0 | 0 | 2 | 6.71e-9 | 1.22e-7 |
| 72007 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 1.30e-9 | 1.58e-7 |
| 72008 | 1 | 1 | 1 | 0 | 0 | 0 | 2 | 2.38e-8 | 6.50e-7 |

## Authentic original files (time-limited GitHub Actions artifacts)

- original-observer-stack_cube-eight-task-states: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37819111802/artifacts/11568467888
- original-observer-pull_cube-eight-task-states: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37819111802/artifacts/11567979000

The original artifacts contain unmodified full JSON outcomes, the console logs and runner-installed Python package freeze; this derived public Markdown report is **not** an independent simulator rerun or a byte-for-byte preservation of those original JSON files.

**Completed CI:** pure CPU action-history observer adversarial contract tests passed on Python 3.10, 3.12 and 3.13, and both true PhysX CPU eight-state frozen PPO jobs completed successfully in the original run. Do not claim GitHub Actions success means independent external scientific acceptance.

## Falsification and adoption gates still missing

1. New target-controller **implementation maintained independently** of ManiSkill, with hidden/changed memory semantics and verified action delivery acknowledgements.
2. Accurate achieved-trajectory divergence, controller saturation and contact metrics, not just the final commanded target and official task flag.
3. Trials with missed/delayed/unknown command execution. The current observer deliberately rejects ambiguous delivery rather than silently continuing; this does not solve lost-action recovery.
4. Repetition on independent machines/runner states with fully frozen runtime dependencies and fresh preregistered seeds, treating earlier cross-run #10014 divergence as an unresolved phenomenon.
5. Direct comparison to strong learned or state-estimation baseline given exactly the same observation/action access and an explicit online compute budget.

**Interpretation:** for these two task/checkpoint families, documented stateful controller recurrence can be reconstructed from action history to sufficient fidelity to reproduce the success outcomes of privileged target-memory conversion in one original multi-arm simulator run. No first-ever robot adapter, controller-general transport or top-venue acceptance is asserted.
