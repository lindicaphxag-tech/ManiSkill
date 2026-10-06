import numpy as np

from cst_validation.clipping_semantics import (
    CoordinateSemantic,
    SaturationContract,
    check_linear_saturation_commutation,
    compile_named_saturation_mapping,
)


def _contract(semantics, names, lower, upper):
    return SaturationContract(
        semantics=tuple(semantics),
        names=tuple(names),
        lower=np.asarray(lower, dtype=float),
        upper=np.asarray(upper, dtype=float),
    )


def test_joint_named_limits_cannot_be_reused_as_task_space_clip():
    joint = _contract(
        [CoordinateSemantic.JOINT_POSITION] * 3,
        ["joint_1", "joint_2", "joint_3"],
        [-1, -1, -1],
        [1, 1, 1],
    )
    task = _contract(
        [CoordinateSemantic.TASK_TRANSLATION] * 3,
        ["x", "y", "z"],
        [-0.1, -0.1, -0.1],
        [0.1, 0.1, 0.1],
    )
    cert = compile_named_saturation_mapping(joint, task)
    assert not cert.compatible
    assert set(cert.incompatible_names) == {"joint_1", "joint_2", "joint_3"}


def test_same_dimension_and_same_names_are_not_enough_when_semantics_differ():
    joint = _contract(
        [CoordinateSemantic.JOINT_POSITION] * 2,
        ["0", "1"],
        [-1, -1],
        [1, 1],
    )
    task = _contract(
        [CoordinateSemantic.TASK_TRANSLATION] * 2,
        ["0", "1"],
        [-0.1, -0.1],
        [0.1, 0.1],
    )
    cert = compile_named_saturation_mapping(joint, task)
    assert not cert.compatible
    assert cert.incompatible_names == ("0", "1")


def test_semantically_matching_named_clip_can_be_transferred():
    a = _contract(
        [CoordinateSemantic.JOINT_DELTA] * 2,
        ["shoulder", "elbow"],
        [-0.1, -0.2],
        [0.1, 0.2],
    )
    b = _contract(
        [CoordinateSemantic.JOINT_DELTA] * 2,
        ["elbow", "shoulder"],
        [-0.2, -0.1],
        [0.2, 0.1],
    )
    cert = compile_named_saturation_mapping(a, b)
    assert cert.compatible
    assert cert.source_indices == (0, 1)
    assert cert.target_indices == (1, 0)


def test_saturation_and_cross_coordinate_transport_do_not_generally_commute():
    source = _contract(
        [CoordinateSemantic.JOINT_DELTA] * 2,
        ["q1", "q2"],
        [-1.0, -1.0],
        [1.0, 1.0],
    )
    target = _contract(
        [CoordinateSemantic.TASK_TRANSLATION] * 2,
        ["x", "y"],
        [-1.0, -1.0],
        [1.0, 1.0],
    )
    # A local kinematic map mixes the two source coordinates.
    J = np.array([[1.0, 1.0], [1.0, -1.0]])
    action = np.array([2.0, 0.5])
    witness = check_linear_saturation_commutation(
        source_action=action,
        transport=J,
        source_contract=source,
        target_contract=target,
    )
    assert not witness.commutes
    # clip_A([2,.5])=[1,.5], then J -> [1.5,.5]
    # J@[2,.5]=[2.5,1.5], then clip_B -> [1,1]
    np.testing.assert_allclose(witness.source_then_transport, [1.5, 0.5])
    np.testing.assert_allclose(witness.transport_then_target, [1.0, 1.0])


def test_saturation_commutes_inside_both_representable_interiors():
    source = _contract(
        [CoordinateSemantic.JOINT_DELTA] * 2,
        ["q1", "q2"],
        [-1.0, -1.0],
        [1.0, 1.0],
    )
    target = _contract(
        [CoordinateSemantic.TASK_TRANSLATION] * 2,
        ["x", "y"],
        [-2.0, -2.0],
        [2.0, 2.0],
    )
    J = np.array([[1.0, 0.2], [-0.1, 1.0]])
    action = np.array([0.2, -0.3])
    witness = check_linear_saturation_commutation(
        source_action=action,
        transport=J,
        source_contract=source,
        target_contract=target,
    )
    assert witness.commutes
    np.testing.assert_allclose(witness.residual, 0.0, atol=1e-12)
