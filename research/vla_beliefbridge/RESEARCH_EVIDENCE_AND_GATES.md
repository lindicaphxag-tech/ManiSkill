# BeliefBridge-VLA: actionable interface, original hypothesis, and strict evidence gates

**Status 2026-10-09:** *real-source correctness prototype*; not a new trained VLA, not WAM, not independent research adoption, and not a robot-safety certificate.

## Scientific objective
A VLA produces a future action chunk under an RGB-language-proprioceptive observation. Under a target-relative Cartesian controller, the controller's private *last commanded target* can differ from public achieved end-effector pose if an ACK is missing, a target is held, or a command is not delivered. Merely replaying the same VLA chunk is incorrect because the future action conversion depends on hidden target-memory history.

**Hypothesis to falsify:** One-step receding-horizon VLA with a complete finite controller-target belief, explicit bounded common native action, authoritative readback on conditional denial, and chunk invalidation can preserve more tasks per privileged target read under unknown execution acknowledgements than a task-matched VLA with either blind chunk replay or indiscriminate fixed-time readback.

This is a **candidate** new contribution at the VLA/controller interface; it is NOT demonstrated original-task improvement yet.

## Current actual implementation (inspected)

- [Production API source: typed physical action + provenance, fresh observation, `UncertainDeliveryBelief` and `common_multi_history_command`](./vla_controller_bridge.py).
- [Tests directly executing the real previous ManiSkill finite-belief class and SE(3) controller geometry](../../tests/test_vla_beliefbridge_actual_controller.py).
- [Real-source numerical test workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/vla-beliefbridge-contract.yml) passes the source K-history model without any fake VLA model claim.
- The gateway requires an **operator-verified**, task-specific physical schema: `[dx,dy,dz,rotvec_x,rotvec_y,rotvec_z,gripper]`, root frame, left-multiplied orientation, meters/radians, genuine LeRobot postprocessor and immutable checkpoint + normalizer revisions. `ActionProvenance` is a strongly checked **declared contract**, not evidence that an upstream pretraining corpus actually used it.
- A passed action is a **conditional last-commanded-target setpoint tolerance** only. IK, collision, contact force, tracking, limb torque, movement legality and physical hardware safety are *not* certified.
- An action rejection never automatically reads private target memory or invents it from an observed achieved pose. A deliberate `authoritative_controller_target_readback` must be supplied; it collapses the belief to one target state, invalidates old chunks and requires a new public observation.
- For actual LeRobot policy runtime, `gateway.bind_live_policy(policy)` requires official `policy.drop_queued_actions()` and `count_queued_actions()`. It refuses live policy objects that cannot prove stale action queue invalidation. It discards the queue after every commanded dispatch/unknown ACK/readback. **Never repurpose queued pre-fault actions**.
- **New asynchronous completion-generation contract:** stamp each public visual observation when inference is requested with `gateway.current_inference_generation`, send it back in `VisualObservation.inference_generation`, and check that it still matches at response time. Any dispatch, ACK or trusted readback flushes the policy queue **and increments this generation**, so delayed old inference results are rejected even if they arrive after the queue was cleared. [Direct real-geometry async stale-result regression](../../tests/test_vla_beliefbridge_actual_controller.py). This is a correctness contract, not a proven low-latency async VLA robot system.
- Finite belief hypotheses are inherited from the original upstream-modeled unknown ACK implementation; no false collapse on missing feedback. Exceeding the declared model max is a hard failure, not silent pruning.

## True pretrained VLA verification (separate from controller action compatibility)

- [Actual SmolVLA model + original LIBERO sample inference script](./real_smolvla_checkpoint_probe.py) uses **released** `lerobot/smolvla_base` weights, Hugging Face Hub model SHA, official `lerobot/libero` dataset revision, real RGB frames, and exactly matched official LeRobot preprocessing and postprocessing.
- [Public true model load/forward workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/real-smolvla-checkpoint-probe.yml) pins Hugging Face LeRobot source to `b9cb121cb7d4e3e26ec5c906d08dda68d151ba52`; records the released checkpoint SHA, actual input keys, tensor shape, finiteness and source environment.
- **A successful model load is ONLY evidence of pretrained VLA forward inference, not robot task success.** The public generic base checkpoint is not automatically a certified ManiSkill Cartesian controller, and source LIBERO convention requires independent frame/gripper/controller equivalence checks before physical dispatch. A tensor having seven values is not sufficient.

## What is independently established versus still unmeasured

| Boundary | Current factual state |
|---|---|
| Two unknown-ACK, four-possible-controller-memory native Panda closed loop with source-frozen third-party PPO | Prior native PhysX study completed; see repository's 64-state original full results |
| Invalid post-readback multi-target cardinality cache | Fresh 16-state native PhysX validation completed; corrected fixed and phase Stack arm produce identical paired outcomes |
| Typed VLA physical action and chunk invalidation contract | Source implemented; real finite-belief / actual geometry integration tests are publicly runnable |
| Actual released SmolVLA forward over actual observations | Separate checkpoint probe; only mark complete if actual model load succeeds and raw result JSON produced |
| Real SmolVLA-controlled ManiSkill task success under faults | **NOT TESTED** |
| WAM predictions of future state, or training a WAM | **NOT IMPLEMENTED / NOT TESTED** |
| Third-party maintainer or external investigator validates new BeliefBridge-VLA | **NOT YET** |

## Hard next benchmark, not a marketing checklist

1. **Confirm exact trained robot-action ABI**: image frame mapping, action normalization/statistics, observation state channels, `ee_delta` vs joint/absolute conventions, gripper scale and world/root vs local delta rotation. Prefer a *task-matched fine-tuned pretrained VLA* rather than universal base weights. Reject incompatible schemas before PhysX dispatch.
2. Verify *unfaulted native task success* from the same exact VLA checkpoint and camera preprocessing. Otherwise fault-recovery rates are uninterpretable.
3. Under the same native target-hold fault, same seeds and same truly executed policy, compare: unmodified VLA actions, VLA with fixed private target readback, VLA with finite-belief certificates/no reads, VLA with conditional read and fresh action replanning.
4. Freeze task seeds, read budgets and method before outcomes; record official success, actual readback counts, belief width and real/masked actuator target bound witnesses; run outside-lab held-out verification.
5. Only after a real and repeatable closed-loop VLA improvement, consider a lightweight future-state dynamics predictor (WAM-inspired) that estimates **task cost of deferring information**, compared with other query budgets and state-observation baselines.

## Prior art and appropriate credit
- [Hugging Face LeRobot official SmolVLA docs](https://huggingface.co/docs/lerobot/smolvla): action chunking, official preprocessing and async inference are **existing** contributions.
- [LeRobot action representation guide](https://huggingface.co/docs/lerobot/action_representations): joint vs EE and absolute vs delta action representations are **existing** distinctions.
- [Original full 64-state frozen-PPO double-ACK study](../frozen_policy_transfer/COMPOUND_ACK_NEW64_AUTHENTIC_PHYSX_FINDINGS.md) and [stale readback semantic repair](../frozen_policy_transfer/READBACK_SINGLETON_CONTRACT_FRESH16_20261009.md) give our project-specific implementation provenance; they do not prove VLA performance.

**Scientific gate:** no "VLA gains", "WAM original model", "safe robot" or "top-tier accepted" statements until independently reproduced task-level native outcomes support the claim.
