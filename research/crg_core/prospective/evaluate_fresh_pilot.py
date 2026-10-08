"""Frozen fresh-state policy-transfer calibration pilot aggregator.

The protocol JSON was committed separately BEFORE this program. Never tune
its seeds, tolerance or assumptions using results from this or older banks.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np

from research.crg_core.paired_state_conformal_transfer import (
    ScreenDecision,
    audit_heldout_state,
    fit_state_block_envelope,
    screen_new_state_pair,
)

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "conformal_transfer_fresh_pilot_v1.json"


def _read_protocol(path: Path) -> tuple[dict, str]:
    source = path.read_bytes()
    data = json.loads(source)
    if data.get("schema") != "crg-transfer-conformal-fresh-state-pilot-v1":
        raise ValueError("wrong frozen protocol schema")
    cal = data["calibration_state_seeds"]
    test = data["test_state_seeds"]
    seen = data["prior_seen_negative_bank_seeds"]
    if (len(cal) != 9 or len(test) != 4 or len(set(cal+test+seen)) !=
            len(cal+test+seen)):
        raise ValueError("frozen state split duplicate, overlap or changed size")
    if (data["calibration_alpha"] != 0.10 or
        data["physical_response_tolerance_abs_xy"] != 1.0 or
        data["checkpoint_runtime_source"]["exact_sha"] !=
            "8207ac01c56e75ccee19cba0e75eb0978cde37b2"):
        raise ValueError("unexpected hypothesis or source change")
    return data, sha256(source).hexdigest()


def _read_state(directory: Path, seed: int, protocol: dict) -> dict:
    paths = list(directory.rglob(f"state-{seed}.json"))
    if len(paths) != 1:
        raise ValueError(f"frozen seed {seed} missing or duplicate: {len(paths)}")
    data = json.loads(paths[0].read_text())
    src = protocol["checkpoint_runtime_source"]
    required = {
        "reset_seed":seed,
        "schema":"eprc-cross-policy-state-v1",
        "state_restore_protocol":src["state_restore_protocol"],
        "lerobot_commit":src["lerobot_source_sha"],
        "randomness_seeds":src["randomness_seeds"],
        "probe_epsilon":src["finite_difference_epsilon"],
        "heldouts":protocol["heldouts"],
    }
    for key, value in required.items():
        if data.get(key) != value:
            raise ValueError(f"state {seed}: frozen {key} mismatch")
    if not np.allclose(data["physical_probe"], [2., 2., 0.01], rtol=0, atol=0):
        raise ValueError(f"state {seed}: physical perturbation changed")
    for kind, checkpoint in (
        ("diffusion",src["diffusion_checkpoint"]),
        ("vqbet",src["vqbet_checkpoint"]),
    ):
        p = data["policies"][kind]
        if (p["revision"] != checkpoint or p["replicate_count"] != 3 or
            p["query_count"] != 27):
            raise ValueError(f"state {seed}: {kind} checkpoint/query provenance mismatch")
    if [x["heldout_id"] for x in data["pairs"]] != ["A", "B"]:
        raise ValueError(f"state {seed}: missing or reordered A/B")
    return data


def _group(state: dict, protocol: dict) -> dict:
    output = []
    scale = np.asarray(protocol["support_scale"],dtype=float)
    for p in state["pairs"]:
        heldout=p["heldout_id"]
        a,b=p["a"],p["b"]
        output.append({
            "heldout_id":heldout,
            "map_a":a["raw_action_jacobian"],
            "map_b":b["raw_action_jacobian"],
            "support_delta":(
                np.asarray(protocol["heldouts"][heldout],dtype=float)/scale
            ).tolist(),
            "observed_response_a":a["heldout_physical_response"],
            "observed_response_b":b["heldout_physical_response"],
        })
    return {"state_id":str(state["reset_seed"]),"pairs":output}


def _chart_gate(state: dict) -> bool:
    for pair in state["pairs"]:
        for kind in ("a","b"):
            p=pair[kind]
            if (p["static_representation"] != "absolute_xy" or
                p["support_ids"] != ["block_x","block_y","block_theta"] or
                not np.array_equal(p["action_to_physical_jacobian"],np.eye(2)) or
                not np.array_equal(p["physical_support_to_support_chart_jacobian"],np.eye(3))):
                return False
    return True


def evaluate(path: Path, directory: Path) -> dict:
    protocol,digest=_read_protocol(path)
    calibration_states=[
        _read_state(directory,i,protocol) for i in protocol["calibration_state_seeds"]
    ]
    test_states=[
        _read_state(directory,i,protocol) for i in protocol["test_state_seeds"]
    ]
    envelope=fit_state_block_envelope(
        [_group(s,protocol) for s in calibration_states],
        alpha=protocol["calibration_alpha"],
        source_protocol_digest=digest,
    )
    audits=[]
    test_rows=[]
    naive_errors=0
    authorized=0
    errors=0
    for state in test_states:
        group=_group(state,protocol)
        both_stable=all(state["policies"][kind]["stable"] for kind in ("diffusion","vqbet"))
        supported=_chart_gate(state)
        decisions=[]
        point_results=[]
        for pair in group["pairs"]:
            d=screen_new_state_pair(
                envelope,test_state_id=group["state_id"],pair=pair,
                trusted_response_tolerance=protocol["physical_response_tolerance_abs_xy"],
                local_model_a_admissible=bool(state["policies"]["diffusion"]["stable"]),
                local_model_b_admissible=bool(state["policies"]["vqbet"]["stable"]),
                support_admissible=bool(supported),
                controller_authority_admissible=bool(supported),
            )
            decisions.append(d)
            pred=d.nominal_disagreement
            # For a transparent naive point-reference, compute the same
            # nominal center even when the proposed method must reject.
            a=np.asarray(pair["map_a"],float)
            b=np.asarray(pair["map_b"],float)
            h=np.asarray(pair["support_delta"],float)
            point=float(np.linalg.norm((a-b)@h))
            actual=float(np.linalg.norm(
                np.asarray(pair["observed_response_a"],float)-
                np.asarray(pair["observed_response_b"],float)))
            naive_authorize_similar=point <= protocol["physical_response_tolerance_abs_xy"]
            naive_false=(
                naive_authorize_similar !=
                (actual <= protocol["physical_response_tolerance_abs_xy"])
            )
            naive_errors += int(naive_false)
            point_results.append({
                "heldout_id":pair["heldout_id"],
                "decision":d.decision.value,
                "nominal_gap":point,
                "true_gap":actual,
                "accepted":d.decision in (
                    ScreenDecision.STATISTICALLY_SIMILAR,
                    ScreenDecision.STATISTICALLY_DISTINCT,
                ),
                "naive_point_wrong":bool(naive_false),
            })
        check=audit_heldout_state(envelope,group,decisions)
        authorized+=sum(int(x["accepted"]) for x in point_results)
        errors+=check["false_authorizations"]
        audits.append(check)
        test_rows.append({
            "seed":state["reset_seed"],
            "both_policy_stability_proxies_pass":both_stable,
            "chart_gate":supported,
            "pairs":point_results,
        })
    total=int(2*len(test_states))
    queries=sum(
        int(s["policies"][kind]["query_count"])
        for s in calibration_states+test_states
        for kind in ("diffusion","vqbet")
    )
    if queries!=13*54:
        raise ValueError("unexpected query count / hidden rerun")
    n_block_covered=sum(int(x["state_block_covered"]) for x in audits)
    return {
        "schema":"crg-transfer-conformal-fresh-state-pilot-result-v1",
        "frozen_protocol_sha256":digest,
        "preregistered_calibration_seeds":protocol["calibration_state_seeds"],
        "preregistered_test_seeds":protocol["test_state_seeds"],
        "n_calibration_states":len(calibration_states),
        "n_test_state_clusters":len(test_states),
        "n_dependent_test_pairs":total,
        "calibration_radius":envelope.radius,
        "calibration_k":envelope.k_order_statistic,
        "calibration_state_ids":list(envelope.calibration_state_ids),
        "calibration_digest":envelope.calibration_digest,
        "state_blocks_covered":n_block_covered,
        "state_blocks_total":len(test_states),
        "authorized_requests":authorized,
        "authorization_fraction":authorized/total,
        "false_authorizations":errors,
        "naive_point_reference_false_decisions":naive_errors,
        "always_abstain_coverage":0.0,
        "total_policy_queries":queries,
        "all_states_retained":True,
        "outcome": "ZERO_UTILITY_ALL_ABSTAIN" if authorized==0 else "DESCRIPTIVE_PILOT_NONZERO_COVERAGE",
        "calibration_coverage_type":"exchangeable-state marginal, NOT conditional safety",
        "not_confirmatory_superiority":True,
        "locality_stability_gate_only_proxy":True,
        "independent_external_replication":False,
        "test_state_diagnostics":test_rows,
        "test_block_audits":audits,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--protocol",type=Path,default=PROTOCOL)
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=evaluate(args.protocol,args.input_dir)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
