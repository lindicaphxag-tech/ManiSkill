# Source-pinned controller reference-mode probe: preregistration (2026-10-09)

**Source freeze:** branch created from git commit `a82a9876e138da9de12bccccf94f1ad97539acf0` of the actual ManiSkill 3 official simulator fork. This specification is committed BEFORE source implementation and before observing its PhysX result.

## Precisely framed question (no claim of first online system identification)
Can the reference used to interpret a Cartesian delta command be inferred without inspecting `config.use_target`, using **one finite, bounded translation excitation and a subsequent zero-delta probe**, where the simulator exposes separate current-achieved EE and controller-commanded target pose telemetry? Cases: achieved-pose-relative `pd_ee_delta_pose` and prior-target-relative `pd_ee_target_delta_pose`.

This is a **telemetry-assisted controller mode diagnosis**, *not black-box robot system ID*: it requires trusted read-only access to current achieved pose, previous commanded target and post-probe commanded target. If target telemetry is unavailable or forgeable the algorithm **must abstain**. The implementation never changes controller class, policy weights or uses a `config.use_target` switch to make the decision.

## Predeclared execution / scope
- Tasks `PickCube-v1` and `PushCube-v1`; each uses `state`, `physx_cpu`, one environment, `reconfiguration_freq=1`, no pretrained policy and no training.
- Seeds: exactly `24001–24008` in EACH task and BOTH hidden controller modes, 32 physical simulator episodes, with 1 warm-up and at most 1 zero probe each.
- Warmup native Cartesian command: translation x=0.25, others zero; preserve gripper command 0. Verify native command is within [-1,1] and its physical translation command magnitude ≤0.03m before executing; otherwise refuse. Call this command a bounded excitation, **not hardware safe**.
- Probe action: exact zero six-dimensional native arm command. A zero command is only zero *relative command*, not proof of zero physical motion or physical safety.
- Before issuing the probe read previous target and achieved EE base-frame translations; refuse if their discrepancy >0.04m. If discrepancy <0.001m (observations not distinguishable), ABSTAIN, **do not** misclassify the target reference.
- A separate CPU-only evidence classifier accepts the three translation vectors and uses a declared `1e-4m` telemetry tolerance. It returns achieved-relative only when measured post-probe target is within tolerance of previous achieved and separated from previous target; returns target-relative only for the reverse; otherwise abstains. It never reads the true controller mode label; only the outer evaluator knows it.
- The controller receives a true native zero-delta probe **only if preflight passes**. Record every skipped/abstained episode (do not exclude them from denominator).
- Output a JSON file containing ALL 32 outcomes plus source commit, controls, gap and errors; job `success` means completed and valid denominators, not necessarily successful model identification.
- **Prospective accept criterion:** at least 6/8 correctly classified and zero incorrect **out of all seeds** for each (task, mode) 8-run group. Abstentions count as not-correct. If the gap gate leaves fewer than 6 eligible, this gate FAILS; no relaxing the threshold based on data.
- Confounds to disclose: observing internally commanded targets may reveal controller logic, no unknown robot or unseen actuator dynamics, two-mode restricted hypothesis set, no task-level learned PPO recovery and no external third-party independent run. Competing probes and an actual identify→compile→task control pipeline remain future experiments.

The expected diagnostic mechanism is analytically dictated by official ManiSkill controller semantics:
`new_target = compute_target_pose(achieved, zero_delta)` for `use_target=False` and
`new_target = compute_target_pose(previous_target, zero_delta)` for `use_target=True`.
This simple known mapping is not a novel control theorem; the experimental result (if positive) would only show the feasibility of *active reference-mode diagnosis* in a controlled, observed simulator.
