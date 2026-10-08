import json
import subprocess
import sys

import numpy as np

from research.crg_core.verify_impossibility import check_robust_impossibility


def _check(tau=0.1, epsilon=0.1, normal=None):
    return check_robust_impossibility(
        np.array([[1.0]]),
        np.array([0.8]),
        np.array([1.0]) if normal is None else normal,
        certified_radius=0.5,
        operator_error_bound=epsilon,
        trusted_residual_tolerance=tau,
    )


def test_genuine_conditional_impossibility():
    result = _check()
    assert result.arithmetic_witness_valid
    assert np.isclose(result.separation_margin, 0.15)
    assert not result.external_experiment_verified


def test_untrusted_witness_cannot_reduce_trusted_tolerance():
    assert not _check(tau=0.3).arithmetic_witness_valid
    assert not _check(epsilon=0.5).arithmetic_witness_valid


def test_rejects_nonfinite_matrices_and_nonunit_normals():
    assert not _check(normal=np.array([2.0])).arithmetic_witness_valid
    assert not _check(normal=np.array([float("nan")])).arithmetic_witness_valid
    assert not check_robust_impossibility(
        np.array([[float("inf")]]), np.array([0.8]), np.array([1.0]),
        certified_radius=0.5, operator_error_bound=0.1,
        trusted_residual_tolerance=0.1,
    ).arithmetic_witness_valid


def test_distinct_claim_and_normal_cli(tmp_path):
    claim = tmp_path / "trusted-claim.json"
    witness = tmp_path / "untrusted-normal.json"
    claim.write_text(json.dumps({
        "physical_map": [[1.0]], "target": [0.8],
        "certified_radius": 0.5, "operator_error_bound": 0.1,
        "residual_tolerance": 0.1,
    }))
    # The witness cannot overwrite tau, epsilon, radius, or map.
    witness.write_text(json.dumps({"normal": [1.0]}))
    cmd = [
        sys.executable, "-m", "research.crg_core.verify_impossibility",
        "--claim", str(claim), "--witness", str(witness),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["arithmetic_witness_valid"]
    assert report["external_experiment_verified"] is False

    claim_data = json.loads(claim.read_text())
    claim_data["residual_tolerance"] = 0.3
    claim.write_text(json.dumps(claim_data))
    result = subprocess.run(cmd, text=True, capture_output=True)
    assert result.returncode == 2
    assert json.loads(result.stdout)["arithmetic_witness_valid"] is False
