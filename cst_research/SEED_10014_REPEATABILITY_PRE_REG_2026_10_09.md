# Seed 10014 stability audit — preregistered rerun protocol

The original *preregistered 32-seed holdout* had seed 10014 compiled
failure (source success at step 31). The later instrumented one-off
reproduction of the same seed yielded compiled success. We do NOT
retroactively replace the holdout outcome.

This new audit is **exploratory**, triggered by the observed discrepancy.

- Use exactly **12 consecutive complete rollouts** of seed `10014` in a
  single clean GitHub Actions job.
- Run the **unmodified verified** source / compiled / naive PPO controller
  swap code, not the step-instrumented variant, except for a wrapper
  selecting seed and repetition count.
- Same external frozen PPO hash, same native ManiSkill PhysX CPU
  backend, 50-step task horizon, and exactly checked identical initial
  observations in each fresh triple.
- Log each repetition's source, compiled, naive success and steps,
  without selective retry or abort.
- Observe whether compile success is stable across repetitions despite
  nominal identical seed. Do not attribute variance to a particular
  numerical or software cause without a separate intervention and
  environment fingerprint.
- This repeat audit is NOT another independent holdout sample and must
  not enter the 32-seed denominator.
