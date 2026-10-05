from cst.action_contract import (
    ActionBlockContract,
    ExecutableActionContract,
    compare_action_blocks,
    compare_executable_contracts,
)


def block(*, reference="absolute", normalized=False, semantic_space="joint_position"):
    return ActionBlockContract.create(
        name="arm",
        semantic_space=semantic_space,
        manifold="R^7" if semantic_space == "joint_position" else "SE(3)",
        reference=reference,
        frame="joint" if semantic_space == "joint_position" else "base",
        units=("rad",) if semantic_space == "joint_position" else ("m", "rad"),
        normalized=normalized,
        physical_lower=(-0.1,) * 7 if normalized and semantic_space == "joint_position" else None,
        physical_upper=(0.1,) * 7 if normalized and semantic_space == "joint_position" else None,
        required_state=(
            ("q_current",) if reference == "current_state"
            else ("q_target",) if reference == "target_state"
            else ()
        ),
    )


def executable(b, *, norm="n0", controller="panda/pd_joint_pos"):
    return ExecutableActionContract(
        schema_version="cst-action-contract/0",
        checkpoint_revision="abc123",
        controller_id=controller,
        blocks=(b,),
        normalization_digest=norm,
        preprocessor_digest="pre0",
        postprocessor_digest="post0",
        software=(("maniskill", "3.x"),),
    )


def test_native_equal_requires_resolved_semantics_to_match():
    a = block()
    result = compare_action_blocks(a, a)
    assert result.status == "native_equal"
    assert result.reasons == ()


def test_current_vs_target_delta_requires_transport_not_false_incompatibility():
    current = block(reference="current_state", normalized=True)
    target = block(reference="target_state", normalized=True)
    result = compare_action_blocks(current, target)
    assert result.status == "transport_required"
    assert any("reference" in reason for reason in result.reasons)
    assert any("required_state" in reason for reason in result.reasons)


def test_joint_position_and_ee_pose_are_incompatible_without_explicit_operator():
    joint = block()
    ee = block(semantic_space="ee_pose")
    result = compare_action_blocks(joint, ee)
    assert result.status == "incompatible"
    assert any("semantic_space" in reason for reason in result.reasons)
    assert any("manifold" in reason for reason in result.reasons)


def test_same_weights_with_different_normalization_has_different_identity():
    base = executable(block(), norm="stats-A")
    changed = executable(block(), norm="stats-B")
    assert base.digest() != changed.digest()

    result = compare_executable_contracts(base, changed)
    assert result.status == "transport_required"
    assert any("normalization_digest" in reason for reason in result.reasons)


def test_canonical_digest_is_stable_for_identical_resolved_contract():
    a = executable(block(reference="current_state", normalized=True))
    b = executable(block(reference="current_state", normalized=True))
    assert a.canonical_json() == b.canonical_json()
    assert a.digest() == b.digest()
    assert compare_executable_contracts(a, b).status == "native_equal"


def test_controller_change_prevents_native_equality_even_if_block_schema_matches():
    a = executable(block(), controller="panda/pd_joint_pos")
    b = executable(block(), controller="panda/pd_joint_target_delta_pos")
    result = compare_executable_contracts(a, b)
    assert result.status == "transport_required"
    assert any("controller_id" in reason for reason in result.reasons)


def test_block_count_difference_is_incompatible():
    a = executable(block())
    b = ExecutableActionContract(
        schema_version="cst-action-contract/0",
        checkpoint_revision="abc123",
        controller_id="panda/pd_joint_pos",
        blocks=(block(), block()),
        normalization_digest="n0",
        preprocessor_digest="pre0",
        postprocessor_digest="post0",
        software=(("maniskill", "3.x"),),
    )
    assert compare_executable_contracts(a, b).status == "incompatible"
