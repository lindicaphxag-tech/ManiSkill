import numpy as np

from research.eprc.dec_uncertainty import estimate_dec_uncertainty
from research.eprc.local_model_admissibility import classify_local_model_admissibility
from research.eprc.locality_refinement import evaluate_locality_refinement
from research.eprc.standalone_admissibility import evaluate


def _fixture(seed: int):
    rng = np.random.default_rng(seed)
    base = np.array([[1.2, 0.1], [-0.2, 0.7]])
    fine = np.stack([base + 0.002 * rng.normal(size=base.shape) for _ in range(5)])
    finer = np.stack([base + 0.001 * rng.normal(size=base.shape) for _ in range(5)])
    coarse = base + np.array([[0.12, 0.0], [0.0, 0.04]])
    return coarse, fine, finer


def test_standalone_matches_owner_implementation():
    coarse, fine, finer = _fixture(4)
    out = evaluate(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
        max_q95_radius=0.15,
        contraction_threshold=0.75,
    )

    dec = estimate_dec_uncertainty(
        fine, min_replicates=5, max_q95_radius=0.15
    )
    loc, _ = evaluate_locality_refinement(
        coarse_map=coarse,
        fine_map_replicates=fine,
        finer_map_replicates=finer,
        contraction_threshold=0.75,
    )
    adm = classify_local_model_admissibility(
        dec_stable=dec.stable,
        locality_contracting=loc.contracting,
    )

    assert np.isclose(out.dec_q95_radius, dec.q95_signature_radius)
    assert out.dec_stable == dec.stable
    assert np.isclose(out.coarse_fine_drift, loc.coarse_fine_drift)
    assert np.isclose(out.fine_finer_drift, loc.fine_finer_drift)
    assert np.isclose(out.contraction_ratio, loc.contraction_ratio)
    assert out.locality_contracting == loc.contracting
    assert np.isclose(out.finer_stochastic_radius, loc.finer_stochastic_radius)
    assert out.admissibility.value == adm.state.value


def test_standalone_exposes_all_four_quadrants():
    base = np.eye(2)
    stable = np.stack([base] * 5)
    unstable = np.stack([
        base,
        2.0 * base,
        0.5 * base,
        1.5 * base,
        0.7 * base,
    ])
    contracting_finer = np.stack([base + 0.01 * np.eye(2)] * 5)
    noncontracting_finer = np.stack([base + 0.5 * np.eye(2)] * 5)
    coarse = base + 0.4 * np.eye(2)

    a=evaluate(coarse_map=coarse,fine_map_replicates=stable,finer_map_replicates=contracting_finer)
    b=evaluate(coarse_map=coarse,fine_map_replicates=unstable,finer_map_replicates=contracting_finer)
    c=evaluate(coarse_map=coarse,fine_map_replicates=stable,finer_map_replicates=noncontracting_finer)
    d=evaluate(coarse_map=coarse,fine_map_replicates=unstable,finer_map_replicates=noncontracting_finer)

    assert a.admissibility.value == "ADMISSIBLE_FIRST_ORDER"
    assert b.admissibility.value == "INFORMATION_LIMITED"
    assert c.admissibility.value == "LOCALITY_LIMITED"
    assert d.admissibility.value == "REJECT_LOCAL_MODEL"
