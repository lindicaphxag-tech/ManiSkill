"""Source-checked complete 32-reset prospective actual native PPO task audit.
ALL original individual PhysX task outcomes required; no synthetic splices.
Statistical unit is task/reset, four ACK truths are correlated repeated measures.
"""
from __future__ import annotations
import argparse,hashlib,json,math,random
from pathlib import Path
from itertools import product
from collections import defaultdict
from statistics import mean

TASKS={"pull_cube":4100001,"stack_cube":4200001}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
ARMS=(A,B,C)
PROBES=("zero","x")
TRUTHS=tuple(range(4))
PROTO="research/ACTIVE_PROBE_TASK_ZERO_X_PREOUTCOME_20261010.json"
PROTO_BLOB="9cbe516f24de4c363eb4b6d5ec250d79e83a207a"
SOURCE_BLOB="2f2fc34f492bf6d2810b48193283e0347f6bdc93"

def paired_signflip_reset_p(deltas):
    nonzero=[float(x) for x in deltas if x]
    if len(nonzero)>20:raise ValueError("Exact signflip too many nonzero reset clusters")
    if not nonzero:return 1.
    observed=abs(sum(nonzero))
    wins=0
    for signs in product((-1,1),repeat=len(nonzero)):
        if abs(sum(x*s for x,s in zip(nonzero,signs)))>=observed-1e-9:wins+=1
    return wins/(2**len(nonzero))

def audit(directory):
    d=Path(directory)
    rows={}
    all_hash={}
    for task,start in TASKS.items():
        for chunk in range(4):
            sha_path=d/f"physx_probe_{task}_chunk{chunk}.sha256"
            if not sha_path.is_file():raise ValueError("Missing first-source SHA manifest "+str(sha_path))
            listed=sha_path.read_text().splitlines()
            manifest_entries={}
            for line in listed:
                digest,sep,filename=line.partition("  ")
                if not sep or len(digest)!=64 or filename in manifest_entries or Path(filename).name!=filename:
                    raise ValueError("Bad original shard SHA manifest")
                manifest_entries[filename]=digest
            filenames=[f"physx_probe_{task}_chunk{chunk}_truth{truth}_{p}.json" for truth in TRUTHS for p in PROBES]
            filenames.append(f"physx_probe_{task}_chunk{chunk}_provenance.json")
            if set(filenames)!=set(manifest_entries):raise ValueError("Original shard source manifest incomplete")
            for name in filenames:
                content=(d/name).read_bytes()
                if hashlib.sha256(content).hexdigest()!=manifest_entries[name]:
                    raise ValueError("Physical source SHA byte drift "+name)
                all_hash[name]=manifest_entries[name]
            provenance=json.loads((d/filenames[-1]).read_text())
            if (provenance["task"]!=task or provenance["chunk"]!=chunk
                or provenance["independent_reset_clusters"]!=4
                or provenance["all_native_robot_controller_worlds"]!=320
                or provenance["all_same_reset_true_ack_A_B_C_action_prefixes_confirmed"] is not True
                or len(provenance["arm_paired_outcomes"])!=4*4*3):
                raise ValueError("Physical matched source provenance incomplete")
            for truth in TRUTHS:
                for probe in PROBES:
                    name=f"physx_probe_{task}_chunk{chunk}_truth{truth}_{probe}.json"
                    body=json.loads((d/name).read_text())
                    if (body["schema"]!="new_frozen_task_zero_v_x_true_physx_v1"
                        or body["task"]!=task or body["chunk"]!=chunk
                        or body["fault_truth_index"]!=truth or body["probe"]!=probe
                        or body["original_source_git_blob"]!=SOURCE_BLOB
                        or body["preoutcome_protocol"]!=PROTO
                        or body["world_count"]!=40 or body["no_policy_retraining"] is not True
                        or body["source_original_reset_ids"]!=list(range(start+4*chunk,start+4*chunk+4))
                        or len(body["episodes"])!=4):
                        raise ValueError("Wrong source study membership / complete all-world count")
                    for row in body["episodes"]:
                        key=(task,int(row["seed"]),truth,probe)
                        if key in rows or row["seed"] not in body["source_original_reset_ids"]:
                            raise ValueError("Duplicate/non-preregistered reset/truth/probe")
                        if row["initial_source_physical_obs_sha256"] is None:
                            raise ValueError("Missing same-init source provenance")
                        for arm in ARMS:
                            if (type(row["success_once"].get(arm)) is not bool
                                or type(row["privileged_target_readback_decision_count"].get(arm)) is not int
                                or row["privileged_target_readback_decision_count"][arm] not in (0,1)
                                or row["public_motion_observation_cost_samples"].get(arm)!=(0 if arm==C else 2)):
                                raise ValueError("Invalid original task/read/public sample outcome")
                            ev={} if arm==C else row["public_t3_evidence"] if arm==A else row["same_sensor_posterior_evidence"]
                            if arm!=C and (type(ev.get("authorized")) is not bool
                                           or type(ev.get("wrong_confident")) is not bool
                                           or ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True):
                                raise ValueError("unverified or leaked audit only controller target")
                        rows[key]=row
    expected={(task,seed,truth,probe)
            for task,start in TASKS.items() for seed in range(start,start+16)
            for truth in TRUTHS for probe in PROBES}
    if set(rows)!=expected or len(rows)!=256:
        raise ValueError("Dropped/new physical task context")
    differences=defaultdict(list);detail=[]
    for task,start in TASKS.items():
        for seed in range(start,start+16):
            for truth in TRUTHS:
                z,x=(rows[(task,seed,truth,p)] for p in PROBES)
                if z["initial_source_physical_obs_sha256"]!=x["initial_source_physical_obs_sha256"]:
                    raise ValueError("Unmatched source reset before probe")
                for arm in ARMS:
                    zt,xt=(z["shared_neutral_probe_step4"][arm],x["shared_neutral_probe_step4"][arm])
                    if zt["native_six_dim_arm"]!=[0.]*6 or xt["native_six_dim_arm"]!=[.15,0.,0.,0.,0.,0.]:
                        raise ValueError("Physically executed t4 action not promised")
                    if abs(zt["audit_only_target_position_delta_m"])>5e-5 or abs(xt["audit_only_target_position_delta_m"]-.015)>5e-5:
                        raise ValueError("Verified target changed unlike registered action")
                    dsucc=int(x["success_once"][arm])-int(z["success_once"][arm])
                    differences[(task,seed,arm)].append(dsucc)
                    detail.append(dict(task=task,seed=seed,truth=truth,arm=arm,
                        zero_success=z["success_once"][arm],x_success=x["success_once"][arm],
                        success_difference=dsucc,
                        zero_privileged_reads=z["privileged_target_readback_decision_count"][arm],
                        x_privileged_reads=x["privileged_target_readback_decision_count"][arm],
                        zero_confident=None if arm==C else bool((z["public_t3_evidence"] if arm==A else z["same_sensor_posterior_evidence"])["authorized"]),
                        x_confident=None if arm==C else bool((x["public_t3_evidence"] if arm==A else x["same_sensor_posterior_evidence"])["authorized"]),
                        zero_wrong=False if arm==C else bool((z["public_t3_evidence"] if arm==A else z["same_sensor_posterior_evidence"])["wrong_confident"]),
                        x_wrong=False if arm==C else bool((x["public_t3_evidence"] if arm==A else x["same_sensor_posterior_evidence"])["wrong_confident"])))
    summaries={}
    for task,start in TASKS.items():
        summaries[task]={}
        for arm in ARMS:
            rr=[r for r in detail if r["task"]==task and r["arm"]==arm]
            ds=[sum(differences[(task,seed,arm)]) for seed in range(start,start+16)]
            summaries[task][arm]=dict(n_unique_resets=16,n_correlated_ACK_truths=64,
                zero_success=sum(r["zero_success"] for r in rr),
                x_success=sum(r["x_success"] for r in rr),
                x_only_success=sum(r["x_success"] and not r["zero_success"] for r in rr),
                zero_only_success=sum(r["zero_success"] and not r["x_success"] for r in rr),
                zero_getters=sum(r["zero_privileged_reads"] for r in rr),
                x_getters=sum(r["x_privileged_reads"] for r in rr),
                zero_wrong=sum(r["zero_wrong"] for r in rr),
                x_wrong=sum(r["x_wrong"] for r in rr),
                x_minus_zero_success_cluster_differences=ds,
                cluster_paired_signflip_two_sided_exploratory_p=paired_signflip_reset_p(ds))
    return dict(status="REAL_COMPLETED_NEW_FREEZE_PPO_TASK_SOURCE_AUDITED",
        preregistered_protocol_blob=PROTO_BLOB,
        physically_executed_original_controller_worlds=2560,
        new_independent_reset_clusters=32,
        four_actual_ACK_truths_per_reset=4,
        probe_options=2,
        matched_original_PPO_task_cells=256,
        official_task_endpoint_not_source_only=True,
        original_shard_file_sha256=all_hash,
        by_task=summaries,
        all_full_actual_PPO_task_outcomes=detail,
        interpretation="No policy retraining, no robot-hardware test, no prospectively powered conditional authority risk guarantee; 32 iid resets not 256 contexts.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input-dir",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    out=audit(args.input_dir)
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True))
    print("ORIGINAL_ACTIVE_PROBE_FULL_TASK_AUDIT",json.dumps({
        "physical_worlds":out["physically_executed_original_controller_worlds"],
        "n_resets":out["new_independent_reset_clusters"],
        "by_task":out["by_task"]},sort_keys=True))
