import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch

VALIDATION_DIR = Path(__file__).resolve().parents[1] / ".github" / "validation"
sys.path.insert(0, str(VALIDATION_DIR))

from embodied_semantic_experiment_design import (  # noqa: E402
    DiagnosisDecision,
    DiagnosisLeaf,
    SemanticExperiment,
    _observation_compatible,
    solve_optimal_semantic_diagnosis,
    verify_optimal_semantic_diagnosis,
)
from mani_skill.agents.controllers import PDJointPosController  # noqa: E402
from mani_skill.trajectory.utils.actions.conversion import (  # noqa: E402
    from_pd_joint_delta_pos,
)
from mani_skill.utils import gym_utils  # noqa: E402


class _Combined:
    def __init__(self, arm):
        self.controllers = {"arm": arm}

    def to_action_dict(self, action):
        return {"arm": np.asarray(action, dtype=np.float64).copy()}

    def from_action_dict(self, action_dict):
        return torch.as_tensor(action_dict["arm"], dtype=torch.float64)


class _Env:
    def __init__(self, arm):
        self.unwrapped = SimpleNamespace(
            agent=SimpleNamespace(controller=_Combined(arm)),
            device=torch.device("cpu"),
        )
        self.last_action = None

    def step(self, action):
        self.last_action = np.asarray(action, dtype=np.float64)
        return None, 0.0, False, False, {"success": True}


def _source_arm(monkeypatch):
    arm = object.__new__(PDJointPosController)
    source_low = np.array([-0.1, -0.2], dtype=np.float64)
    source_high = np.array([0.1, 0.2], dtype=np.float64)
    arm.config = SimpleNamespace(
        use_delta=True,
        normalize_action=True,
        lower=source_low,
        upper=source_high,
    )
    arm.action_space_low = torch.tensor(source_low, dtype=torch.float64)
    arm.action_space_high = torch.tensor(source_high, dtype=torch.float64)

    qpos = torch.tensor([[0.0, 0.0]], dtype=torch.float64)
    original_qpos = PDJointPosController.qpos

    def fake_qpos(self):
        if self is arm:
            return qpos
        return original_qpos.fget(self)

    monkeypatch.setattr(PDJointPosController, "qpos", property(fake_qpos))
    return arm


def _target_arm():
    arm = object.__new__(PDJointPosController)
    arm.config = SimpleNamespace(use_delta=False, normalize_action=True)
    arm.action_space_low = torch.tensor([-2.0, -2.0], dtype=torch.float64)
    arm.action_space_high = torch.tensor([2.0, 2.0], dtype=torch.float64)
    return arm


def _round(values):
    return tuple(round(float(value), 12) for value in values)


def _decode_source_delta(source, source_native):
    return gym_utils.clip_and_scale_action(
        torch.as_tensor(source_native, dtype=torch.float64),
        source.action_space_low,
        source.action_space_high,
    ).numpy()


def _decode_target_native(target, target_native):
    return gym_utils.clip_and_scale_action(
        torch.as_tensor(target_native, dtype=torch.float64),
        target.action_space_low,
        target.action_space_high,
    ).numpy()


def _hypothesis_outcomes(source, target, source_native):
    source_native = np.asarray(source_native, dtype=np.float64)
    desired_qpos = _decode_source_delta(source, source_native)

    source_native_passthrough = _decode_target_native(
        target,
        source_native,
    )
    physical_qpos_passthrough = _decode_target_native(
        target,
        desired_qpos,
    )
    reencoded_target_chart = desired_qpos

    return {
        "source-native-passthrough": _round(source_native_passthrough),
        "physical-qpos-passthrough": _round(physical_qpos_passthrough),
        "reencoded-target-chart": _round(reencoded_target_chart),
    }


def _run_production_patch(source, target, source_native):
    source_env = _Env(source)
    target_env = _Env(target)
    from_pd_joint_delta_pos(
        output_mode="pd_joint_pos",
        ori_actions=np.asarray([source_native], dtype=np.float64),
        ori_env=source_env,
        env=target_env,
    )
    return _round(_decode_target_native(target, target_env.last_action))


def test_exact_design_identifies_real_issue_429_target_chart(monkeypatch):
    source = _source_arm(monkeypatch)
    target = _target_arm()

    neutral = np.array([0.0, 0.0], dtype=np.float64)
    informative = np.array([0.5, -0.5], dtype=np.float64)

    neutral_outcomes = _hypothesis_outcomes(source, target, neutral)
    informative_outcomes = _hypothesis_outcomes(source, target, informative)

    assert len(set(neutral_outcomes.values())) == 1
    assert len(set(informative_outcomes.values())) == 3

    experiments = (
        SemanticExperiment(
            name="neutral-zero-action",
            outcomes=tuple(neutral_outcomes.items()),
            cost=0.25,
            risk=0.0,
            probe="source-native=[0,0]",
            observation_atol=1.0e-6,
        ),
        SemanticExperiment(
            name="asymmetric-nonzero-action",
            outcomes=tuple(informative_outcomes.items()),
            cost=1.0,
            risk=0.0,
            probe="source-native=[0.5,-0.5]",
            observation_atol=1.0e-6,
        ),
    )

    result = solve_optimal_semantic_diagnosis(
        (
            "source-native-passthrough",
            "physical-qpos-passthrough",
            "reencoded-target-chart",
        ),
        experiments,
        objective="worst_case",
    )

    assert result.complete
    assert result.optimal_cost == 1.0
    assert isinstance(result.policy, DiagnosisDecision)
    assert result.policy.experiment == "asymmetric-nonzero-action"
    assert verify_optimal_semantic_diagnosis(result, experiments).valid

    observed = _run_production_patch(source, target, informative)
    assert _observation_compatible(
        informative_outcomes["reencoded-target-chart"],
        observed,
        atol=1.0e-6,
    )

    branch = next(
        item
        for item in result.policy.branches
        if _observation_compatible(
            item.outcome,
            observed,
            atol=1.0e-6,
        )
    )
    assert isinstance(branch.child, DiagnosisLeaf)
    assert branch.child.hypotheses == ("reencoded-target-chart",)


def test_real_issue_429_probe_rejects_naive_chart_interpretations(monkeypatch):
    source = _source_arm(monkeypatch)
    target = _target_arm()
    informative = np.array([0.5, -0.5], dtype=np.float64)

    outcomes = _hypothesis_outcomes(source, target, informative)
    observed = _run_production_patch(source, target, informative)

    assert _observation_compatible(
        outcomes["reencoded-target-chart"],
        observed,
        atol=1.0e-6,
    )
    assert not _observation_compatible(
        outcomes["source-native-passthrough"],
        observed,
        atol=1.0e-6,
    )
    assert not _observation_compatible(
        outcomes["physical-qpos-passthrough"],
        observed,
        atol=1.0e-6,
    )
