import pytest

from research.eprc.physical_ir import (
    ActionSemantics,
    ControllerContext,
    ControllerContract,
    UnrepresentableCommand,
    transport_action,
)


def test_delta_current_to_absolute_preserves_physical_target():
    source = ControllerContract(ActionSemantics.DELTA_CURRENT)
    target = ControllerContract(ActionSemantics.ABSOLUTE)

    result = transport_action(
        source,
        target,
        (0.2, -0.1),
        source_context=ControllerContext(current=(1.0, 2.0)),
        target_context=ControllerContext(current=(7.0, 8.0)),
    )

    assert result.source_canonical_target == pytest.approx((1.2, 1.9))
    assert result.target_action == pytest.approx((1.2, 1.9))

    # Direct tensor copying would mean target=(0.2,-0.1), a different command.
    assert result.target_action != pytest.approx((0.2, -0.1))


def test_delta_target_transport_requires_hidden_target_state():
    source = ControllerContract(ActionSemantics.DELTA_TARGET)
    target = ControllerContract(ActionSemantics.ABSOLUTE)

    with pytest.raises(UnrepresentableCommand, match="previous_target"):
        transport_action(
            source,
            target,
            (0.1,),
            source_context=ControllerContext(current=(0.0,)),
            target_context=ControllerContext(current=(0.0,)),
        )


def test_delta_target_uses_previous_target_not_current_state():
    source = ControllerContract(ActionSemantics.DELTA_TARGET)
    target = ControllerContract(ActionSemantics.ABSOLUTE)

    result = transport_action(
        source,
        target,
        (0.1,),
        source_context=ControllerContext(current=(10.0,), previous_target=(2.0,)),
        target_context=ControllerContext(current=(0.0,)),
    )
    assert result.source_canonical_target == pytest.approx((2.1,))


def test_target_authority_rejects_semantically_correct_but_unreachable_command():
    source = ControllerContract(ActionSemantics.ABSOLUTE)
    target = ControllerContract(
        ActionSemantics.DELTA_CURRENT,
        action_low=(-0.25,),
        action_high=(0.25,),
    )

    with pytest.raises(UnrepresentableCommand, match="outside target controller authority"):
        transport_action(
            source,
            target,
            (1.0,),
            source_context=ControllerContext(current=(0.0,)),
            target_context=ControllerContext(current=(0.0,)),
        )


def test_representability_margin_is_explicit():
    source = ControllerContract(ActionSemantics.ABSOLUTE)
    target = ControllerContract(
        ActionSemantics.DELTA_CURRENT,
        action_low=(-1.0, -1.0),
        action_high=(1.0, 1.0),
    )

    result = transport_action(
        source,
        target,
        (0.4, -0.2),
        source_context=ControllerContext(current=(0.0, 0.0)),
        target_context=ControllerContext(current=(0.1, -0.1)),
    )
    assert result.target_action == pytest.approx((0.3, -0.1))
    assert result.target_representability_margin == pytest.approx(0.7)
