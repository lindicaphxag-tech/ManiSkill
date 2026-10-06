from dataclasses import replace

import numpy as np
import pytest

from cst.core import JointControllerContext, JointGoalChart
from cst.proof import (
    emit_exact_joint_transport_proof,
    verify_exact_joint_transport_proof,
)


def _delta_current():
    return JointGoalChart(
        mode="delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )


def _absolute():
    return JointGoalChart(
        mode="absolute",
        normalized=False,
    )


def test_exact_proof_passes_independent_verifier():
    source = _delta_current()
    target = _absolute()
    sx = JointControllerContext(q_current=np.array([0.2, -0.3]))
    tx = JointControllerContext()
    proof = emit_exact_joint_transport_proof(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.5, -0.5]),
        source_context=sx,
        target_context=tx,
    )
    verdict = verify_exact_joint_transport_proof(
        proof,
        source_chart=source,
        target_chart=target,
        source_context=sx,
        target_context=tx,
    )
    assert verdict.valid
    assert verdict.cross_goal_residual <= 1e-12


def test_stale_source_reference_invalidates_proof_identity():
    source = _delta_current()
    target = _absolute()
    sx = JointControllerContext(q_current=np.array([0.2, -0.3]))
    proof = emit_exact_joint_transport_proof(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.5, -0.5]),
        source_context=sx,
        target_context=JointControllerContext(),
    )
    verdict = verify_exact_joint_transport_proof(
        proof,
        source_chart=source,
        target_chart=target,
        source_context=JointControllerContext(q_current=np.array([0.21, -0.3])),
        target_context=JointControllerContext(),
    )
    assert not verdict.valid
    assert not verdict.identity_match


def test_target_action_tampering_is_detected_by_payload_digest():
    source = _delta_current()
    target = _absolute()
    sx = JointControllerContext(q_current=np.array([0.2, -0.3]))
    proof = emit_exact_joint_transport_proof(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.5, -0.5]),
        source_context=sx,
        target_context=JointControllerContext(),
    )
    tampered = replace(
        proof,
        target_action=proof.target_action + np.array([0.01, 0.0]),
    )
    verdict = verify_exact_joint_transport_proof(
        tampered,
        source_chart=source,
        target_chart=target,
        source_context=sx,
        target_context=JointControllerContext(),
    )
    assert not verdict.valid
    assert not verdict.identity_match


def test_chart_bound_drift_invalidates_proof():
    source = _delta_current()
    target = _absolute()
    sx = JointControllerContext(q_current=np.array([0.2, -0.3]))
    proof = emit_exact_joint_transport_proof(
        source_chart=source,
        target_chart=target,
        source_action=np.array([0.5, -0.5]),
        source_context=sx,
        target_context=JointControllerContext(),
    )
    changed_source = JointGoalChart(
        mode="delta_current",
        normalized=True,
        lower=-0.2,
        upper=0.2,
    )
    verdict = verify_exact_joint_transport_proof(
        proof,
        source_chart=changed_source,
        target_chart=target,
        source_context=sx,
        target_context=JointControllerContext(),
    )
    assert not verdict.valid
    assert not verdict.identity_match


def test_nonrepresentable_transport_cannot_emit_exact_proof():
    source = _absolute()
    target = JointGoalChart(
        mode="delta_current",
        normalized=True,
        lower=-0.1,
        upper=0.1,
    )
    with pytest.raises(ValueError, match="nonrepresentable"):
        emit_exact_joint_transport_proof(
            source_chart=source,
            target_chart=target,
            source_action=np.array([1.0]),
            source_context=JointControllerContext(),
            target_context=JointControllerContext(q_current=np.array([0.0])),
        )
