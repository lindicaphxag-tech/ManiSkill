# Seed 10014 failure is not a stable across-run outcome

## Evidence hierarchy and why this update matters

The **original preregistered 32-seed experiment remains frozen and published
unchanged**:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505

- Seed `10014` there: source succeeds at step 31; compiled frozen PPO
  does *not* succeed within 50 steps.
- The 32-case frozen tally is therefore exactly **32/32 source,
  31/32 compiled, 0/32 raw-copy** in *that original run*.

An instrumented **separate** diagnostic reproducing that seed:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717458927

- The same nominal integer seed resulted in source success at step **19**
  and compiled success at step **25**. So the previously observed
  `10014` migration failure did NOT reappear in that different run.
- Per-step source/compiled pre-action observation differences start
  near zero, but the first serious divergence arises around steps
  7–14 and affects the later task trajectory.

To distinguish ordinary same-process Monte Carlo variability from
cross-run initialization / backend differences, we built a **fixed-script
repetition probe** on two seeds with per-initial-observation SHA256:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37812061162

- Seed 10013: **six of six** independent env-instance repeats had the
  *same* initial observation SHA256
  `548ac3508402d7eda2304b4e9546832265122313c80f569c72732e5a708cf7e9`,
  and all were source success step 11 / compiled success step 11.
- Seed 10014: **six of six** within-run env-instance repeats had the
  *same* initial observation SHA256
  `ddf3094fc979367baa7b35ed45ddbf5a8abcd14c9ec3a99493811b5e3f78b2d0`,
  and all were source success step **19**, compiled success step **25**.
- The three controller arms had identical initial observation hashes
  **within each case**. This supports fair *within-run* comparisons.
- These twelve trials are **not twelve independent initial seeds**,
  and should not be pooled into the preregistered holdout denominator.

## Conservative interpretation

One CI run confirmed **31/32** compiled successes, including a failed
10014 scene. Another correctly instrumented run and six additional
within-process repeats saw **success** for nominal seed 10014, with
different source episode length (31 vs 19).

The precise reason for this **cross-run discrepancy is not yet known**.
Possible contributors include run-order/init context, simulator model
construction, global RNG state outside reset(seed), dependency/environment
versions and CPU physics numerics. These are hypotheses, not verified root
causes. Do NOT assert a stable seed-10014 failure mode, a deterministic
collision failure, or a universal guarantee of exact semantic conversion.

The appropriate next study is *snapshot-level control*: record a
**complete simulator scene state, controller-owned memory, solver
configuration, code commit and software environment hash**, reload
the exact same initial scene across runs and verify its digest. A nominal
integer reset seed by itself is not a cryptographic scene identity.

All three runs are preserved without data deletion or denominator changes.
