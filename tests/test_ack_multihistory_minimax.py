"""Synthetic ACK minimax solver tests with independent HiGHS oracles.

No PhysX response distributions are calibrated or asserted in this suite.
"""
from itertools import product

import numpy as np
import pytest
from scipy.optimize import linprog

from research.ack_multihistory_minimax import (
    RobustBinaryProbe,
    _prior_worst_case,
    choose_minimax_ack_decision,
)


def _probe(name, q, cost=0.02, attested=True):
    return RobustBinaryProbe(
        name, q, cost, attested, attested, attested,
        "SYNTHETIC-NOT-PHYSICAL-PROOF",
    )


def _data(hs, q=None):
    if q is None:
        q = {h: (0.1, 0.1) if i == 0 else (0.8, 0.8)
             for i, h in enumerate(hs)}
    prior = {h: (1 / len(hs), 1 / len(hs)) for h in hs}
    loss = {h: {d: float(h != d) for d in hs} for h in hs}
    return prior, loss, _probe("p", q)


def _choose(hs, prior, loss, probes, **changes):
    kwargs = dict(
        abstain_cost=0.4,
        trusted_readback_cost=0.3,
        risk_cap=0.25,
        independently_calibrated_prior=True,
        authoritative_readback_attested=True,
    )
    kwargs.update(changes)
    return choose_minimax_ack_decision(hs, prior, loss, probes, **kwargs)


def test_three_histories_binary_signal_still_ambiguous():
    hs = ("held", "applied", "other")
    prior, loss, probe = _data(
        hs, {"held": (0, 0), "applied": (1, 1), "other": (0.5, 0.5)}
    )
    ans = _choose(
        hs, prior, loss, [probe], risk_cap=0.4,
        trusted_readback_cost=0.9,
    )
    assert ans.mode == "PROBE"
    assert ans.worst_case_error_loss == pytest.approx(1 / 3)
    assert ans.no_probe_risk == pytest.approx(2 / 3)
    assert not ans.physical_safety_certified


def test_ambiguous_signal_prefers_trusted_readback():
    hs = ("held", "applied", "other")
    prior, loss, _ = _data(hs)
    evidence = _probe("p", {h: (0.2, 0.8) for h in hs})
    ans = _choose(hs, prior, loss, [evidence], risk_cap=0.01)
    assert ans.mode == "READBACK"
    assert ans.worst_case_error_loss == 0
    assert ans.decoder_on_zero is None


def test_attested_narrow_prior_allows_no_probe():
    hs = ("held", "applied")
    _, loss, probe = _data(hs)
    ans = _choose(
        hs, {"held": (0.98, 0.99), "applied": (0.01, 0.02)},
        loss, [probe], risk_cap=0.025,
        trusted_readback_cost=1, abstain_cost=0.5,
    )
    assert ans.mode == "NO_PROBE"
    assert ans.decoder_on_zero == ans.decoder_on_one == "held"
    assert ans.no_probe_risk == pytest.approx(0.02)


def test_unattested_sources_fail_closed():
    hs = ("held", "applied")
    prior, loss, evidence = _data(
        hs, {"held": (0, 0), "applied": (1, 1)}
    )
    bad = _probe("bad", evidence.signal_one_by_history, attested=False)
    assert _choose(hs, prior, loss, [bad]).mode == "READBACK"
    assert _choose(
        hs, prior, loss, [evidence],
        independently_calibrated_prior=False,
        authoritative_readback_attested=False,
    ).mode == "ABSTAIN"


def test_bounded_prior_simplex_against_independent_linprog():
    rng = np.random.default_rng(20261013)
    for k in (2, 3, 4, 7):
        for _ in range(90):
            seed = rng.dirichlet(np.ones(k))
            lower = seed * rng.uniform(0.1, 1, k)
            upper = seed + (1 - seed) * rng.uniform(0, 1, k)
            loss = rng.uniform(-2, 5, k)
            bounds = list(zip(lower, upper))
            actual = _prior_worst_case(loss, bounds)
            lp = linprog(
                -loss, A_eq=[np.ones(k)], b_eq=[1],
                bounds=bounds, method="highs",
            )
            assert lp.success
            assert actual == pytest.approx(-lp.fun, abs=1e-9)


def test_complete_decoder_against_independent_linprog():
    rng = np.random.default_rng(404209)
    for k in (2, 3, 4):
        hs = tuple(f"h{i}" for i in range(k))
        for _ in range(40):
            center = rng.dirichlet(np.ones(k))
            lows = center * rng.uniform(0.1, 1, k)
            highs = center + (1 - center) * rng.uniform(0.1, 1, k)
            prior = {h: (float(lows[i]), float(highs[i]))
                     for i, h in enumerate(hs)}
            matrix = rng.uniform(0.1, 4, size=(k, k))
            np.fill_diagonal(matrix, 0)
            loss = {h: {d: float(matrix[i, j])
                        for j, d in enumerate(hs)}
                    for i, h in enumerate(hs)}
            q0 = rng.uniform(0, 0.6, k)
            q1 = q0 + rng.uniform(0, 1, k) * (1 - q0)
            intervals = {h: (float(q0[i]), float(q1[i]))
                         for i, h in enumerate(hs)}
            ans = _choose(
                hs, prior, loss, [_probe("p", intervals, cost=0.0001)],
                risk_cap=1e4, abstain_cost=1e4,
                trusted_readback_cost=None,
            )
            oracle_rules = []
            for d0, d1 in product(range(k), repeat=2):
                by_history = np.array([
                    matrix[i, d0] + (
                        q1[i] if matrix[i, d1] >= matrix[i, d0] else q0[i]
                    ) * (matrix[i, d1] - matrix[i, d0])
                    for i in range(k)
                ])
                lp = linprog(
                    -by_history, A_eq=[np.ones(k)], b_eq=[1],
                    bounds=list(zip(lows, highs)), method="highs",
                )
                assert lp.success
                oracle_rules.append((-lp.fun, hs[d0], hs[d1]))
            expected = min(oracle_rules)
            assert ans.mode in ("PROBE", "NO_PROBE")
            if ans.mode == "PROBE":
                assert ans.worst_case_error_loss == pytest.approx(
                    expected[0], abs=1e-8
                )
                assert (ans.decoder_on_zero, ans.decoder_on_one) == expected[1:]


def test_invalid_bounds_loss_and_duplicate_action_rejected():
    hs = ("h0", "h1", "h2")
    prior, loss, probe = _data(hs)
    with pytest.raises(ValueError, match="empty"):
        _choose(hs, {h: (0, 0.1) for h in hs}, loss, [probe])
    with pytest.raises(ValueError, match="identity mismatch"):
        _choose(hs, {"h0": (0, 1)}, loss, [probe])
    corrupted = {h: dict(row) for h, row in loss.items()}
    corrupted["h1"]["h0"] = float("nan")
    with pytest.raises(ValueError, match="loss matrix"):
        _choose(hs, prior, corrupted, [probe])
    with pytest.raises(ValueError, match="duplicate"):
        _choose(hs, prior, loss, [probe, probe])
    with pytest.raises(ValueError, match="probability interval"):
        _choose(hs, prior, loss, [
            _probe("invalid", {h: (0.8, 0.2) for h in hs})
        ])
