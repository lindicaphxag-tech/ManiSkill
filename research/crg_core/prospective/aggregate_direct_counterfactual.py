"""Read-only aggregate and anti-tampering audit of frozen direct-response bank.

The true independent unit is the restored PushT state, not its dependent
A/B requests. Original target/baseline first actions are kept in every JSON.
"""
from __future__ import annotations
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "direct_counterfactual_pilot_v1.json"
FROZEN_BLOB = "495eb5f65695cb6b4e7cb22e89e2841fd25c7d6f"


def evaluate(directory: Path, protocol_path: Path = PROTOCOL):
    raw = Path(protocol_path).read_bytes()
    blob = sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if blob != FROZEN_BLOB:
        raise ValueError("preregistered protocol changed")
    p = json.loads(raw)
    digest = sha256(raw).hexdigest()
    valid_state_ids = p["state_seeds"]
    if valid_state_ids != [311,313,317,331,337] or p["hard_controller_action_bounds"] is not None:
        raise ValueError("changed frozen state IDs or trusted bounds")
    expected_pairs = [
        (request, split, int(seed))
        for request in p["physically_requested_block_deltas"]
        for split, seeds in p["policy_rng_seed_split"].items()
        for seed in seeds
    ]
    audit = []
    all_queries = 0
    for seed in valid_state_ids:
        paths = list(Path(directory).rglob("state-"+str(seed)+".json"))
        if len(paths) != 1:
            raise ValueError(f"missing/duplicate preregistered state {seed}: {len(paths)}")
        state = json.loads(paths[0].read_text())
        fixed = {
            "schema":"crg-direct-counterfactual-state-v1",
            "reset_seed":seed,
            "frozen_protocol_sha256":digest,
            "source_sha":p["sources"]["frozen_source_sha"],
            "lerobot_sha":p["sources"]["lerobot_sha"],
            "state_restore_protocol":"reset-fresh-space-block-position-4ulp-v2",
            "official_checkpoint_revisions":{
                "diffusion":p["sources"]["diffusion_revision"],
                "vqbet":p["sources"]["vqbet_revision"],
            },
            "policy_forward_counts":{"diffusion":24,"vqbet":24},
            "total_policy_forward_counts":48,
            "trusted_global_hard_action_bound":False,
            "certified_transfer_authorizations":0,
            "outcome":"DESCRIPTIVE_NO_TRUSTED_BOUND",
        }
        for k,v in fixed.items():
            if state.get(k) != v:
                raise ValueError(f"state {seed}: {k} does not match frozen contract")
        if not state.get("actual_gym_pusht_distribution_version"):
            raise ValueError("unrecorded installed PushT simulator distribution")
        if len(state.get("baseline_pixels_sha256","")) != 64:
            raise ValueError("baseline observation source fingerprint absent")
        entries = state.get("observations",[])
        keys = [(x.get("heldout_id"),x.get("split"),x.get("rng_seed")) for x in entries]
        if keys != expected_pairs:
            raise ValueError(f"state {seed}: missing, duplicated or reordered target/seed")
        for x in entries:
            action = np.asarray(x["four_raw_first_actions"],dtype=float)
            delta = np.asarray(x["paired_full_response_gap_vector"],dtype=float)
            if (action.shape != (4,2) or delta.shape != (2,)
                or not np.isfinite(action).all() or not np.isfinite(delta).all()):
                raise ValueError("invalid or nonfinite recorded physical policy action")
            if not np.allclose(action[0]-action[1]-action[2]+action[3], delta,
                               rtol=0, atol=1e-11):
                raise ValueError("recorded paired response differs from raw model actions")
        rows = []
        for request in p["physically_requested_block_deltas"]:
            pair_groups = {}
            for split in p["policy_rng_seed_split"]:
                values = np.stack([
                    np.asarray(x["paired_full_response_gap_vector"],dtype=float)
                    for x in entries
                    if x["heldout_id"]==request and x["split"]==split
                ])
                pair_groups[split]=values
            screen = pair_groups["decision_only"].mean(axis=0)
            holdout = pair_groups["independent_audit_only"].mean(axis=0)
            rows.append({
                "request":request,
                "decision_seed_mean_response_gap":float(np.linalg.norm(screen)),
                "independent_seed_mean_response_gap":float(np.linalg.norm(holdout)),
                "screen_vs_audit_mean_vector_delta":float(np.linalg.norm(screen-holdout)),
                "n_screen_random_seeds":3,
                "n_audit_random_seeds":3,
                "statistically_certified":False,
                "authorized_transfer":False,
            })
        audit.append({
            "seed":seed,
            "observed_raw_file_sha256":sha256(paths[0].read_bytes()).hexdigest(),
            "gym_pusht_distribution":state["actual_gym_pusht_distribution_version"],
            "rows":rows,
        })
        all_queries+=48
    if all_queries!=p["expected_policy_first_action_calls"] or len(audit)!=5:
        raise ValueError("complete frozen sample denominator not respected")
    return {
        "schema":"crg-direct-counterfactual-pilot-result-v1",
        "frozen_protocol_sha256":digest,
        "state_clusters_total":5,
        "dependent_requests_total":10,
        "official_policy_forward_calls":all_queries,
        "certified_transfer_authorizations":0,
        "outcome":"DESCRIPTIVE_NO_TRUSTED_BOUND",
        "missing_controller_hard_bound":True,
        "simulation_counterfactual_oracle":True,
        "task_rollout_success_measured":False,
        "same_random_seeds_inside_paired_baseline_target_queries":True,
        "independent_external_replication":False,
        "n_independent_policy_random_seeds_per_split":3,
        "states":audit,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    a=parser.parse_args()
    result=evaluate(a.input_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        k:result[k] for k in (
            "state_clusters_total","dependent_requests_total",
            "official_policy_forward_calls","certified_transfer_authorizations","outcome"
        )
    },sort_keys=True))
