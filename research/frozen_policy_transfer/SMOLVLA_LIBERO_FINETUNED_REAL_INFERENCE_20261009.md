# Real public VLA checkpoints: Base vs LIBERO-finetuned original inference, verified 2026-10-09

**Important:** two actual checkpoint inference runs succeeded. **No VLA robot task rollout, WAM world-state prediction, changed policy training, clinical or hardware safety, or external original-method validation was performed.**

## Full original reproducible source

| Published checkpoint | Exact Hugging Face resolved model SHA | Original 1-frame real LIBERO result | CPU forward |
|---|---|---|---|
| [`lerobot/smolvla_base`](https://huggingface.co/lerobot/smolvla_base) | `5e8d12a6e2975b0e5e5fce7c8caf47c371d257b6` | **postprocessed `[1,6]`**, all finite | **29.363 s** |
| [`HuggingFaceVLA/smolvla_libero`](https://huggingface.co/HuggingFaceVLA/smolvla_libero) | `6721902bc4d61e50a3bfdb11dfb4cb626f05d102` | **postprocessed `[1,7]`**, all finite | **9.816 s** |

Both were loaded via official `SmolVLAPolicy.from_pretrained` with the resolved pinned revision, and used real `lerobot/libero` dataset original episode-0 imagery, `make_pre_post_processors` from the exact same checkpoint revision, `policy.select_action` in eval/no-grad mode and the actual output postprocessor.

Real dataset revision for BOTH runs: `a1aaacb7f6cd6ee5fb43120f673cebb0cfea7dd4`. Official LeRobot library code exact revision: `b9cb121cb7d4e3e26ec5c906d08dda68d151ba52`, Python 3.12, PyTorch 2.11.0+cu130 installed; both jobs used CPU `select_action`. A single observed runtime per checkpoint is **NOT** a valid hardware throughput benchmark or speed superiority claim.

### Real source artifacts, unmodified logs and model/data hash evidence
- [General SmolVLA base **SUCCESS** run #37915931628](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915931628) / [complete actual source artifact #11608879045](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915931628/artifacts/11608879045).
  - Real dual-view `lerobot/libero` input images were `observation.images.image` and `observation.images.image2`. The general checkpoint expects `observation.images.camera1/camera2`, so the preprocessor smoke added an **explicitly recorded input-key rename**. This matches field names, **NOT independently proven camera optical-frame calibration**.
  - After official preprocessing and inference, the checkpoint returned finite action `shape=[1,6]`, range `[-0.7019544244, 2.1112532616]`. Zero native Panda actions issued.
- [Task-tuned LIBERO SmolVLA **SUCCESS** run #37916418907](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916418907) / [complete actual source artifact #11608969830](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916418907/artifacts/11608969830).
  - The fine-tuned checkpoint's expected image feature names already match the real LIBERO dataset images, so **zero camera-field rewrites** were applied.
  - The published fine-tuned model's actual postprocessed action was **shape `[1,7]`**, finite, observed range `[-1.0028998852, 0.03703292459]`. Zero native Panda actions issued.
- Full original source reproducer: [`real_smolvla_checkpoint_probe.py`](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/beliefbridge-vla-action-contract-20261009/research/vla_beliefbridge/real_smolvla_checkpoint_probe.py).
- [Model-source geometry and missing-ACK control abstraction](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/beliefbridge-vla-action-contract-20261009/research/vla_beliefbridge/vla_controller_bridge.py) / [GitHub real-source unit tests](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/vla-beliefbridge-contract.yml) / [Draft research integration PR #133](https://github.com/lindicaphxag-tech/ManiSkill/pull/133).

## Correct scientific interpretation

1. The general base model on this actual frame **does not match** a desired 7D Panda EE delta + gripper interface even in dimension, and cannot be dispatched by the gateway. The genuine LIBERO fine-tuned checkpoint matches the **seven-dimensional native LIBERO action shape** and uses the correct camera key identity. This is necessary but **not sufficient** to prove correct physical action semantics on ManiSkill.
2. The fine-tuned output range includes a value slightly below -1, and it is **not permissible to assume** the first 6 components are already in meters/radians or that the last channel maps to a ManiSkill Panda gripper. The complete LIBERO OSC normalization, reference-frame rule, gripper convention, LeRobot official postprocessing and ManiSkill target-relative action chart MUST be verified; no silent clipping or zero-filling.
3. The controller research gate explicitly requires a real task-specific action representation, checkpoint SHA, normalizer SHA, fresh RGB/proprioceptive observations, a valid finite memory belief, and a fail-closed per-step command certificate. It invalidates stale LeRobot queued actions and asynchronous policy results after target-state changes. **These parts have controller-source tests but have not been connected to a successful original VLA task rollout.**
4. The model and checkpoint were originally built/trained by their respective upstream authors. This work contributes an evidence-driven cross-stack interface and reproducible failure-mode analysis, **not** the original SmolVLA algorithm/checkpoint or independent validation of new WAM/VLA performance.

## Best-cost next experiment (not yet done)

**Use the actual released fine-tuned LIBERO checkpoint**, not `smolvla_base`, and implement an explicitly verified `LIBERO OSC 7D ↔ ManiSkill root-frame target-relative actuator` action adapter, validated on identical no-fault initial states first. Then compare true frozen VLA with and without BeliefBridge under two native target-hold faults on fresh registered seeds. Include post-readback singleton fix, full-vs-selective query accounting and a fixed-query strong baseline. If no-fault genuine VLA cannot accomplish the task under matched images/action contract, STOP rather than advertising a fault-recovery success rate.

No original VLA-based fault-recovery success or external scientific acceptance is presently claimed.
