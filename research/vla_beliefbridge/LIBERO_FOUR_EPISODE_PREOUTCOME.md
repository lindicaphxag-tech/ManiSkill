# Four-episode authentic SmolVLA closed-loop competency pilot

This exploratory extension was written before its *four-episode* cohort was executed; it does not relabel the previously observed task-1 success as prospective held-out evidence.

- Native LeRobot and released SmolVLA model: same immutable sources and checkpoint resolver as the completed Task 0/Task 1 one-episode real-pilot workflow.
- Simulator: actual original LIBERO Spatial tasks 0 and 1, unchanged original native relative-action controller, model inference `num_steps=1`, `n_action_steps=1`, CPU OSMesa MuJoCo.
- Four **original official initial-state episodes per task**, no custom easy-state filters, `eval.batch_size=1`, `eval.n_episodes=4`, original fixed init-state enumeration, same seed 1180001. Initial-state index 0 overlaps the previously observed first-episode pilot; explicitly report reuse.
- Original env-level per-episode `successes`, `sum_rewards`, exact total, and all failed trajectories preserved; independent source auditor rejects missing/contradicting denominators.
- Outcome goal: discover whether there is any repeatable no-fault task competence in *this* source/runtime setup, not whether BeliefBridge repairs an unknown ACK.
- Do NOT claim native controller target-state semantics, unknown-ACK fault recovery, full LIBERO-10 benchmark, generalization to ManiSkill PhysX, or third-party external reproduction.
- Distinct prospective fault experiments and fair active readback baselines are gated behind (a) native controller semantic inspection and (b) a task-competent frozen VLA setting.

Both success and failure are scientifically retained. No methodological thresholds are tuned on these four episodes.
