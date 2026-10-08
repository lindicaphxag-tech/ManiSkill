# Frozen PPO seed 10014 reproducibility audit

Declared before the 12-repeat run.

**Motivation:** Original 32-seed holdout recorded a compiled controller
failure on seed 10014:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505

Later standalone instrumented seed-10014 rerun showed a compiled
controller SUCCESS:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717458927

The difference rules out claiming *reliably failing seed 10014*.

## Controlled replication

Execute **12 sequential trials** under exactly the original uninstrumented
three-arm frozen PPO test, changing ONLY the requested seed list to
`(10014,)*12`, recording each trial separately. Hash the raw initial
source state observation before actions, record source/compiled/naive
success and actual completion steps. No added per-timestep diagnostic
queries that might affect simulator caches, and no model updates.

Report count of compiled successes across all 12, distinct initial
observation hashes, and per-run source successes. Equal seed and
equal initial observation are NOT proof of identical entire simulator
state or solver warm start; any nondeterminism needs further study.

Do not pool these 12 repeats with the 32 pre-registered distinct-seed
pilot or use them as independent scenes. No superiority significance
claim is allowed from same-seed repeats.
