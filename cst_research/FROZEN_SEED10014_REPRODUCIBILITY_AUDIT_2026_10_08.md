# Seed 10014: original prospective failure vs repeated independent successes

**Do not rewrite the original 32-seed cohort.** The frozen PPO
delta→absolute mapping first completed an original preregistered
`10001..10032` run:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505
=> original per-seed reported **31/32**, and seed `10014`
source success / compiled target failure.

Later diagnostic evidence (NOT a fix and not a new test success claim):
- Detailed single-seed trace:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717458927
  => source success step 19 / compiled success step 25.
- **12 independent Python processes** with the same seed and a new
  reset-state SHA fingerprint:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751087938
  => all **12/12 compiled successful**, **12/12 original successful**,
  **0/12 naive successful**; exact initial observation and full
  `env.get_state()` SHA256 repeated across all 12 processes.
- Same-process reproduction of the original **prefix seeds 10001..10013
  followed by 10014**:
  https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751770195
  => seed `10014` compiled success (step 25), source success (step 19)
  and 14/14 successes across the prefix run. Seed 10014 initial state
  fingerprint matched isolated-run SHA.

## Scientific conclusion

The earlier failed episode has **not been reproduced** under current
single-seed, 12-process, and fixed-prefix checks. That does not prove
the earlier failure was bogus; it is real as recorded in the original
CI and must remain in the original numerator/denominator.

The initial fingerprint was not recorded in the original 32-seed
workflow, so we cannot establish bitwise identical environment,
checkpoint execution trace, all unobserved solver internals, runner
dependency versions, or global RNG state between first and later runs.
Initial full-state hashing in subsequent runs rules out differing
reset-state snapshots *within these later runs*, not differences from
the original without its missing hash.

**Avoid claiming** that an actual algorithmic fix, action-memory
transport, deterministic-order problem, or 100% reproducibility was
demonstrated by this diagnostic. Pin exact dependency versions and
add fixed-run repeated checks in a prospective follow-up.

No cherry-picking, replacing original 31/32 with posthoc 32/32, or
using a 12-process diagnostics run as 12 new independent task seeds.
