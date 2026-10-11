"""Synthetic plumbing tests only; these are NOT real policy outcomes."""
from __future__ import annotations

import json
import numpy as np
import pytest

from research.crg_core.prospective.evaluate_fresh_pilot import (
    PROTOCOL, _read_protocol, evaluate,
)


def _state(seed, protocol):
    src=protocol["checkpoint_runtime_source"]
    G_a=[[1.0,0.0,0.0],[0.0,1.0,0.0]]
    G_b=[[1.0,0.0,0.0],[0.0,1.0,0.0]]
    pair=[]
    for heldout_id,delta in protocol["heldouts"].items():
        h=np.asarray(delta)/np.asarray(protocol["support_scale"])
        def case(matrix, bias=0):
            response=(np.asarray(matrix)@h + np.asarray([bias,0.0])).tolist()
            return {
                "raw_action_jacobian":matrix,
                "heldout_physical_response":response,
                "static_representation":"absolute_xy",
                "support_ids":["block_x","block_y","block_theta"],
                "action_to_physical_jacobian":np.eye(2).tolist(),
                "physical_support_to_support_chart_jacobian":np.eye(3).tolist(),
            }
        pair.append({
            "pair_id":f"seed-{seed}-{heldout_id}",
            "reset_seed":seed,"heldout_id":heldout_id,
            "a":case(G_a),
            "b":case(G_b,bias=0.02),
        })
    return {
        "schema":"eprc-cross-policy-state-v1",
        "reset_seed":seed,
        "state_restore_protocol":src["state_restore_protocol"],
        "lerobot_commit":src["lerobot_source_sha"],
        "probe_epsilon":src["finite_difference_epsilon"],
        "physical_probe":[2,2,0.01],
        "randomness_seeds":src["randomness_seeds"],
        "heldouts":protocol["heldouts"],
        "policies":{
            "diffusion":{"revision":src["diffusion_checkpoint"],"replicate_count":3,
                         "query_count":27,"stable":True},
            "vqbet":{"revision":src["vqbet_checkpoint"],"replicate_count":3,
                     "query_count":27,"stable":True},
        },
        "pairs":pair,
    }


def _write_states(path,protocol):
    path.mkdir(parents=True,exist_ok=True)
    for seed in protocol["calibration_state_seeds"]+protocol["test_state_seeds"]:
        (path/f"state-{seed}.json").write_text(json.dumps(_state(seed,protocol)))


def test_immutable_preregistration_is_pinned_before_new_data():
    protocol,digest=_read_protocol(PROTOCOL)
    assert len(digest)==64
    assert protocol["expected_state_total"]==13
    assert len(protocol["calibration_state_seeds"])==9
    assert len(protocol["test_state_seeds"])==4
    assert not (set(protocol["test_state_seeds"])&set(protocol["prior_seen_negative_bank_seeds"]))


def test_original_source_and_new_split_replay_without_pseudoreplication(tmp_path):
    proto,digest=_read_protocol(PROTOCOL)
    _write_states(tmp_path,proto)
    result=evaluate(PROTOCOL,tmp_path)
    assert result["frozen_protocol_sha256"]==digest
    assert result["n_calibration_states"]==9
    assert result["n_test_state_clusters"]==4
    assert result["n_dependent_test_pairs"]==8
    assert result["all_states_retained"]
    assert result["total_policy_queries"]==702
    assert not result["independent_external_replication"]
    assert len(result["test_state_diagnostics"])==4
    assert 0<=result["authorized_requests"]<=8
    assert len(result["calibration_digest"])==64


def test_missing_state_cannot_be_dropped_from_denominator(tmp_path):
    protocol,_=_read_protocol(PROTOCOL)
    _write_states(tmp_path,protocol)
    (tmp_path/"state-269.json").unlink()
    with pytest.raises(ValueError,match="269 missing"):
        evaluate(PROTOCOL,tmp_path)


def test_resealing_modified_protocol_json_cannot_change_original_hypothesis(tmp_path):
    protocol,_=_read_protocol(PROTOCOL)
    protocol["physical_response_tolerance_abs_xy"]=0.001
    p=tmp_path/"tampered.json"
    p.write_text(json.dumps(protocol))
    with pytest.raises(ValueError,match="frozen preregistration blob"):
        _read_protocol(p)


def test_mixed_policy_checkpoint_is_rejected(tmp_path):
    protocol,_=_read_protocol(PROTOCOL)
    _write_states(tmp_path,protocol)
    p=tmp_path/"state-211.json"
    raw=json.loads(p.read_text())
    raw["policies"]["diffusion"]["revision"]="latest"
    p.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="checkpoint"):
        evaluate(PROTOCOL,tmp_path)
