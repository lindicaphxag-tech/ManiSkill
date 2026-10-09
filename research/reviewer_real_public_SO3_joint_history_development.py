"""Original 16 true-PhysX frozen PPO public-SO3 developmental identifiability frontier.

Do not confuse this source-only label-assisted SCIENTIFIC DEVELOPMENT
ANALYSIS with a new physically executed controller intervention or
held-out prospective success. All decisions use public XYZ and public
quaternion arc residuals only; the hidden real native target label is used
AFTER selection to grade accuracy, NEVER as inference input.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import defaultdict
from pathlib import Path

TASKS=("pull_cube","stack_cube")
PUBLIC="fault_public_t3_fourhistory_or_t4_query"
SCORE="fault_strong_tuned_score_060_or_query"
FIRST={"pull_cube":2040001,"stack_cube":2050001}
THRESHOLDS=(0.002,0.005,0.01,0.02,0.04,0.08,0.16)

def original_source(source_dir:Path):
    from research.run_so3_public_signal_pilot import audit_raw
    episodes=[]
    names={}
    for task in TASKS:
        p=source_dir/f"so3_physical_{task}_original8.json"
        raw=p.read_bytes()
        file=json.loads(raw)
        summary=audit_raw(file,task)
        if summary["n_original_resets"]!=8:raise ValueError("Eight required physically stepped task resets per task")
        names[p.name]=hashlib.sha256(raw).hexdigest()
        for i,trial in enumerate(file["episodes"]):
            if trial["seed"]!=FIRST[task]+i:raise ValueError("Missing original physically reset seed")
            exposures={}
            for arm,event_key in ((PUBLIC,"public_t3_evidence"),(SCORE,"strong_score_060_evidence")):
                ev=trial.get(event_key,{})
                if ev.get("so3_public_samples_charged") is not None:
                    n=ev["physical_candidate_count"]
                    xyz=ev.get("candidate_residuals_m")
                    so3=ev.get("so3_public_geodesic_to_candidate_arc_rad")
                    truth=ev.get("audit_only_true_candidate_indices")
                    if any(not isinstance(v,list) or len(v)!=n for v in (xyz,so3)) or not isinstance(truth,list):
                        raise ValueError("Inconsistent original external frozen policy source SO3 evidence")
                    if any(not math.isfinite(x) or x<0 for x in xyz+so3):
                        raise ValueError("Illegal original public evidence residual")
                    if ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True or ev.get("so3_only_feasibility_no_decision_use") is not True:
                        raise ValueError("Original PPO actions could have been influenced by postphysical labels")
                    exposures[arm]={"n":n,"xyz":xyz,"so3":so3,"truth":truth,
                                    "old_epsilon":ev["prior_training_epsilon_m"],
                                    "old_authorized":ev.get("authorized"),
                                    "old_selected":ev.get("selected_candidate_index"),
                                    "old_wrong":ev.get("wrong_confident")}
                else:exposures[arm]=None
            episodes.append({"task":task,"seed":trial["seed"],
                             "original_official_success":trial["success_once"].get(PUBLIC),
                             "original_getter_reads":trial["privileged_target_readback_decision_count"].get(PUBLIC),
                             "source_public_history":exposures[PUBLIC],
                             "source_tuned_score_history":exposures[SCORE],
                             "ACK_physical_reference_exposed":len(trial.get("faults",{}).get(PUBLIC,[]))==2})
    if len(episodes)!=16 or len({(r["task"],r["seed"]) for r in episodes})!=16:
        raise ValueError("Not genuine complete original sixteen")
    return names,episodes

def public_joint_gate(ev,so3_radius):
    """PUBLIC-only finite SE3 history feasibility; no private target or truth."""
    if ev is None:return (False,None,"no_actuation_no_information")
    # Both are genuine measurements from the same achieved end-effector pose;
    # quaternion readings are NOT an independent device.
    feasible=[i for i,(px,rot) in enumerate(zip(ev["xyz"],ev["so3"]))
              if px<=ev["old_epsilon"]+1e-12 and rot<=so3_radius+1e-12]
    if len(feasible)==1:
        return (True,feasible[0],"unique_full_SE3_joint_xyz_and_quaternion")
    return (False,None,"none_or_multiple_joint_feasible")

def frontier(episodes,source_sha):
    grid={}
    for eps_rot in THRESHOLDS:
        pertask={}
        for task in TASKS:
            original=[e for e in episodes if e["task"]==task]
            decisions=[]
            for r in original:
                e=r["source_public_history"]
                aut,sel,_=public_joint_gate(e,eps_rot)
                decisions.append({"seed":r["seed"],"full_two_ACK_exposed":r["ACK_physical_reference_exposed"],
                    "joint_authorized":aut,"selected":sel,
                    "true_audit_only_target_index_is_correct":sel in e["truth"] if e is not None and aut else None,
                    "previous_xyz_only_public_authorized":e["old_authorized"] if e is not None else None,
                    "different_controller_trajectory_NOT_REEXECUTED":True})
            pertask[task]={
                "original_n":8,
                "physically_observed_both_ACKs":sum(x["full_two_ACK_exposed"] for x in decisions),
                "joint_authorities":sum(x["joint_authorized"] for x in decisions),
                "wrong_confident_joint_decisions":sum(x["joint_authorized"] and not x["true_audit_only_target_index_is_correct"] for x in decisions),
                "would_query_when_original_probe_was_observed":sum(not x["joint_authorized"] for x in decisions),
                "old_xyz_only_authorities_on_same_REAL_physics":sum(x["previous_xyz_only_public_authorized"] is True for x in decisions),
                "case_by_case":decisions
            }
        grid[str(eps_rot)]={"max_public_SO3_arc_residual_rad":eps_rot,
                            "per_task":pertask,
                            "total_joint_authorities":sum(z["joint_authorities"] for z in pertask.values()),
                            "total_wrong":sum(z["wrong_confident_joint_decisions"] for z in pertask.values())}
    return {"schema":"16_genuine_native_PhysX_public_SO3_joint_SE3_history_DEVELOPMENT_ONLY_v1",
            "original_physx_first_source":"https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37931907253",
            "original_task_reset_n":len(episodes),
            "real_native_controller_world_instances":160,
            "original_source_SHA256":source_sha,
            "same_real_physical_quaternion_and_XYZ_both_measured":True,
            "quaternion_is_not_an_independent_sensor":True,
            "per_source_pilot_quaternion_was_NOT_used_for_any_task_decision":True,
            "source_only_risk_frontier_NOT_a_fresh_physically_executed_counterfactual_controller":True,
            "SO3_threshold_selected_on_this_source_is_POSTHOC_DEVELOPMENT_ONLY":True,
            "threshold_sensitivity":grid,
            "conclusion_boundary":"No SO3 historical label-aware performance may be claimed as held-out test. Need one frozen SO3 radius chosen HERE and truly new native PPO source trials with actual SO3 gate and counted fallbacks."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    sha,episodes=original_source(args.source_dir)
    d=frontier(episodes,sha)
    args.output.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("PHYSICALLY_MEASURED_PUBLIC_SO3_DEVELOPMENT_FRONTIER",json.dumps({
        "n":d["original_task_reset_n"],
        "grid":{k:{"authorized":v["total_joint_authorities"],"wrong":v["total_wrong"],
                    "tasks":{t:{"authorities":z["joint_authorities"],"wrong":z["wrong_confident_joint_decisions"]}
                             for t,z in v["per_task"].items()}}
                for k,v in d["threshold_sensitivity"].items()}},sort_keys=True))
if __name__=="__main__":main()
