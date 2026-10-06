from __future__ import annotations

from pathlib import Path
import sys


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


root = Path(sys.argv[1])

cfg_path = root / "src/lerobot/policies/act/configuration_act.py"
cfg = cfg_path.read_text()
cfg = replace_once(
    cfg,
    """    n_obs_steps: int = 1
    chunk_size: int = 100
    n_action_steps: int = 100

    normalization_mapping:""",
    """    n_obs_steps: int = 1
    chunk_size: int = 100
    n_action_steps: int = 100

    # Optional state-relative action representation. The action chunk is
    # expressed relative to the state at chunk generation time; queued actions
    # therefore share one anchor until the policy queue drains.
    use_relative_actions: bool = False
    relative_exclude_joints: list[str] = field(default_factory=lambda: ["gripper"])
    # Populated from dataset action metadata by make_policy when available.
    action_feature_names: list[str] | None = None

    normalization_mapping:""",
    "ACTConfig relative-action fields",
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
    """    return make_default_pre_post_processors(config, dataset_stats, normalizer_device=config.device)
""",
    """    # Keep the historical ACT pipeline byte-for-byte equivalent when
    # relative actions are disabled.
    if not config.use_relative_actions:
        return make_default_pre_post_processors(config, dataset_stats, normalizer_device=config.device)

    relative_step = RelativeActionsProcessorStep(
        enabled=True,
        exclude_joints=config.relative_exclude_joints,
        action_names=config.action_feature_names,
    )
    steps = make_default_policy_processor_steps(
        config, dataset_stats, normalizer_device=config.device
    )

    # Raw absolute actions -> state-relative chunk -> normalize -> model.
    # Model output -> unnormalize -> same chunk anchor -> absolute robot action.
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
    "ACT processor implementation",
)
proc_path.write_text(proc)
