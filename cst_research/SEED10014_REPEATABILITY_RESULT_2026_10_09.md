# Post-hoc seed-10014 repeatability audit

Protocol locked *after* observing conflicting one-off outcomes, but
**before** running twelve new repetitions:
[SEED_10014_REPEATABILITY_PRE_REG_2026_10_09.md](SEED_10014_REPEATABILITY_PRE_REG_2026_10_09.md)

Full public CI:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37810027750

Twelve consecutive independent source/compiled/raw-copy triples of
nominal integer seed `10014`, keeping identical published frozen PPO,
ManiSkill PhysX CPU, 50-step horizon and no policy training.

| Replicates | Source success | Compiled success | Raw-copy success |
|---|---:|---:|---:|
| 12/12 run to completion | 12/12 | 12/12 | 0/12 |

Every one of the twelve runs reported:
- initial matched source/target observations: maximum difference exactly 0;
- source task success at step **19**;
- compiled task success at step **25**;
- raw-copy no success by step **50**.

**Conflict:** the original 32-seed sequential holdout had a compiled
failure at seed 10014 and source success at step 31.
A separate instrumented run gave compiled success at a different
step and a different physical trajectory; the new uninstrumented
12-repeat audit was internally stable, but **did not reproduce the
original seed-10014 initial state**.

Conclusion: integer seed alone is an insufficient, currently
unverified identifier for a fully reproducible rollout across these
different jobs/execution orders. This is NOT evidence that the
32-seed holdout log is wrong and does not change its observed 31/32
compiled rate. Neither is this evidence of a stable action-adapter
defect at seed 10014.

The next experiment must preserve and hash the **actual initial task
observation / physical simulator state**, source code/environment
fingerprint and creation order. If initial observations differ,
the same seed across two jobs is NOT a matched counterfactual.

Do not promote twelve repeats of the same initial condition as twelve
independent environment samples. This is an exploratory repeatability
audit, not a prospective new validation cohort.
