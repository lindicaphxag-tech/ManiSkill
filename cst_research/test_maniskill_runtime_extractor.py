from types import SimpleNamespace

import numpy as np

from maniskill_runtime_extractor import (
    compile_maniskill_joint_position_migration,
    extract_maniskill_joint_position_contract,
)
from maniskill_joint_contract import JointTransportStatus


class _NormalizedController:
    def __init__(self, *, use_delta, use_target, low, high):
        self.config = SimpleNamespace(
            use_delta=use_delta,
            use_target=use_target,
            normalize_action=True,
        )
        self.action_space_low = np.asarray(low, dtype=float)
        self.action_space_high = np.asarray(high, dtype=float)

    def get_state(self):
        if self.config.use_target:
            return {"target_qpos": np.zeros_like(self.action_space_low)}
        return {}


class _PhysicalController:
    def __init__(self, *, use_delta, use_target, low, high):
        self.config = SimpleNamespace(
            use_delta=use_delta,
            use_target=use_target,
            normalize_action=False,
        )
        self.single_action_space = SimpleNamespace(
            low=np.asarray(low, dtype=float),
            high=np.asarray(high, dtype=float),
        )

    def get_state(self):
        if self.config.use_target:
            return {"target_qpos": np.zeros_like(self.single_action_space.low)}
        return {}


def test_extractor_reads_normalized_runtime_bounds():
    controller = _NormalizedController(
        use_delta=True,
        use_target=False,
        low=[-0.1, -0.2],
        high=[0.1, 0.2],
    )
    extracted = extract_maniskill_joint_position_contract(controller)
    assert extracted.normalized
    assert not extracted.uses_previous_target
    assert extracted.reference_owner == "current_qpos"
    assert extracted.controller_state_observable
    assert extracted.controller_state_keys == ()
    assert not extracted.requires_stateful_migration
    assert "action_space_low" in extracted.evidence_fields
    assert "get_state()" in extracted.evidence_fields
    np.testing.assert_allclose(extracted.contract.low, [-0.1, -0.2])


def test_extractor_reads_physical_action_space_when_not_normalized():
    controller = _PhysicalController(
        use_delta=False,
        use_target=False,
        low=[-2.0, -1.0],
        high=[2.0, 3.0],
    )
    extracted = extract_maniskill_joint_position_contract(controller)
    assert not extracted.normalized
    assert extracted.reference_owner == "absolute"
    assert not extracted.requires_stateful_migration
    assert "single_action_space.low" in extracted.evidence_fields
    np.testing.assert_allclose(extracted.contract.high, [2.0, 3.0])


def test_runtime_compile_reproduces_issue_429_semantics():
    source = _NormalizedController(
        use_delta=True,
        use_target=False,
        low=[-0.1, -0.1],
        high=[0.1, 0.1],
    )
    target = _PhysicalController(
        use_delta=False,
        use_target=False,
        low=[-2.0, -2.0],
        high=[2.0, 2.0],
    )

    src, tgt, cert = compile_maniskill_joint_position_migration(
        source,
        target,
        current_qpos=np.array([0.2, -0.3]),
        source_target_qpos=np.array([0.2, -0.3]),
        target_target_qpos=np.array([0.2, -0.3]),
        source_native_action=np.array([0.5, -0.5]),
    )

    assert src.controller_class == "_NormalizedController"
    assert tgt.controller_class == "_PhysicalController"
    assert cert.status is JointTransportStatus.EXACT
    np.testing.assert_allclose(cert.target_native_action, [0.25, -0.35])


def test_runtime_compile_retains_saturation_evidence():
    source = _PhysicalController(
        use_delta=False,
        use_target=False,
        low=[-2.0],
        high=[2.0],
    )
    target = _NormalizedController(
        use_delta=True,
        use_target=False,
        low=[-0.1],
        high=[0.1],
    )

    _, _, cert = compile_maniskill_joint_position_migration(
        source,
        target,
        current_qpos=np.array([0.0]),
        source_target_qpos=np.array([0.0]),
        target_target_qpos=np.array([0.0]),
        source_native_action=np.array([1.5]),
    )

    assert cert.status is JointTransportStatus.SATURATED
    assert not cert.target_representable
    assert cert.residual_norm > 1.0


def test_extractor_rejects_incomplete_runtime_contract():
    broken = SimpleNamespace(
        config=SimpleNamespace(
            use_delta=True,
            use_target=False,
            normalize_action=True,
        )
    )
    try:
        extract_maniskill_joint_position_contract(broken)
    except TypeError as exc:
        assert "action_space_low" in str(exc)
    else:
        raise AssertionError("incomplete controller contract was accepted")


def test_extractor_marks_target_relative_controller_as_stateful():
    controller = _NormalizedController(
        use_delta=True,
        use_target=True,
        low=[-0.1, -0.1],
        high=[0.1, 0.1],
    )

    extracted = extract_maniskill_joint_position_contract(controller)

    assert extracted.uses_previous_target
    assert extracted.reference_owner == "controller_target"
    assert extracted.requires_stateful_migration
    assert extracted.controller_state_observable
    assert extracted.controller_state_keys == ("target_qpos",)
    assert "get_state()" in extracted.evidence_fields


def test_extractor_fails_closed_on_state_visibility_not_by_guessing_keys():
    controller = SimpleNamespace(
        config=SimpleNamespace(
            use_delta=True,
            use_target=True,
            normalize_action=True,
        ),
        action_space_low=np.array([-0.1]),
        action_space_high=np.array([0.1]),
    )

    extracted = extract_maniskill_joint_position_contract(controller)

    assert extracted.reference_owner == "controller_target"
    assert extracted.requires_stateful_migration
    assert not extracted.controller_state_observable
    assert extracted.controller_state_keys == ()
