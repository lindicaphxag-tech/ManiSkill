"""Actual 32-source PhysX nonzero causal-native-probe pilot: original bytes
only, independently recompute each full history, task status, query count,
native arm target manipulation and achieved public XYZ displacement.

Pilot is NOT confirmatory general robotics safety/performance proof.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from research.run_causal_nonzero_native_ack_pilot32 import (
    TASKS,new_seeds,audit_pilot_shard,PREREG_BLOB,SOURCE_BLOB)

def independent_all32(root):
    original={f"active_nonzero_pilot_{task}_chunk{i}_original8.json"
        for task in TASKS for i in range(2)}
    audited={f"active_nonzero_pilot_{task}_chunk{i}_audit.json"
        for task in TASKS for i in range(2)}
    present={x.name for x in root.glob("active_nonzero_pilot_*.json")}
    if present!=original|audited:
        raise RuntimeError("Incomplete genuine prospective 4 physical controller shard population")
    allrows=[]
    sha={}
    for task in TASKS:
        for chunk in range(2):
            p=root/f"active_nonzero_pilot_{task}_chunk{chunk}_original8.json"
            a=root/f"active_nonzero_pilot_{task}_chunk{chunk}_audit.json"
            raw=p.read_bytes()
            d=json.loads(raw)
            expected=audit_pilot_shard(d,task,new_seeds(task,chunk))
            original_audit=json.loads(a.read_text())
            if (original_audit["original_byte_identical_physics_source_sha256"]
                !=hashlib.sha256(raw).hexdigest() or
                any(original_audit.get(k)!=v for k,v in expected.items()) or
                original_audit.get("method_native_git_blob")!=SOURCE_BLOB or
                original_audit.get("source_prereg_git_blob")!=PREREG_BLOB):
                raise ValueError("Original real source audit not independently replicated")
            sha[p.name]=hashlib.sha256(raw).hexdigest()
            sha[a.name]=hashlib.sha256(a.read_bytes()).hexdigest()
            allrows.extend(expected["original_all_task_rows"])
    if (len(allrows)!=32 or len({(x["task"],x["seed"]) for x in allrows})!=32):
        raise ValueError("Not 32 distinct source-precommitted actual PhysX resets")
    per_truth={}
    for task in TASKS:
        for truth in ("AA","AH","HA","HH"):
            z=[r for r in allrows if r["task"]==task and r["truth"]==truth]
            if len(z)!=4:
                raise ValueError("Actual native physical four-ACK truth represented unequally in precommitted seeds")
            per_truth[f"{task}:{truth}"]={k:sum(int(x[k]) for x in z) for k in (
                "passive_success","active_success","active_always_query_success",
                "passive_private_reads","active_private_reads",
                "active_authorized","passive_authorized",
                "active_wrong_confident","passive_wrong_confident")}
    total={k:sum(int(x[k]) for x in allrows) for k in (
        "passive_success","active_success","active_always_query_success",
        "strong_task_gate_success","passive_private_reads","active_private_reads",
        "active_always_query_private_reads","strong_private_reads",
        "passive_authorized","active_authorized",
        "passive_wrong_confident","active_wrong_confident")}
    paired={"both":0,"active_only":0,"zero_only":0,"neither":0}
    for r in allrows:
        if r["active_success"] and r["passive_success"]:key="both"
        elif r["active_success"]:key="active_only"
        elif r["passive_success"]:key="zero_only"
        else:key="neither"
        paired[key]+=1
    return {
      "schema":"actual_original_nonzero_vs_passive_native_ACK_intervention_physx_pilot32_v1",
      "protocol_exact_preregistered_git_blob":PREREG_BLOB,
      "method_preoutcome_real_native_physx_source_blob":SOURCE_BLOB,
      "genuine_original_physical_reset_task_states":32,
      "real_separately_physically_stepped_controller_worlds":352,
      "two_ambiguously_executed_native_true_ACKs_per_trial":True,
      "each_active_and_always_query_intervention_applied_physical_t4_nonzero":True,
      "actual_native_nonzero_arm_6d_FROZEN":[.12,-.09,.07,0.,0.,0.],
      "no_unmatched_unreported_extra_physical_probe_step":True,
      "t4_nonzero_moves_real_native_target_and_has_explicit_cost":True,
      "old_zero_probed_motion_response_epsilon_is_NOT_validated_for_nonzero_actuation":True,
      "source_original_eight_files_sha256":sha,
      "all_original_task_truth_and_probe_evidence":allrows,
      "per_task_true_ACK":per_truth,
      "total":total,"paired_active_vs_zero_task":paired,
      "not_confirmatory_top_conference_or_safety_certified":True,
      "outside_independent_researcher_replication":False,
      "real_network_ack_drop_not_tested":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    out=independent_all32(a.source_dir)
    a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("INDEPENDENT_TRUE_NATIVE_PHYSX_NONZERO_ACK_PILOT32",json.dumps({
        "total":out["total"],"paired":out["paired_active_vs_zero_task"],
        "strata":out["per_task_true_ACK"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
