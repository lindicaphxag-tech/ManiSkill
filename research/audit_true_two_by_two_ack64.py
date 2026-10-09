"""Separate original eight-shard/64-population true native 2x2 ACK PhysX auditor.

No simulator call. Never reconstruct physics from JSON labels; all results rely
on first full native source runner and honest audit-only target state records.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from research.run_true_two_by_two_ack64 import (
    PUBLIC,FIXED,SELECTIVE,HELD,audit_eight,seeds,
    PHYSICS_BLOB,REG_BLOB
)

def complete(folder:Path):
    wanted={f"true_double_{task}_chunk{chunk}_{kind}.json"
            for task in ("pull_cube","stack_cube") for chunk in range(4)
            for kind in ("original8","audit")}
    present={p.name for p in folder.glob("true_double_*.json")}
    if wanted!=present:raise ValueError(f"Missing/non-original PhysX source rows: {wanted-present}; extra: {present-wanted}")
    rows=[];by_task={}
    for task in ("pull_cube","stack_cube"):
        original=[]
        for chunk in range(4):
            f=folder/f"true_double_{task}_chunk{chunk}_original8.json"
            data=json.loads(f.read_text())
            expected=audit_eight(data,task,chunk)
            expected.update(schema="actual_true_two_by_two_physx_shard_audit_v1",
                  exact_original_physics_source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
                  source_native_runner_blob=PHYSICS_BLOB,prereg_blob=REG_BLOB)
            saved=json.loads((folder/f"true_double_{task}_chunk{chunk}_audit.json").read_text())
            if expected!=saved:
                raise ValueError(f"Independent source rows disagree: {task} chunk={chunk}")
            original.extend(expected["per_original_reset"])
        if len(original)!=32 or [r["seed"] for r in original]!=[z for ch in range(4) for z in seeds(task,ch)]:
            raise ValueError("Deleted or duplicated original seed rows")
        strong_sum={"success":sum(int(r["strong_task_success"]) for r in original),
                    "reads":sum(r["strong_private_reads"] for r in original)}
        public_sum={"success":sum(int(r["public_task_success"]) for r in original),
                    "reads":sum(r["public_private_reads"] for r in original)}
        fixed_sum={"success":sum(int(r["fixed_t5_success"]) for r in original),
                   "reads":sum(r["fixed_private_reads"] for r in original)}
        strata={}
        for two in ((False,False),(False,True),(True,False),(True,True)):
            sub=[r for r in original if (r["physical_t2_applied"],r["physical_t3_applied"])==two]
            if len(sub)!=8:raise ValueError(f"No balanced four real physical truths: {task} {two} {len(sub)}")
            strata["t2_"+("A" if two[0] else "H")+"_t3_"+("A" if two[1] else "H")]={
                "n":len(sub),"new_success":sum(int(r["public_task_success"]) for r in sub),
                "strong_success":sum(int(r["strong_task_success"]) for r in sub),
                "fixed_success":sum(int(r["fixed_t5_success"]) for r in sub),
                "public_private_reads":sum(r["public_private_reads"] for r in sub),
                "strong_private_reads":sum(r["strong_private_reads"] for r in sub),
                "public_unique":sum(int(r["public_unique"]) for r in sub),
                "wrong_confident":sum(int(r["wrong_confident"]) for r in sub)}
        pairing={
            "both":sum(r["public_task_success"] and r["strong_task_success"] for r in original),
            "neither":sum(not r["public_task_success"] and not r["strong_task_success"] for r in original),
            "new_only":sum(r["public_task_success"] and not r["strong_task_success"] for r in original),
            "strong_only":sum(not r["public_task_success"] and r["strong_task_success"] for r in original)}
        by_task[task]={"original_reset_states":32,"native_physx_controller_worlds":288,
                       "new":public_sum,"strong":strong_sum,"fixed":fixed_sum,
                       "paired":pairing,"physical_truth_strata":strata}
        rows.extend(original)
    if len(rows)!=64 or len(set((r["task"],r["seed"]) for r in rows))!=64:
        raise ValueError("Full 64 reset states are mandatory")
    totals={"new":{"success":sum(v["new"]["success"] for v in by_task.values()),
                   "private_reads":sum(v["new"]["reads"] for v in by_task.values())},
            "strong":{"success":sum(v["strong"]["success"] for v in by_task.values()),
                      "private_reads":sum(v["strong"]["reads"] for v in by_task.values())},
            "fixed":{"success":sum(v["fixed"]["success"] for v in by_task.values()),
                     "private_reads":sum(v["fixed"]["reads"] for v in by_task.values())}}
    pairs={key:sum(x["paired"][key] for x in by_task.values())
           for key in ("both","neither","new_only","strong_only")}
    return {"schema":"true_two_by_two_nonzero_real_native_physx_64_full_audit_v1",
            "preregistration_git_blob":REG_BLOB,
            "original_unchanged_physics_runner_git_blob":PHYSICS_BLOB,
            "physical_worlds":576,"original_reset_states":64,
            "full_two_by_two_applied_held_truth_strata":True,
            "four_true_physically_nonzero_t3_events_by_seed_mod4":True,
            "neutral_probe_cost_paid_for_all_undone_worlds":True,
            "not_actual_network_packet_loss_or_hardware_safety":True,
            "owner_operated_no_independent_lab":True,
            "by_task":by_task,"paired":pairs,"total_outcomes":totals,
            "all_original_rows":rows,
            "public_identified_complete_pose_history":sum(r["public_unique"] for r in rows),
            "wrong_confident_history_identifications":sum(r["wrong_confident"] for r in rows)}

def main():
    p=argparse.ArgumentParser();p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    result=complete(a.source_dir)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("REAL_FOUR_TRUTH_NONZERO_64_FULL_SOURCE_AUDIT",
          json.dumps({k:result[k] for k in ("physical_worlds","original_reset_states",
                          "total_outcomes","paired","public_identified_complete_pose_history",
                          "wrong_confident_history_identifications")},sort_keys=True))

if __name__=="__main__":main()
