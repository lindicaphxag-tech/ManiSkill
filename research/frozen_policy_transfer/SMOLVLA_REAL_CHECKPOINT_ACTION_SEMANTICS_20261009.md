# Real released SmolVLA base checkpoint on REAL LIBERO observation: semantic-action contract falsification

**2026-10-09 — original actual Hugging Face pretrained model forward completed successfully, source- and revision-pinned; NO robot task success claimed.**

## Immutable actual execution and evidence
- [GitHub Actions full CPU job #37915931628 — SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915931628).
- [Original model/model-data/processor/source experiment artifact #11608879045](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915931628/artifacts/11608879045) with full original `real_inference_full.log`, JSON result, actual original source Git blobs, `pip freeze --all` and SHA-256 of all files.
- Official unchanged [Hugging Face `lerobot/smolvla_base`](https://huggingface.co/lerobot/smolvla_base) actual model SHA: `5e8d12a6e2975b0e5e5fce7c8caf47c371d257b6`.
- Real original [`lerobot/libero` dataset](https://huggingface.co/datasets/lerobot/libero), SHA: `a1aaacb7f6cd6ee5fb43120f673cebb0cfea7dd4`. Original episode 0, two actual 256×256 camera streams and proprioceptive/language fields; no generated or fake model observations.
- Official LeRobot source fixed to Git SHA `b9cb121cb7d4e3e26ec5c906d08dda68d151ba52`, Python 3.12, official `make_pre_post_processors(..., pretrained_revision=actual_model_sha)`, genuine `SmolVLAPolicy.from_pretrained(..., revision=actual_model_sha)`, `policy.select_action(preprocess(real_frame))`, postprocessed physical action output. The model `eval` and `torch.inference_mode` paths were used, not random policy initialization.
- One explicit and logged camera input rename for inference: `observation.images.image → observation.images.camera1`, `observation.images.image2 → observation.images.camera2`. This matches the declared model input feature keys **but does not prove physical camera calibration, viewpoint equivalence, or controller action semantics**.
- Actual CPU model forward time **29.363 seconds** following model init **17.134 seconds** and dataset load **1.377 seconds** on the cited runner.

## CRITICAL observed robot-action incompatibility

The real released checkpoint produced **postprocessed action tensor [1, 6]**, 6 values, finite, observed `min=-0.7019544244`, `max=2.1112532616`.

This is NOT the 7D **(XYZ EE delta, axis-angle root-left, gripper)** contract required by the newly developed ManiSkill BeliefBridge-VLA gateway and by the source LIBERO actuator schema. A 6D tensor alone does not establish even which of those channels are joint values, Cartesian displacements, or orientations. **Do not append a zero gripper, silently relabel the vector, use it as a Panda action or report robot tasks as evaluated.**

Consequently, [the typed action ABI gate and multi-history controller authorization code](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/beliefbridge-vla-action-contract-20261009/research/vla_beliefbridge/vla_controller_bridge.py) correctly rejects this incompatible model–controller contract unless a task-specific fine-tuned checkpoint with independently verified physical units, frame, rotation rule, gripper, and true model postprocessing is supplied.

The base model is a general foundation checkpoint intended to be adapted to specific tasks; an actual LIBERO fine-tuned released policy offers a better **candidate** for the next original complete robotics study. At the time of writing this report, no LIBERO-fine-tuned model result or native robot task outcome is claimed. [Candidate released finetune](https://huggingface.co/HuggingFaceVLA/smolvla_libero).

## Why this is useful and what it is NOT
- Demonstrates *real released VLA weight inference* rather than recycled frozen PPO benchmarks, and pinpoints a verifiable physical action-ABI failure.
- Shows that even when original image tensors and policy feature keys match after an explicit map, the action semantic contract can still fail. We do **not** treat shape compatibility as a substitute for units, reference frame, calibration or controller provenance.
- Does **NOT** implement or empirically test a WAM, future physical state prediction, a robot-safe controller, a task-level success improvement, physical packet loss, external group adoption or a peer-reviewed publication.

## Next honest performance gate
1. A genuine fine-tuned VLA whose real postprocessed action dimensions match the task, with an explicit, auditable mapping of state+camera+root-frame action units.
2. Verify nonfaulted success using that same published checkpoint and native simulator; stop if it does not control the task at all.
3. On fresh registered seeds, inject the same controller-memory ACK uncertainty; compare naive VLA, fixed private target readback, finite-belief with no private access, and finite-belief with conditional private access. All use the SAME authentic VLA checkpoint.
4. Require original full trajectories and matched budgets, report failure episodes and independent external replication. Do not infer VLA gains from earlier frozen PPO results.

This report explicitly preserves original released checkpoint authorship and distinguishes source model inference from downstream research innovation.
