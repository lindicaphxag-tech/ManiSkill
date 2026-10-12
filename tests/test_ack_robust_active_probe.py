import numpy as np
import pytest

from research.ack_robust_active_probe import Candidate, choose_probe, segment_distance


def candidate(name, a, b, cost=1, admitted=True):
    return Candidate(name, {"APPLIED": a, "HELD": b}, cost, admitted, admitted)


def design(candidates, *, noise=0.01, attested=True, alpha=(1, 1), budget=10):
    return choose_probe(
        (0, 0, 0), ("APPLIED", "HELD"), candidates,
        alpha_min=alpha[0], alpha_max=alpha[1],
        model_and_sensor_error_m=noise, maximum_cost=budget,
        response_envelope_independently_attested=attested,
    )


def test_segment_distance_parallel_overlapping_and_degenerate():
    assert segment_distance((0, 0, 0), (2, 0, 0), (1, 0, 0), (3, 0, 0)) == 0
    assert segment_distance((0, 0, 0), (0, 0, 0), (1, 0, 0), (1, 0, 0)) == 1
    assert segment_distance((0, 0, 0), (1, 0, 0), (.5, -1, 0), (.5, 1, 0)) == 0
    assert segment_distance((0, 0, 0), (1, 0, 0), (0, 2, 0), (1, 2, 0)) == 2


def test_segment_distance_matches_independent_dense_grid_oracle():
    rng = np.random.default_rng(20261013)
    grid = np.linspace(0, 1, 101)
    for _ in range(100):
        a0, a1, b0, b1 = rng.uniform(-1, 1, (4, 3))
        exact = segment_distance(a0, a1, b0, b1)
        a = a0[None, :] + grid[:, None] * (a1 - a0)
        b = b0[None, :] + grid[:, None] * (b1 - b0)
        oracle = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1).min()
        assert exact >= 0
        assert exact <= oracle + 1e-10
        assert oracle - exact <= 0.03


def test_informative_active_probe_beats_nonidentifying_passive_probe():
    passive = candidate("zero", (0, 0, 0), (0, 0, 0))
    active = candidate("separating", (1, 0, 0), (-1, 0, 0), cost=2)
    selected = design([passive, active])
    assert selected.candidate == "separating"
    assert selected.certified_gap_m == pytest.approx(1.98 - 2e-9)
    assert not selected.physical_safety_certified


def test_segment_overlap_abstains_despite_distinct_nominal_targets():
    # Response intervals can overlap even when nominal endpoints differ.
    proposal = candidate("misleading", (1, 0, 0), (2, 0, 0))
    result = design([proposal], alpha=(.2, .8), noise=0)
    assert result.candidate is None


def test_increasing_sensor_error_only_revokes_certificate():
    p = candidate("small_gap", (.10, 0, 0), (-.10, 0, 0))
    assert design([p], noise=.09).candidate == "small_gap"
    assert design([p], noise=.10).candidate is None
    assert design([p], noise=.15).candidate is None


def test_unattested_unsafe_and_overbudget_candidates_cannot_win():
    perfect = candidate("perfect", (10, 0, 0), (-10, 0, 0))
    unsafe = candidate("unattested", (10, 0, 0), (-10, 0, 0), admitted=False)
    assert design([perfect], attested=False).candidate is None
    assert design([unsafe]).candidate is None
    assert design([perfect], budget=.5).candidate is None


def test_cost_normalization_and_worst_pair_over_three_histories():
    candidates = [
        Candidate("expensive", {"a": (3, 0, 0), "b": (0, 0, 0), "c": (-3, 0, 0)},
                  4, True, True),
        Candidate("cheap", {"a": (2, 0, 0), "b": (0, 0, 0), "c": (-2, 0, 0)},
                  1, True, True),
    ]
    r = choose_probe((0, 0, 0), ("a", "b", "c"), candidates,
        alpha_min=1, alpha_max=1, model_and_sensor_error_m=0.01,
        maximum_cost=4, response_envelope_independently_attested=True)
    assert r.candidate == "cheap"
    assert r.worst_pair in (("a", "b"), ("b", "c"))
    assert r.evaluated == 2


def test_invalid_contracts_fail_closed():
    with pytest.raises(ValueError):
        design([], alpha=(-.1, 1))
    with pytest.raises(ValueError):
        design([], noise=float("nan"))
    with pytest.raises(ValueError):
        design([], budget=0)
    with pytest.raises(ValueError):
        choose_probe((float("inf"), 0, 0), ("a", "b"), [],
            alpha_min=0, alpha_max=1, model_and_sensor_error_m=0,
            maximum_cost=1, response_envelope_independently_attested=True)


def test_closed_loop_identifies_only_nonoverlapping_response_history():
    from research.ack_robust_active_probe import infer_after_probe

    active = candidate("separating", (1, 0, 0), (-1, 0, 0))
    kwargs = dict(alpha_min=1, alpha_max=1, model_and_sensor_error_m=.01,
                  response_envelope_independently_attested=True,
                  actual_probe_dispatch_confirmed=True,
                  fresh_public_observation_confirmed=True)
    def infer(y, **extra):
        return infer_after_probe((0, 0, 0), y, ("APPLIED", "HELD"),
                                 active, **(kwargs | extra))
    assert infer((1.005, 0, 0)).compatible_histories == ("APPLIED",)
    assert infer((-1.005, 0, 0)).compatible_histories == ("HELD",)
    assert infer((0, 0, 0)).status == "MODEL_FALSIFIED"
    assert infer((1, 0, 0), actual_probe_dispatch_confirmed=False).status == "UNATTESTED"
    assert infer((1, 0, 0), fresh_public_observation_confirmed=False).status == "UNATTESTED"
    assert not infer((1, 0, 0)).physical_safety_certified


def test_closed_loop_refuses_ambiguous_history_and_unknown_dynamics():
    from research.ack_robust_active_probe import infer_after_probe

    overlapping = candidate("overlap", (1, 0, 0), (2, 0, 0))
    d = infer_after_probe((0, 0, 0), (.5, 0, 0),
        ("APPLIED", "HELD"), overlapping,
        alpha_min=.2, alpha_max=.8, model_and_sensor_error_m=0,
        response_envelope_independently_attested=True,
        actual_probe_dispatch_confirmed=True,
        fresh_public_observation_confirmed=True)
    assert d.status == "AMBIGUOUS"
    assert d.compatible_histories == ("APPLIED", "HELD")


def test_positive_separation_matches_generated_bounded_response_worlds():
    from research.ack_robust_active_probe import infer_after_probe

    rng = np.random.default_rng(42003)
    action = candidate("a", (1, .5, 0), (-1, -.5, 0))
    kwargs = dict(alpha_min=.8, alpha_max=1, model_and_sensor_error_m=.02,
                  response_envelope_independently_attested=True,
                  actual_probe_dispatch_confirmed=True,
                  fresh_public_observation_confirmed=True)
    assert design([action], noise=.02, alpha=(.8, 1)).candidate == "a"
    for truth, target in action.targets.items():
        for _ in range(100):
            a = rng.uniform(.8, 1)
            noise = rng.uniform(0, .02) * rng.normal(size=3)
            noise = noise / max(np.linalg.norm(noise), 1e-12) * min(np.linalg.norm(noise), .02)
            y = a * np.asarray(target) + noise
            result = infer_after_probe((0, 0, 0), y,
                ("APPLIED", "HELD"), action, **kwargs)
            assert result.status == "UNIQUE"
            assert result.compatible_histories == (truth,)
