from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re


@dataclass(frozen=True)
class IsaacLabTaskSpaceClipAudit:
    commit: str
    task_space_action_declared: bool
    clip_resolved_against_joint_names: bool
    clip_applied_on_action_axis: bool
    generic_action_cfg_exposes_name_dict_clip: bool
    independent_subclass_refuses_joint_named_clip: bool
    semantic_violation_reproduced: bool

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _read(root: Path, rel: str) -> str:
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def audit_isaaclab_task_space_clip(
    root: str | Path,
    *,
    commit: str,
) -> IsaacLabTaskSpaceClipAudit:
    """Audit one pinned IsaacLab checkout for action-chart clip semantics.

    This intentionally checks *declared source behavior*, not runtime outcome.
    It asks whether a term that declares itself as a task-space action resolves
    clip keys against joint names and then applies those bounds on action-axis
    coordinates. A current independent subclass refusal is used as a
    repository-native witness that those coordinate systems are not generally
    interchangeable.
    """
    root = Path(root)
    task = _read(
        root,
        "source/isaaclab/isaaclab/envs/mdp/actions/task_space_actions.py",
    )
    cfg = _read(
        root,
        "source/isaaclab/isaaclab/managers/manager_term_cfg.py",
    )
    so101_cfg = _read(
        root,
        "source/isaaclab_tasks/isaaclab_tasks/contrib/stack/config/so101/"
        "pose_ik_action.py",
    )
    so101_term = _read(
        root,
        "source/isaaclab_tasks/isaaclab_tasks/contrib/stack/config/so101/"
        "pose_ik_action_term.py",
    )

    declared = (
        'self._IO_descriptor.action_type = "TaskSpaceAction"' in task
        and "class DifferentialInverseKinematicsAction(ActionTerm)" in task
    )
    joint_keyed = (
        "resolve_matching_names_values(self.cfg.clip, self._joint_names)" in task
    )
    action_axis = (
        re.search(
            r"repeat\(\s*self\.num_envs\s*,\s*self\.action_dim\s*,\s*1\s*\)",
            task,
        )
        is not None
        and "self._processed_actions = torch.clamp(" in task
        and "min=self._clip[:, :, 0]" in task
        and "max=self._clip[:, :, 1]" in task
    )
    generic = (
        "class ActionTermCfg:" in cfg
        and "clip: dict[str, tuple] | None = None" in cfg
    )
    refusal = (
        "is not supported for this subclass" in so101_cfg
        and "does not map to joint names" in so101_cfg
        and "if self.cfg.clip is not None:" in so101_term
        and "raise NotImplementedError(" in so101_term
        and "does not map to joint-name clip keys" in so101_term
    )

    violation = bool(declared and joint_keyed and action_axis and generic and refusal)
    return IsaacLabTaskSpaceClipAudit(
        commit=commit,
        task_space_action_declared=declared,
        clip_resolved_against_joint_names=joint_keyed,
        clip_applied_on_action_axis=action_axis,
        generic_action_cfg_exposes_name_dict_clip=generic,
        independent_subclass_refuses_joint_named_clip=refusal,
        semantic_violation_reproduced=violation,
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    result = audit_isaaclab_task_space_clip(args.root, commit=args.commit)
    rendered = result.to_json()
    print(rendered)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    if not result.semantic_violation_reproduced:
        raise SystemExit(
            "Pinned IsaacLab source no longer exhibits the frozen clip-chart mismatch; "
            "do not cite this case as external CST evidence."
        )


if __name__ == "__main__":
    main()
