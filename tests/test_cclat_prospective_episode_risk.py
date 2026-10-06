import numpy as np

from cst_validation.closed_loop_transport import synthesize_closed_loop_transport
from cst_validation.native_physx_two_joint import NativeTwoJointPlant, frozen_policy, linearize
from cst_validation.trajectory_risk import (
    calibrate_episode_max_residual,
    certify_episode_risk_dominance,
    combine_episode_event_families,
)


STATE_LOW = np.array([-0.07, -0.07, -0.12, -0.12], dtype=float)
STATE_HIGH = np.array([0.07, 0.07, 0.12, 0.12], dtype=float)
HORIZON = 12
CALIBRATION_EPISODES = 24
HELDOUT_EPISODES = 12
ALPHA = 0.08
REQUIRED_COVERAGE = 0.92


def _model_next(model, x, u):
    return model.A @ x + model.B @ u


def _episode_events(source_plant, target_plant, source_model, target_model, transport, initial):
    """Collect the frozen residual-event family along one source-policy episode.

    At each source state we score all three model queries that the deployment
    decision may compare: source behavior, transported target behavior, and
    passthrough target behavior.  The state-generation rule is fixed before
    calibration and is reused unchanged for held-out episodes.
    """
    x = np.asarray(initial, dtype=float).copy()
    source_residuals = []
    adapted_residuals = []
    fallback_residuals = []
    records = []

    for _ in range(HORIZON):
        u_src = frozen_policy(x)
        u_adapt = transport.state_gain @ x + transport.action_gain @ u_src
        u_fallback = u_src.copy()

        y_src = source_plant.transition(x, u_src)
        y_adapt = target_plant.transition(x, u_adapt)
        y_fallback = target_plant.transition(x, u_fallback)

        r_src = float(np.linalg.norm(y_src - _model_next(source_model, x, u_src)))
        r_adapt = float(np.linalg.norm(y_adapt - _model_next(target_model, x, u_adapt)))
        r_fallback = float(np.linalg.norm(y_fallback - _model_next(target_model, x, u_fallback)))
        source_residuals.append(r_src)
        adapted_residuals.append(r_adapt)
        fallback_residuals.append(r_fallback)

        records.append(
            {
                "state": x.copy(),
                "source_action": u_src.copy(),
                "actual_source_next": y_src.copy(),
                "actual_adapted_next": y_adapt.copy(),
                "actual_fallback_next": y_fallback.copy(),
            }
        )
        x = y_src

    return (
        combine_episode_event_families(
            np.asarray(source_residuals),
            np.asarray(adapted_residuals),
            np.asarray(fallback_residuals),
        ),
        records,
    )


def test_frozen_episode_risk_certificate_on_prospective_physx_episodes():
    source_ident = NativeTwoJointPlant(
        stiffness=[100.0, 80.0], damping=[10.0, 8.0]
    )
    target_ident = NativeTwoJointPlant(
        stiffness=[60.0, 120.0], damping=[6.0, 12.0]
    )
    source_model = linearize(source_ident)
    target_model = linearize(target_ident)
    transport = synthesize_closed_loop_transport(source_model, target_model)

    source_eval = NativeTwoJointPlant(
        stiffness=[100.0, 80.0], damping=[10.0, 8.0]
    )
    target_eval = NativeTwoJointPlant(
        stiffness=[60.0, 120.0], damping=[6.0, 12.0]
    )

    # Phase 1: freeze calibration on independent episodes.
    rng_cal = np.random.default_rng(2026100601)
    calibration_events = []
    for _ in range(CALIBRATION_EPISODES):
        initial = rng_cal.uniform(STATE_LOW, STATE_HIGH)
        events, _ = _episode_events(
            source_eval,
            target_eval,
            source_model,
            target_model,
            transport,
            initial,
        )
        calibration_events.append(events)

    episode_bound = calibrate_episode_max_residual(
        calibration_events,
        alpha=ALPHA,
    )
    assert episode_bound.finite
    frozen_quantile = float(episode_bound.max_residual_quantile)

    # Phase 2: prospective held-out episodes.  No calibration update is allowed.
    rng_test = np.random.default_rng(2026100602)
    covered_episodes = 0
    accepted = 0
    refused = 0
    harmful_accepts = 0
    accepted_ratios = []
    all_event_maxima = []

    for _ in range(HELDOUT_EPISODES):
        initial = rng_test.uniform(STATE_LOW, STATE_HIGH)
        events, records = _episode_events(
            source_eval,
            target_eval,
            source_model,
            target_model,
            transport,
            initial,
        )
        event_max = float(np.max(events))
        all_event_maxima.append(event_max)
        covered_episodes += int(event_max <= frozen_quantile + 1e-15)

        for record in records:
            cert = certify_episode_risk_dominance(
                source_model,
                target_model,
                transport,
                state=record["state"],
                source_action=record["source_action"],
                episode_residual=episode_bound,
                required_episode_coverage=REQUIRED_COVERAGE,
            )
            actual_adapt = float(
                np.linalg.norm(
                    record["actual_adapted_next"] - record["actual_source_next"]
                )
            )
            actual_fallback = float(
                np.linalg.norm(
                    record["actual_fallback_next"] - record["actual_source_next"]
                )
            )
            if cert.use_transport:
                accepted += 1
                harmful_accepts += int(actual_adapt >= actual_fallback)
                accepted_ratios.append(
                    actual_adapt / max(actual_fallback, 1e-15)
                )
            else:
                refused += 1

    metrics = {
        "calibration_episodes": CALIBRATION_EPISODES,
        "heldout_episodes": HELDOUT_EPISODES,
        "horizon": HORIZON,
        "alpha": ALPHA,
        "required_episode_coverage": REQUIRED_COVERAGE,
        "conformal_rank": episode_bound.order_statistic_rank,
        "frozen_episode_max_quantile": frozen_quantile,
        "covered_episodes": covered_episodes,
        "empirical_episode_coverage": covered_episodes / HELDOUT_EPISODES,
        "heldout_max_event_residual": float(np.max(all_event_maxima)),
        "accepted_decisions": accepted,
        "refused_decisions": refused,
        "harmful_accepts": harmful_accepts,
        "accepted_mean_actual_error_ratio": (
            float(np.mean(accepted_ratios)) if accepted_ratios else float("nan")
        ),
        "accepted_worst_actual_error_ratio": (
            float(np.max(accepted_ratios)) if accepted_ratios else float("nan")
        ),
    }
    print("CCLAT_PROSPECTIVE_EPISODE_RISK_METRICS", metrics)

    # Frozen promotion gate.  A failure is scientific negative evidence; these
    # thresholds must not be relaxed after seeing the held-out result.
    assert episode_bound.max_residual_quantile == frozen_quantile
    assert covered_episodes >= HELDOUT_EPISODES - 2
    assert accepted >= 1
    assert harmful_accepts == 0
    assert metrics["accepted_mean_actual_error_ratio"] < 1.0
