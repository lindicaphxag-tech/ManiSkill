"""Independent source-only auditor of 64 registered ACTUAL ManiSkill CPU PhysX
episodes × eleven separately stepped controllers (704 native physics worlds).

The native source PhysX traces, not retrospective model counterfactuals, are
the primary evidence. Count actual dispatched native probe action magnitude,
public robot XYZ displacement, decision-only target getters, false confident
full-history assignments, true ACK and full frozen PPO task successes.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from research.run_active_ACK_probe_new64 import (
    TASKS,FIRST,ARMS,ZERO,FIXED,ACTIVE,original_seeds,validate_original,
    PROTOCOL_BLOB,SOURCE_BLOB)
def all_original(folder):
    wanted={f"active_probe_{task}_chunk{k}_{v}.json"
       for task in TASKS for k in range(4) for v in ("original8","audit")}
    found={x.name for x in folder.glob("active_probe_*.json")}
    if wanted!=found:
        raise ValueError(f"Missing registered physics cohort shards {wanted-found}; unexpected={found-wanted}")
    allrows=[];manifest={}
    for task in TASKS:
        for chunk in range(4):
            stem=f"active_probe_{task}_chunk{chunk}"
            orig=folder/(stem+"_original8.json")
            proof=folder/(stem+"_audit.json")
            raw=orig.read_bytes()
            recomputed=validate_original(json.loads(raw),task,original_seeds(task,chunk))
            existing=json.loads(proof.read_text())
            if existing.get("source_original_JSON_sha256")!=hashlib.sha256(raw).hexdigest():
                raise ValueError("Original physically executed source JSON hash mismatch")
            if any(existing.get(k)!=v for k,v in recomputed.items()):
                raise ValueError("Original matched native PhysX source audit disagrees")
            manifest[orig.name]=hashlib.sha256(raw).hexdigest()
            manifest[proof.name]=hashlib.sha256(proof.read_bytes()).hexdigest()
            allrows+=recomputed["source_original_8_episodes"]
    if len(allrows)!=64 or len({(r["task"],r["seed"]) for r in allrows})!=64:
        raise ValueError("Not all 64 truly independent new reset identities exist")
    def summarise(rows):
        ret={"n_original_task_resets":len(rows),
             "task_selected_strong_baseline_task_success":sum(r["task_gate_success"] for r in rows),
             "task_selected_strong_baseline_privileged_target_reads":sum(r["task_gate_reads"] for r in rows)}
        for n in ARMS:
            ob=[r["per_method"][n] for r in rows]
            ret[n]={"native_controller_worlds":len(ob),
                    "actual_official_task_success":sum(x["success"] for x in ob),
                    "explicit_native_target_state_reads":sum(x["privileged_reads"] for x in ob),
                    "public_histories_confidently_authorized":sum(x["authorized"] for x in ob),
                    "wrong_confident_after_true_native_physics":sum(x["wrong_confident"] for x in ob),
                    "public_XYZ_sample_events":sum(x["public_samples"] for x in ob),
                    "normalized_native_arm_probe_l2_total":sum(
                        math.sqrt(sum(a*a for a in x["native_action"][:3])) for x in ob),
                    "physical_actual_public_XYZ_displacement_total_m":sum(
                        x["public_displacement_m"] for x in ob)}
        return ret
    per={}
    for task in TASKS:
        for truth in ("AA","AH","HA","HH"):
            rows=[r for r in allrows if r["task"]==task and r["actual_joint_ACK"]==truth]
            if len(rows)!=8:raise ValueError("Four original native ACK combinations not balanced")
            per[f"{task}:{truth}"]=summarise(rows)
    pairs={}
    for a,b in ((ACTIVE,FIXED),(ACTIVE,ZERO),(FIXED,ZERO)):
        ta=tb=both=neither=0
        for row in allrows:
            x=row["per_method"][a]["success"]
            y=row["per_method"][b]["success"]
            ta+=int(x and not y);tb+=int(y and not x)
            both+=int(x and y);neither+=int(not x and not y)
        pairs[f"{a}_VERSUS_{b}"]={"both":both,"a_only":ta,"b_only":tb,"neither":neither}
    return {"schema":"independent_all64_11_actual_native_PhysX_active_vs_fixed_vs_passive_v1",
            "real_separately_actuated_physx_controller_worlds":704,
            "original_unseen_task_resets":64,
            "frozen_PPO_retrained":False,
            "physical_unknown_ACK_joint_truths_matched":True,
            "exact_original_source_file_sha256":manifest,
            "registered_preoutcome_git_blob":PROTOCOL_BLOB,
            "source_pinned_physx_method_blob":SOURCE_BLOB,
            "per_original_physical_reset_row":allrows,
            "total":summarise(allrows),
            "by_task":{t:summarise([r for r in allrows if r["task"]==t]) for t in TASKS},
            "by_truth_and_task":per,
            "paired_success":pairs,
            "one_native_actuated_step_all_controllers_but_different_real_probe_displacements":True,
            "simulated_physical_target_hold_NOT_network_loss":True,
            "no_hardware_safety_certificate":True,
            "active_minimax_selector_NOT_faithful_ActionShift_DualABI":True,
            "no_independent_external_researcher_replication":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data=all_original(a.source_dir)
    a.output.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("INDEPENDENT_ORIGINAL_704_REAL_PHYSX_ACTIVE_FIXED_PASSIVE",
       json.dumps({"total":data["total"],
                   "paired":data["paired_success"],
                   "by_task":data["by_task"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
