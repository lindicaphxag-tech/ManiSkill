# First run v1 -> implementation-only amendment A1 (2026-10-10)

**First archived workflow run:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38014272258

The pre-outcome freeze succeeded. At least the first original physical task worlds were **actually stepped** for PullCube and StackCube before producer jobs failed. They failed in the AFTER-RUN VALIDATION code, at `run_active_probe_full_task_physx.py:105`, not at a simulator/action-controller native command:

```
RuntimeError: known-delivered native t4 physical probe not as registered
```

Source terminal records show the X probe was issued by real PhysX target controllers as `[0.15000000596046448,0,0,0,0,0]`, the standard single-precision representation of the predeclared 0.15. The validator incorrectly compared the **float32-serialized native controller action** to the Python decimal literal using `==`, without tolerance. The task-world post-native target audit measured the preregistered ~0.015 m action target shift.

**Only allowed correction A1:** replace literal float-vector equality checks with an absolute `1e-6` tolerance for each of the six actual command components, without touching native action, semantic belief update, policy weights, study seed/truth/probe schedule, any task loss, official success, source code used for the frozen source PPO, or statistical comparison. Also amend the standalone full-source auditor's identical mistake and update the frozen runner blob SHA in the preflight workflow. Keep all other checks, especially the physically measured target delta (15 mm ± 0.05 mm) and predecision A/B/C action-match SHA checks. DO NOT exclude the first unsuccessful jobs or present the second execution as an untouched first run.

The v1 pre-registration itself is intentionally unchanged, still SHA `9cbe516f24de4c363eb4b6d5ec250d79e83a207a`. All actual amended results must identify themselves as **pre-registered cohort with audited source implementation amendment A1**, *not* independently new prospective seeds, not hidden fresh test data, and not a main-track superiority result.

Research protocol independence: the amendment is numerical serialization tolerance in a source validator ONLY. No adaptive choice of algorithm, amplitude, condition, or threshold from observed native success. Both original failed CI jobs and any new run artifacts remain publicly accessible.
