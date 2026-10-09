"""Dependency-free strict auditor: all 16 original Panda/xArm6 native PhysX rows.
No "successful" robot substitution or excluding non-distinct target outcomes.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path

FIRST={"panda":420001,"xarm6_robotiq":430001}
ORIGINAL_PROTOCOL="research/CROSS_EMBODIMENT_ACK_PREOUTCOME_V1.json"
KEYS=("linf_m","l2_m","so3_rad")

def audit(d,robot,chunk):
    seeds=list(range(FIRST[robot]+chunk*4,FIRST[robot]+chunk*4+4))
    if (d.get("schema")!="cross_embodiment_stateful_action_observability_physics_v1"
        or d.get("protocol")!=ORIGINAL_PROTOCOL
        or d.get("robot")!=robot or d.get("task")!="PickCube-v1"
        or d.get("control")!="pd_ee_target_delta_pose"
        or d.get("real_physx_cpu") is not True
        or d.get("all_seeds")!=seeds or d.get("done") is not True
        or d.get("author_executed_only") is not True
        or d.get("external_independent_replication") is not False
        or d.get("not_policy_transfer_or_task_success_claim") is not True):
        raise ValueError("Evidence identity, source task or external provenance inconsistent")
    rows=d.get("rows")
    if not isinstance(rows,list) or len(rows)!=4 or [r.get("seed") for r in rows]!=seeds:
        raise ValueError("All four genuine physical episodes required")
    nonzero=0;distances=[]
    for row in rows:
        if (row.get("robot_uid")!=robot or row.get("control_mode")!="pd_ee_target_delta_pose"
            or row.get("task")!="PickCube-v1" or row.get("real_physx_cpu") is not True
            or row.get("source_policy_trained") is not False
            or row.get("native_command_ack_visible")!="unknown"
            or row.get("both_private_target_reads_for_audit_only") is not True
            or row.get("xarm6_is_not_a_Panda_relabel") is not (robot=="xarm6_robotiq")):
            raise ValueError("Robot body or truthful observer state identity was altered")
        # Actual physical robot controller ABI must differ; falsified
        # Panda labels can never be counted as an xArm6 experiment.
        expected_keys=(["arm","gripper"] if robot=="panda"
                       else ["arm","gripper_active","gripper_passive"])
        act_keys=row.get("actual_action_controller_keys",{})
        if (set(act_keys)!={"held","applied"} or
            any(list(act_keys[t])!=expected_keys for t in ("held","applied"))):
            raise ValueError("Genuine controller joint/gripper ABI does not match declared robot")
        cmds=row.get("native_requested_commands")
        if (not isinstance(cmds,list) or len(cmds)!=6 or len(cmds[2])!=6
            or cmds[2]==[0.]*6 or cmds[3]!=[0.]*6):
            raise ValueError("Not the frozen one-fault and one-zero-probe commands")
        if not isinstance(row.get("pair_reset_l2_m"),(float,int)) or not 0<=row["pair_reset_l2_m"]<=1e-5:
            raise ValueError("Matched real morphology pose reset does not agree")
        if set(row.get("official_task_success_by_truth",{}))!={"applied","held"}:
            raise ValueError("Unreported official native task flags")
        if any(type(z) is not bool for z in row["official_task_success_by_truth"].values()):
            raise ValueError("Official task flags cannot be misreported")
        residuals=row.get("commanded_target_residual_by_step",{})
        if set(residuals)!={"held","applied"} or any(len(v)!=6 for v in residuals.values()):
            raise ValueError("Twelve actual after-physics target-audit steps required")
        for truth,arr in residuals.items():
            for err in arr:
                if set(err)!=set(KEYS):
                    raise ValueError("Non-exact audit has incomplete target fields")
                if any(type(err[k]) not in (int,float) or not math.isfinite(err[k]) or err[k]<0 for k in KEYS):
                    raise ValueError("Invalid native target reconstruction error")
                if err["linf_m"]>1e-4 or err["so3_rad"]>1e-3:
                    raise ValueError("Claimed target-history prediction disproven by actual native controller")
            for key,base in (("linf_m","commanded_target_residual_max_linf_m_"),
                             ("so3_rad","commanded_target_residual_max_so3_rad_")):
                if not math.isclose(max(z[key] for z in arr),row.get(base+truth,float("nan")),abs_tol=1e-10):
                    raise ValueError("Wrong max original physical target-reconstruction error")
        divergence=row.get("fault_divergence")
        if not isinstance(divergence,dict) or set(divergence)!=set(KEYS):
            raise ValueError("Actual target history branch difference not logged")
        if any(type(divergence[k]) not in (float,int) or not math.isfinite(divergence[k]) or divergence[k]<0 for k in KEYS):
            raise ValueError("NaN/invalid target separation")
        distinct=(divergence["l2_m"]>1e-5 or divergence["so3_rad"]>1e-5)
        if row.get("fault_target_distinct") is not distinct:
            raise ValueError("False controller memory history-label claim")
        nonzero+=distinct
        p=row.get("probe",{})
        if (p.get("private_target_reads_used_in_inference")!=0 or p.get("probe_native_arm_command")!=[0.]*6):
            raise ValueError("Privileged observer contamination or missing matched zero-probe")
        for k in ("achieved_ee_xyz_applied","achieved_ee_xyz_held"):
            if len(p.get(k,[]))!=3 or any(not isinstance(v,(float,int)) or not math.isfinite(v) for v in p[k]):
                raise ValueError("Missing physically achieved EE pose on actual robot")
        actual_sep=sum((x-y)**2 for x,y in zip(p["achieved_ee_xyz_applied"],p["achieved_ee_xyz_held"]))**.5
        if not math.isclose(actual_sep,p.get("achieved_ee_branch_distance_m",float("nan")),abs_tol=1e-9):
            raise ValueError("Fake or inconsistent observed physical probe separation")
        distances.append(actual_sep)
    if d.get("nonzero_target_divergence")!=nonzero or len(d.get("probe_achieved_ee_separation_m",[]))!=4:
        raise ValueError("Aggregate incorrect or cherry-picked")
    if any(abs(a-b)>1e-9 for a,b in zip(distances,d["probe_achieved_ee_separation_m"])):
        raise ValueError("Per-sample physical separation summary tampered")
    return {"n":4,"robot":robot,"target_history_divergence":nonzero,
            "real_achieved_probe_distance_m":distances}

def all_evidence(folder):
    expected={f"cross_robot_ack_{robot}_chunk{c}_original4.json" for robot in FIRST for c in (0,1)}
    paths=list(folder.glob("cross_robot_ack_*_original4.json"))
    if len(paths)!=4 or {p.name for p in paths}!=expected:
        raise ValueError("Exactly FOUR completed Panda/xArm6 source shard JSONs required")
    r={}
    for robot in FIRST:
        for chunk in (0,1):
            name=f"cross_robot_ack_{robot}_chunk{chunk}_original4.json"
            r[f"{robot}:{chunk}"]=audit(json.loads((folder/name).read_text()),robot,chunk)
    return {"schema":"cross_embodiment_unknown_ack_original16_full_audit_v1",
            "source_denominator":16,"robots":list(FIRST),
            "not_policy_transfer":True,"not_external_independent_research":True,
            "results":r}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=all_evidence(a.input_dir)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("CROSS_ROBOT_FULL_SOURCE_AUDIT",json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
