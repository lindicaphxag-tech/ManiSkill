# Prospective run failure and non-outcome implementation correction

**Original frozen source:** `818947883b2940d09b1ea9d1eca71e6b46ac255d`, physically executed in [GitHub Actions run 37924300007](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924300007).

**Failure from original PullCube chunk 0:** `RuntimeError: POSTQUERY_SHARED_COMPILER_STATE_MACHINE_DRIFT` in `frozen_ppo_shared_compiler_twoack_2x2_physx.py:447`, after entering the fixed reader's post-query branch. This is a *real fail-closed implementation failure*, not a completed experimental result. See [original failing native job](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924300007/job/113800022992). Do not use this run's output to claim task success or an intervention benefit.

**Causal mechanism of bug:** `maybe_two` was evaluated immediately *before* the fixed baseline's explicit t5 authoritative target resynchronization. The belief contained >=2 histories just before t5, so the cached flag remained `True` even though resync had collapsed to one exact target. This routed the fixed method through its obsolete multi-hypothesis geometry path and the new dynamic compiler-invariant guard correctly aborted.

**Smallest admissible fix, without observing outcomes:** Move `maybe_two=(name_belief and len(beliefs[n].hypotheses)>1)` *after* both public/fixed t5 information decisions, and keep original seed list, PPO weights, thresholds, official task-success measure, arm aliases and physical fault schedule unchanged. The code fix is a single execution-order correction; no numerical outcome, scored success or confident-history admission was used to choose it.

**Revision:** `89248363b5bc52c0568495f3f78efc58d9a1ac67` (Git source blob); code change commit `d5909e849ea97cde73af6bba0e3969080d3f7393`. Future reruns should pin their own frozen full commit, separately log every shard, reject mixed old/new source evidence and preserve failure records from the first original run.

**Why this matters:** A passing Python compiler/hash preflight is *not sufficient* evidence that the dynamic post-query state machine is valid. This fail-closed trace is a constructive counterexample and the rerun must separately establish correct dynamic execution across all registered cases.
