"""Independent full original source audit, no simulation, no experiment tuning."""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from research.run_sequential_two_probe_new64 import (
    SINGLE,DUAL,FIXED,SELECTIVE,HELD,PROTOCOL_BLOB,
    CHECKPOINT,START,TASKS,validate_source,seeds_for)

def verify(directory):
    wanted={f"sequential_two_probes_{task}_chunk{chunk}_{suffix}.json"
            for task in TASKS for chunk in range(4)
            for suffix in ("original8","audit")}
    present={x.name for x in directory.glob("sequential_two_probes_*.json")}
    if wanted!=present:
        raise ValueError(f"Physical original source shards missing/extra: {wanted-present} / {present-wanted}")
    rows=[]
    sha={}
    for task in TASKS:
        for chunk in range(4):
            originals=directory/f"sequential_two_probes_{task}_chunk{chunk}_original8.json"
            audit_file=directory/f"sequential_two_probes_{task}_chunk{chunk}_audit.json"
            raw=originals.read_bytes()
            d=json.loads(raw)
            calc=validate_source(d,task,seeds_for(task,chunk))
            snapshot=json.loads(audit_file.read_text())
            if (snapshot.get("original_raw_sha256")!=hashlib.sha256(raw).hexdigest()
                or any(snapshot.get(k)!=v for k,v in calc.items())):
                raise ValueError("Unverifiable original PhysX shard / author source audit")
            sha[originals.name]=hashlib.sha256(raw).hexdigest()
            sha[audit_file.name]=hashlib.sha256(audit_file.read_bytes()).hexdigest()
            rows.extend(calc["original_task_rows"])
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Original prospective population not 64 distinct paired task seeds")
    contrasts={}
    for combo in ("AA","AH","HA","HH"):
        pair=[r for r in rows if r["combo"]==combo]
        if len(pair)!=16:
            raise ValueError("Full physical executed/held joint ACK truths not balanced")
        contrasts[combo]={k:sum(int(z[k]) for z in pair) for k in (
            "one_success","two_success","gate_success","fixed_success","held_success",
            "one_reads","two_reads","gate_reads","fixed_reads",
            "one_confident","two_confident","one_wrong","two_wrong")}
        contrasts[combo]["n"]=16
    task_results={}
    for task in TASKS:
        task_rows=[z for z in rows if z["task"]==task]
        task_results[task]={
            "n":32,
            "one_success":sum(z["one_success"] for z in task_rows),
            "two_success":sum(z["two_success"] for z in task_rows),
            "strong_success":sum(z["gate_success"] for z in task_rows),
            "two_read_total":sum(z["two_reads"] for z in task_rows),
            "one_read_total":sum(z["one_reads"] for z in task_rows),
            "two_wrong":sum(z["two_wrong"] for z in task_rows),
            "one_wrong":sum(z["one_wrong"] for z in task_rows)}
    totals={k:sum(int(r[k]) for r in rows) for k in (
         "one_success","two_success","gate_success","fixed_success","held_success",
         "one_reads","two_reads","gate_reads","fixed_reads","one_confident",
         "two_confident","one_wrong","two_wrong","one_public_samples","two_public_samples")}
    paired={k:0 for k in ("both","dual_only","single_only","neither")}
    for z in rows:
        key=("both" if z["two_success"] and z["one_success"]
             else "dual_only" if z["two_success"] else
             "single_only" if z["one_success"] else "neither")
        paired[key]+=1
    return {"schema":"independent_source_64_sequential_two_probe_vs_one_physx_v1",
            "genuine_original_reset_states":64,
            "actual_independently_physically_stepped_policy_controller_worlds":640,
            "joint_actual_execution_truth_both_mixed":True,
            "source_per_file_SHA256":sha,
            "registered_protocol_blob":PROTOCOL_BLOB,
            "frozen_PPO_no_retraining":True,
            "total":totals,
            "by_task":task_results,
            "four_joint_truth_strata":contrasts,
            "paired_dual_vs_single_task":paired,
            "all_original_source_episode_records":rows,
            "two_known_delivered_neutral_steps_per_still_active_world":True,
            "some_old_controllers_may_refuse_before_neutral_steps_and_are_not_fabricated":True,
            "additional_public_XYZ_samples_explicit":True,
            "empirical_motion_calibration_is_not_physics_attestation":True,
            "not_real_network_packet_loss_or_external_lab_or_hardware_collision_safety":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    res=verify(a.source_dir)
    a.output.write_text(json.dumps(res,sort_keys=True,indent=2)+"\n")
    print("INDEPENDENT_FULL_64_TWO_PUBLIC_PROBE_REAL_PHYSX",json.dumps({
        "totals":res["total"],"strata":res["four_joint_truth_strata"],
        "paired":res["paired_dual_vs_single_task"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
