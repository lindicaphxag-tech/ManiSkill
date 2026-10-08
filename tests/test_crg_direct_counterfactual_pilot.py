"""CPU tests on constructed actions only; not live-policy validation."""
import copy
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pytest

from research.crg_core.prospective.aggregate_direct_counterfactual import (
    PROTOCOL, evaluate,
)


def write_fake_bank(folder):
    p = json.loads(PROTOCOL.read_text())
    digest = sha256(PROTOCOL.read_bytes()).hexdigest()
    for seed in p["state_seeds"]:
        records = []
        for request in p["physically_requested_block_deltas"]:
            for split, seeds in p["policy_rng_seed_split"].items():
                for rng in seeds:
                    a_target = [1.0, 2.0]
                    a_base = [0.0, 1.0]
                    b_target = [1.25, 1.25]
                    b_base = [0.25, 0.25]
                    if split=="independent_audit_only":
                        a_target = [1.1, 2.0]
                    z = np.asarray(a_target)-np.asarray(a_base)-np.asarray(b_target)+np.asarray(b_base)
                    records.append(dict(
                        heldout_id=request,split=split,rng_seed=rng,
                        four_raw_first_actions=[a_target,a_base,b_target,b_base],
                        paired_full_response_gap_vector=z.tolist(),
                    ))
        state = dict(
            schema="crg-direct-counterfactual-state-v1",
            reset_seed=seed,
            frozen_protocol_sha256=digest,
            source_sha=p["sources"]["frozen_source_sha"],
            lerobot_sha=p["sources"]["lerobot_sha"],
            state_restore_protocol="reset-fresh-space-block-position-4ulp-v2",
            actual_gym_pusht_distribution_version="synthetic-test-NOT-A-REAL-WHEEL",
            baseline_pixels_sha256="a"*64,
            official_checkpoint_revisions={
                "diffusion":p["sources"]["diffusion_revision"],
                "vqbet":p["sources"]["vqbet_revision"],
            },
            policy_forward_counts={"diffusion":24,"vqbet":24},
            total_policy_forward_counts=48,
            trusted_global_hard_action_bound=False,
            certified_transfer_authorizations=0,
            outcome="DESCRIPTIVE_NO_TRUSTED_BOUND",
            observations=records,
        )
        (folder/f"state-{seed}.json").write_text(json.dumps(state))
    return p


def mutate(folder, seed, op):
    path=folder/f"state-{seed}.json"
    record=json.loads(path.read_text())
    op(record)
    path.write_text(json.dumps(record))


def test_complete_bank_aggregate_honors_all_independent_clusters(tmp_path):
    write_fake_bank(tmp_path)
    result=evaluate(tmp_path)
    assert result["state_clusters_total"]==5
    assert result["dependent_requests_total"]==10
    assert result["official_policy_forward_calls"]==240
    assert result["certified_transfer_authorizations"]==0
    assert result["missing_controller_hard_bound"]
    assert len(result["states"])==5
    for state in result["states"]:
        assert len(state["rows"])==2
        for request in state["rows"]:
            assert request["screen_vs_audit_mean_vector_delta"]==pytest.approx(0.1)
            assert not request["authorized_transfer"]


def test_no_missing_state_deletion_from_denominator(tmp_path):
    write_fake_bank(tmp_path)
    (tmp_path/"state-331.json").unlink()
    with pytest.raises(ValueError,match="missing/duplicate"):
        evaluate(tmp_path)


def test_no_duplicate_seed_or_request_in_stored_evidence(tmp_path):
    write_fake_bank(tmp_path)
    mutate(tmp_path,311,lambda r:r["observations"].__setitem__(1,r["observations"][0]))
    with pytest.raises(ValueError,match="missing, duplicated or reordered"):
        evaluate(tmp_path)


def test_hard_bound_and_transfer_claim_forgery_detected(tmp_path):
    write_fake_bank(tmp_path)
    mutate(tmp_path,313,lambda r:r.update({
        "trusted_global_hard_action_bound":True,
        "certified_transfer_authorizations":5,
    }))
    with pytest.raises(ValueError,match="frozen contract"):
        evaluate(tmp_path)


def test_raw_data_digest_mismatch_is_rejected(tmp_path):
    write_fake_bank(tmp_path)
    def corrupt(r):
        r["observations"][0]["four_raw_first_actions"][0][0]+=1
    mutate(tmp_path,317,corrupt)
    with pytest.raises(ValueError,match="differs from raw"):
        evaluate(tmp_path)


def test_nan_and_incomplete_randomness_do_not_pass(tmp_path):
    write_fake_bank(tmp_path)
    mutate(tmp_path,337,lambda r:r["observations"][0].update({
        "paired_full_response_gap_vector":[float("nan"),0.0]
    }))
    with pytest.raises(ValueError,match="nonfinite"):
        evaluate(tmp_path)


def test_source_revision_tampering_detected(tmp_path):
    write_fake_bank(tmp_path)
    mutate(tmp_path,311,lambda r:r.update({"lerobot_sha":"uncommitted"}))
    with pytest.raises(ValueError,match="frozen contract"):
        evaluate(tmp_path)
