"""Independent exhaustive witness for DP plus input data integrity."""
import random
import pytest
from research.exact_task_readback_oracle_frontier import (
    FIXED,OLD,frontier,brute_force,summarize)

def record(seed, f, o, fr, rr,task="synthetic"):
    return dict(task=task,seed=seed,
        success_once={FIXED:bool(f),OLD:bool(o)},
        privileged_target_readback_decision_count={FIXED:fr,OLD:rr})

def test_200_random_frontiers_match_complete_two_choice_enumeration():
    r=random.Random(20261014)
    for _ in range(200):
        cases=[record(i,r.randrange(2),r.randrange(2),
              r.randrange(1,3),r.randrange(3))
              for i in range(r.randrange(1,10))]
        assert frontier(cases)==brute_force(cases)

def test_strict_two_arm_oracle_not_a_general_action_theorem():
    # 5 fixed-only at zero old read, 1 zero/zero with zero old read,
    # 1 old-only same read, 20 both-success same read, 5 both-fail same.
    rows=([record(i,1,0,1,0) for i in range(5)]
          +[record(5,0,0,1,0),record(6,0,1,1,1)]
          +[record(i,1,1,1,1) for i in range(7,27)]
          +[record(i,0,0,1,1) for i in range(27,32)])
    x=summarize(rows)
    assert x["posthoc_max_savings_without_aggregate_success_loss"]==2
    assert x["posthoc_max_savings_without_ANY_state_level_success_loss"]==1
    assert x["oracle_max_success_with_at_most_fixed_reads_minus_four"]==24
    assert x["fixed_success"]==25

def test_reject_nonbool_success():
    d=record(1,1,0,1,0)
    d["success_once"][FIXED]=1
    with pytest.raises(ValueError):frontier([d])

def test_reject_invalid_paid_read_count():
    d=record(1,1,0,1,0)
    d["privileged_target_readback_decision_count"][OLD]=-1
    with pytest.raises(ValueError):frontier([d])
