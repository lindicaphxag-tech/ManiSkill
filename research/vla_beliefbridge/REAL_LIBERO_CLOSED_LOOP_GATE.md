# BeliefBridge-VLA: official closed-loop model gate (pilot; no fault claim)

## Why this gate is more useful than another inference tensor

The genuine HuggingFaceVLA/smolvla_libero checkpoint has already passed an authentic
LeRobot preprocessing + pretrained-model forward test in the parent branch:
[successful run 37916418907](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916418907).
That is **not** an executed robot episode. This new isolated workflow actually calls
the official frozen LeRobot lerobot-eval on the original LIBERO MuJoCo robot
environment, with no ManiSkill controller ABI reinterpretation or synthetic action.

- Exact LeRobot source SHA: b9cb121cb7d4e3e26ec5c906d08dda68d151ba52.
- Actual model: HuggingFaceVLA/smolvla_libero; snapshot locked to the Hub's
  resolved 40-character model revision before evaluation; resolved ID is archived.
- Official task: libero_spatial, task_ids=[0], original fixed init-state,
  seed=1180001, hard reset, native relative controller, one full episode,
  policy.n_action_steps=1. **This is a feasibility pilot, not a full suite.**
- Simulator and actions: MuJoCo LIBERO through its official LeRobot environment;
  actual postprocessed checkpoint actions are stepped. No direct Panda/PhysX
  calls or assumption of shared controller-target memory with ManiSkill.
- Eval evidence: unmodified eval_info.json with original per-episode success
  flag/reward, full execution log (including failures), exact model/source
  identity, Python package freeze, SHA256 ledger, and fail-closed independent
  count/identity audit. An episode that fails the task is *recorded as failure*;
  green CI only means successful execution/audit, not successful manipulation.

**Interpretation:** A successful native VLA episode establishes a necessary
task-competence gate for later matched fault experiments. A failed episode means
this task/checkpoint/control setting cannot establish recovery improvements
without further baseline analysis. Neither outcome proves BeliefBridge repair,
safe control, or compatibility with ManiSkill target-memory semantics.

## Hard scientific decision rule

1. Require the original audited JSON from the actual one-episode task before
   using the term **VLA closed-loop success**.
2. If real_env_success=false, report it and change the task selection only
   with a declared new exploratory protocol. Never cherry-pick this pilot as
   a prospective held-out benchmark.
3. Once an unfaulted base can reliably complete tasks, freeze a larger
   task/seed split (at least 20 episodes), preserve official success,
   and compare the same VLA under matched, physically applied/held ACK
   faults with zero-read, fixed-read, and equal-public-information active
   read baselines.
4. Do not inject faults using a generic action wrapper and label them
   controller target-memory faults: first verify LIBERO's exact native
   underlying target-memory persistence and readback semantics. If they differ,
   adapt the method at a justified native interface or use a verified
   ManiSkill-compatible trained policy instead.

This is independent of the frozen-PPO 64-state results in PRs #130 and #135;
they must not be combined into a VLA task-success result.
