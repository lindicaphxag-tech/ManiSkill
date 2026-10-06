from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{label}: expected exactly one pinned-source match, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("lerobot_root", type=Path)
    args = p.parse_args()
    root = args.lerobot_root

    cfg_path = root / "src/lerobot/policies/act/configuration_act.py"
    cfg = cfg_path.read_text()
    cfg = replace_once(
        cfg,
        "    n_action_steps: int = 100\n\n    normalization_mapping:",
        """    n_action_steps: int = 100

    # Relative actions: every action in a predicted chunk is expressed relative
    # to the observation state captured when that chunk is generated.
    use_relative_actions: bool = False
    # Joint names to keep absolute (for example a binary gripper command).
    relative_exclude_joints: list[str] = field(default_factory=lambda: ["gripper"])
    # Populated from dataset action metadata by make_policy when available.
    action_feature_names: list[str] | None = None

    normalization_mapping:""",
        "ACT config insertion",
    )
    cfg_path.write_text(cfg)

    proc_path = root / "src/lerobot/policies/act/processor_act.py"
    proc = proc_path.read_text()
    proc = replace_once(
        proc,
        """from lerobot.processor import (
    PolicyAction,
    PolicyProcessorPipeline,
    make_default_pre_post_processors,
)
""",
        """from lerobot.processor import (
    AbsoluteActionsProcessorStep,
    PolicyAction,
    PolicyProcessorPipeline,
    RelativeActionsProcessorStep,
    make_default_policy_processor_steps,
    make_default_pre_post_processors,
    make_policy_processor_pipelines,
)
""",
        "ACT processor imports",
    )
    proc = replace_once(
        proc,
        "    return make_default_pre_post_processors(config, dataset_stats, normalizer_device=config.device)\n",
        """    if not config.use_relative_actions:
        return make_default_pre_post_processors(config, dataset_stats, normalizer_device=config.device)

    relative_step = RelativeActionsProcessorStep(
        enabled=True,
        exclude_joints=config.relative_exclude_joints,
        action_names=config.action_feature_names,
    )
    steps = make_default_policy_processor_steps(
        config,
        dataset_stats,
        normalizer_device=config.device,
    )

    # Relative-action statistics describe the values seen by ACT, so the
    # representation conversion must happen before normalization. Inference
    # performs the exact inverse after unnormalization.
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
""",
        "ACT processor construction",
    )
    proc_path.write_text(proc)

    test_path = root / "tests/processor/test_act_processor.py"
    test = test_path.read_text()
    test = replace_once(
        test,
        """from lerobot.processor import (
    AddBatchDimensionProcessorStep,
    DataProcessorPipeline,
    DeviceProcessorStep,
    NormalizerProcessorStep,
    RenameObservationsProcessorStep,
""",
        """from lerobot.processor import (
    AbsoluteActionsProcessorStep,
    AddBatchDimensionProcessorStep,
    DataProcessorPipeline,
    DeviceProcessorStep,
    NormalizerProcessorStep,
    RelativeActionsProcessorStep,
    RenameObservationsProcessorStep,
""",
        "ACT test imports",
    )
    marker = '\ndef test_act_processor_normalization():\n'
    relative_tests = '''
def test_act_processor_relative_actions_roundtrip_and_exclusion():
    config = create_default_config()
    config.use_relative_actions = True
    config.relative_exclude_joints = ["gripper"]
    config.action_feature_names = ["shoulder", "elbow", "wrist", "gripper"]

    preprocessor, postprocessor = make_act_pre_post_processors(config, create_default_stats())

    assert len(preprocessor.steps) == 5
    assert isinstance(preprocessor.steps[3], RelativeActionsProcessorStep)
    assert isinstance(postprocessor.steps[1], AbsoluteActionsProcessorStep)

    state = torch.tensor([1.0, 2.0, 3.0, 0.2, 0.0, 0.0, 0.0])
    absolute_action = torch.tensor([2.0, 4.0, 6.0, 0.5])
    batch = transition_to_batch(create_transition({OBS_STATE: state}, absolute_action))

    processed = preprocessor(batch)
    torch.testing.assert_close(
        processed[TransitionKey.ACTION],
        torch.tensor([[1.0, 2.0, 3.0, 0.5]]),
    )

    recovered = postprocessor(processed[TransitionKey.ACTION])
    torch.testing.assert_close(recovered, absolute_action.unsqueeze(0))


def test_act_relative_actions_are_opt_in():
    config = create_default_config()
    preprocessor, postprocessor = make_act_pre_post_processors(config, create_default_stats())

    assert not any(isinstance(step, RelativeActionsProcessorStep) for step in preprocessor.steps)
    assert not any(isinstance(step, AbsoluteActionsProcessorStep) for step in postprocessor.steps)

'''
    if marker not in test:
        raise RuntimeError("ACT test insertion marker missing")
    test = test.replace(marker, "\n" + relative_tests + "def test_act_processor_normalization():\n", 1)
    test_path.write_text(test)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
