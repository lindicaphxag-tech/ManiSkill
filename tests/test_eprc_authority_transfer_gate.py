import numpy as np

from research.eprc.authority_transfer_gate import (
    AuthorityGate,
    AuthorityTrial,
    evaluate_authority_gate,
)


def _trial(z_required: bool, *, irrelevant_rank_loss: bool, success: bool):
    if irrelevant_rank_loss:
        target = np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
                [0.0, 0.0],
            ]
        )
    else:
        target = np.eye(3)

    j = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 0.5 if z_required else 0.0],
        ]
    )
    return AuthorityTrial(
        source_physical_jacobian=j,
        target_action_to_physical_jacobian=target,
        transport_succeeded=success,
        global_rank_flag=(np.linalg.matrix_rank(target) == min(target.shape)),
        clipping_flag=bool(z_required and irrelevant_rank_loss),
    )


def test_projection_gate_beats_global_rank_on_task_restricted_cases():
    trials = []
    # 8 globally rank-deficient but task-compatible successes: global-rank gate gets these wrong.
    for _ in range(8):
        trials.append(_trial(False, irrelevant_rank_loss=True, success=True))
    # 8 task-incompatible failures: projection residual catches them.
    for _ in range(8):
        trials.append(_trial(True, irrelevant_rank_loss=True, success=False))
    # 8 ordinary full-rank successes.
    for _ in range(8):
        trials.append(_trial(True, irrelevant_rank_loss=False, success=True))

    result = evaluate_authority_gate(
        trials,
        gate=AuthorityGate(
            min_trials=20,
            min_projection_auc=0.75,
            required_auc_margin=0.05,
        ),
    )

    assert result.n_trials == 24
    assert result.projection_auc > result.global_rank_auc
    assert result.passed


def test_gate_refuses_small_posthoc_sample():
    trials = [_trial(False, irrelevant_rank_loss=True, success=True) for _ in range(5)]
    result = evaluate_authority_gate(trials)
    assert not result.passed
    assert "insufficient" in result.reason
