#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one source anchor, found {count}")
    return text.replace(old, new, 1)


def patch_file(path: Path, transform) -> None:
    before = path.read_text(encoding="utf-8")
    after = transform(before)
    if before == after:
        raise RuntimeError(f"{path}: transformation produced no change")
    path.write_text(after, encoding="utf-8")


def patch_config(text: str) -> str:
    anchor = """    # Architecture.
    # Vision backbone.
"""
    insert = """    # Relative actions: converts absolute actions to state-relative actions.
    use_relative_actions: bool = False
    # Joint names to keep absolute. Empty list = all action dims relative.
    relative_exclude_joints: list[str] = field(default_factory=lambda: ["gripper"])
    # Populated from dataset action-feature metadata by make_policy when available.
    action_feature_names: list[str] | None = None

    # Architecture.
    # Vision backbone.
"""
    return replace_once(text, anchor, insert, label="ACTConfig relative-action fields")


def patch_processor(text: str) -> str:
    old_import = """from lerobot.processor import (
    PolicyAction,
    PolicyProcessorPipeline,
    make_default_pre_post_processors,
)
"""
    new_import = """from lerobot.processor import (
    AbsoluteActionsProcessorStep,
    PolicyAction,
    PolicyProcessorPipeline,
    RelativeActionsProcessorStep,
    make_default_policy_processor_steps,
    make_default_pre_post_processors,
    make_policy_processor_pipelines,
)
"""
    text = replace_once(text, old_import, new_import, label="ACT processor imports")

    old_return = """    return make_default_pre_post_processors(config, dataset_stats, normalizer_device=config.device)
"""
    new_return = """    if not config.use_relative_actions:
        return make_default_pre_post_processors(
            config, dataset_stats, normalizer_device=config.device
        )

    relative_step = RelativeActionsProcessorStep(
        enabled=True,
        exclude_joints=config.relative_exclude_joints,
        action_names=config.action_feature_names,
    )
    steps = make_default_policy_processor_steps(
        config, dataset_stats, normalizer_device=config.device
    )

    # Match the existing LeRobot relative-action contract:
    # raw -> relative -> normalize -> model -> unnormalize -> absolute.
    # Production rollout/eval binds relative_step to the policy action queue,
    # so one predicted chunk keeps its generation-time anchor until it drains.
    return make_policy_processor_pipelines(
        input_steps=[
            steps.rename_observations,
            steps.add_batch_dim,
            steps.to_device,
            relative_step,
            steps.normalize,
        ],
        output_steps=[
            steps.unnormalize,
            AbsoluteActionsProcessorStep(enabled=True, relative_step=relative_step),
            steps.to_cpu,
        ],
    )
"""
    return replace_once(text, old_return, new_return, label="ACT processor pipeline")


def patch_test(text: str) -> str:
    old_import = """from lerobot.processor import (
    AddBatchDimensionProcessorStep,
    DataProcessorPipeline,
    DeviceProcessorStep,
    NormalizerProcessorStep,
    RenameObservationsProcessorStep,
    TransitionKey,
    UnnormalizerProcessorStep,
)
"""
    new_import = """from lerobot.processor import (
    AbsoluteActionsProcessorStep,
    AddBatchDimensionProcessorStep,
    DataProcessorPipeline,
    DeviceProcessorStep,
    NormalizerProcessorStep,
    RelativeActionsProcessorStep,
    RenameObservationsProcessorStep,
    TransitionKey,
    UnnormalizerProcessorStep,
)
"""
    text = replace_once(text, old_import, new_import, label="ACT test imports")

    anchor = """@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_act_processor_cuda():
"""
    test = '''def test_act_processor_relative_actions_round_trip():
    """ACT relative actions reuse the same state anchor around normalization."""
    config = create_default_config()
    config.use_relative_actions = True
    config.relative_exclude_joints = ["gripper"]
    config.action_feature_names = ["joint_0", "joint_1", "joint_2", "gripper"]
    stats = create_default_stats()

    preprocessor, postprocessor = make_act_pre_post_processors(config, stats)

    assert len(preprocessor.steps) == 5
    assert isinstance(preprocessor.steps[3], RelativeActionsProcessorStep)
    assert len(postprocessor.steps) == 3
    assert isinstance(postprocessor.steps[1], AbsoluteActionsProcessorStep)

    state = torch.tensor([1.0, 2.0, 3.0, 0.25, 0.0, 0.0, 0.0])
    action = torch.tensor([1.5, 1.0, 4.0, 0.8])
    batch = transition_to_batch(create_transition({OBS_STATE: state}, action))

    processed = preprocessor(batch)
    torch.testing.assert_close(
        processed[TransitionKey.ACTION],
        torch.tensor([[0.5, -1.0, 1.0, 0.8]]),
    )

    restored = postprocessor(processed[TransitionKey.ACTION])
    torch.testing.assert_close(restored, action.unsqueeze(0))


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
def test_act_processor_cuda():
'''
    return replace_once(text, anchor, test, label="ACT relative-action regression")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply the minimal ACT relative-action integration to an exact LeRobot checkout."
    )
    parser.add_argument("lerobot_root", type=Path)
    args = parser.parse_args()
    root = args.lerobot_root.resolve()

    patch_file(root / "src/lerobot/policies/act/configuration_act.py", patch_config)
    patch_file(root / "src/lerobot/policies/act/processor_act.py", patch_processor)
    patch_file(root / "tests/processor/test_act_processor.py", patch_test)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
