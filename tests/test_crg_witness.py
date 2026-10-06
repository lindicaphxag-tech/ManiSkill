import dataclasses

import numpy as np

from research.crg_core.witness import (
    build_impossibility_witness,
    build_repair_witness,
    verify_impossibility_witness,
    verify_repair_witness,
)


def test_primal_witness_verifies_robust_repair_without_solver():
    g = np.eye(2)
    d = np.array([0.2, -0.1])
    w = build_repair_witness(g, d, certified_radius=0.5, epsilon_g=0.05, residual_tolerance=0.02, support_delta=d)
    assert w.worst_case_residual_upper < 0.02
    assert verify_repair_witness(g, d, certified_radius=0.5, epsilon_g=0.05, witness=w)


def test_forged_repair_residual_is_rejected():
    g = np.eye(1)
    d = np.array([0.2])
    w = build_repair_witness(g, d, certified_radius=0.5, epsilon_g=0.01, residual_tolerance=0.01, support_delta=np.array([0.2]))
    forged = dataclasses.replace(w, worst_case_residual_upper=0.0)
    assert not verify_repair_witness(g, d, certified_radius=0.5, epsilon_g=0.01, witness=forged)


def test_dual_witness_proves_robust_impossibility_without_solver():
    g = np.array([[1.0]])
    d = np.array([0.8])
    w = build_impossibility_witness(g, d, certified_radius=0.5, epsilon_g=0.1, residual_tolerance=0.1, normal=np.array([1.0]))
    assert np.isclose(w.robust_support, 0.55)
    assert np.isclose(w.distance_lower_bound, 0.25)
    assert np.isclose(w.margin_over_tolerance, 0.15)
    assert verify_impossibility_witness(g, d, certified_radius=0.5, epsilon_g=0.1, witness=w)


def test_model_uncertainty_can_destroy_impossibility_witness():
    g = np.array([[1.0]])
    d = np.array([0.8])
    w = build_impossibility_witness(g, d, certified_radius=0.5, epsilon_g=0.5, residual_tolerance=0.1, normal=np.array([1.0]))
    assert w.margin_over_tolerance < 0
    assert not verify_impossibility_witness(g, d, certified_radius=0.5, epsilon_g=0.5, witness=w)


def test_forged_impossibility_margin_is_rejected():
    g = np.array([[1.0]])
    d = np.array([0.8])
    w = build_impossibility_witness(g, d, certified_radius=0.5, epsilon_g=0.1, residual_tolerance=0.1, normal=np.array([1.0]))
    forged = dataclasses.replace(w, margin_over_tolerance=w.margin_over_tolerance + 1.0)
    assert not verify_impossibility_witness(g, d, certified_radius=0.5, epsilon_g=0.1, witness=forged)
