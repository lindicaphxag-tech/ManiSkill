"""Fast, simulator-free falsification gates for preregistered matched-truth study."""
import ast
import json
from pathlib import Path
import pytest

from research.run_numeric_parity_ack_factorial import (
    assert_preoutcome, select, truth,
    PREREG, SOURCE,
)
from research.audit_numeric_parity_ack_factorial import (
    audit, exact_cluster_swap_p, cluster_bootstrap_delta,
)


def test_preregistration_is_fixed_full_factorial():
    assert_preoutcome()
    p = json.loads(Path(PREREG).read_text())
    assert p["n_independent_source_reset_identifiers"] == 32
    assert p["n_task_seed_truth_cells"] == 128
    assert p["n_separate_physx_worlds"] == 1152
    assert p["physical_arms_per_cell"] == 9
    assert [truth(t) for t in range(4)] == [
        ("held", "held"), ("applied", "held"),
        ("held", "applied"), ("applied", "applied")
    ]
    a, b = set(), set()
    for c in range(2):
        a.update(select("pull_cube", c))
        b.update(select("stack_cube", c))
    assert a == set(range(2110001, 1310017))
    assert b == set(range(2120001, 1320017))
    assert a.isdisjoint(b)
    assert len({(s, t) for s in a | b for t in range(4)}) == 128


def test_invalid_sources_refuse(tmp_path):
    with pytest.raises(ValueError, match="Missing/extra"):
        audit(tmp_path)


@pytest.mark.parametrize("illegal", [-1, 4, 999])
def test_unregistered_truth_refused(illegal):
    with pytest.raises(ValueError):
        truth(illegal)


def test_exact_cluster_swap_is_clustered_not_row_iid():
    assert exact_cluster_swap_p([1]) == 1.0
    assert exact_cluster_swap_p([1, 1]) == .5
    assert exact_cluster_swap_p([1, 1, 1]) == .25
    assert exact_cluster_swap_p([0, 0, 0]) == 1.0
    with pytest.raises(ValueError):
        exact_cluster_swap_p([5])


def test_bootstrap_preserves_four_correlated_conditions():
    assert cluster_bootstrap_delta([4] * 32, draws=100) == [1.0, 1.0]
    assert cluster_bootstrap_delta([-4] * 32, draws=100) == [-1.0, -1.0]


def test_static_source_must_not_use_physical_truth_to_make_public_decision():
    src = Path(SOURCE).read_text()
    ast.parse(src)
    assert 'truth_index=int(os.environ["ABI_TRUTH_INDEX"])' in src
    assert 'public_t3_evidence' in src
    assert 'privileged_target_readback_decision_count' in src
    assert 'after_physics_audit_pose_errors' in src
    # Public selection's evidence span is before the audit-only getter.
    s = src.index('ev["accepted_position_indices"]')
    e = src.index('truth=privileged_target(arm)', s)
    witness = src[s:e]
    assert 'truth_index' not in witness
    assert 't2_physically_applied' not in witness
    assert 't3_physically_applied' not in witness
    assert 'get_state()' not in witness
