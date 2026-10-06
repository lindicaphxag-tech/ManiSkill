from pathlib import Path

from cst_validation.external_contract_audit import audit_isaaclab_task_space_clip


def _write(root: Path, rel: str, text: str):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_audit_requires_repository_native_semantic_witnesses(tmp_path):
    _write(
        tmp_path,
        "source/isaaclab/isaaclab/envs/mdp/actions/task_space_actions.py",
        '''
class DifferentialInverseKinematicsAction(ActionTerm):
    pass
self._IO_descriptor.action_type = "TaskSpaceAction"
index_list, _, value_list = resolve_matching_names_values(self.cfg.clip, self._joint_names)
self._clip = x.repeat(self.num_envs, self.action_dim, 1)
self._processed_actions = torch.clamp(
    self._processed_actions, min=self._clip[:, :, 0], max=self._clip[:, :, 1]
)
''',
    )
    _write(
        tmp_path,
        "source/isaaclab/isaaclab/managers/manager_term_cfg.py",
        '''
class ActionTermCfg:
    clip: dict[str, tuple] | None = None
''',
    )
    _write(
        tmp_path,
        "source/isaaclab_tasks/isaaclab_tasks/contrib/stack/config/so101/pose_ik_action.py",
        '''
clip is not supported for this subclass
task-space pose [pos_xyz, quat_xyzw] does not map to joint names
''',
    )
    _write(
        tmp_path,
        "source/isaaclab_tasks/isaaclab_tasks/contrib/stack/config/so101/pose_ik_action_term.py",
        '''
if self.cfg.clip is not None:
    raise NotImplementedError("does not map to joint-name clip keys")
''',
    )
    result = audit_isaaclab_task_space_clip(tmp_path, commit="fixture")
    assert result.semantic_violation_reproduced


def test_audit_fails_if_task_space_clip_gets_semantic_coordinate_names(tmp_path):
    _write(
        tmp_path,
        "source/isaaclab/isaaclab/envs/mdp/actions/task_space_actions.py",
        '''
class DifferentialInverseKinematicsAction(ActionTerm):
    pass
self._IO_descriptor.action_type = "TaskSpaceAction"
index_list = resolve_task_coordinate_names(self.cfg.clip, self.task_coordinate_names)
self._clip = x.repeat(self.num_envs, self.action_dim, 1)
self._processed_actions = torch.clamp(
    self._processed_actions, min=self._clip[:, :, 0], max=self._clip[:, :, 1]
)
''',
    )
    _write(
        tmp_path,
        "source/isaaclab/isaaclab/managers/manager_term_cfg.py",
        "class ActionTermCfg:\n    clip: dict[str, tuple] | None = None\n",
    )
    _write(
        tmp_path,
        "source/isaaclab_tasks/isaaclab_tasks/contrib/stack/config/so101/pose_ik_action.py",
        "clip is not supported for this subclass; pose does not map to joint names",
    )
    _write(
        tmp_path,
        "source/isaaclab_tasks/isaaclab_tasks/contrib/stack/config/so101/pose_ik_action_term.py",
        'if self.cfg.clip is not None:\n    raise NotImplementedError("does not map to joint-name clip keys")\n',
    )
    result = audit_isaaclab_task_space_clip(tmp_path, commit="fixed")
    assert not result.semantic_violation_reproduced
    assert not result.clip_resolved_against_joint_names
