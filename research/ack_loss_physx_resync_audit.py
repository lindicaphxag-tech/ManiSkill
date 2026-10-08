"""Independent full denominator audit of actual simulated lost-ACK/recovery episodes."""
import json
import math
import sys
from pathlib import Path

TASKS={
"pull_cube":("PullCube-v1",85001,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
"stack_cube":("StackCube-v1",95001,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
ARMS=("source","memory","projected","observer","stateless","naive")
EXPECTED_REV="6bdeb28810330ab5425ccd629bb561c58a56ff85"


def audit(name,spec,root):
    task,first,sha=spec
    file=root/f"ack_loss_physx_resync_{name}_8.json"
    if not file.exists():
        raise ValueError(f"Missing original native PhysX task: {name}")
    a=json.loads(file.read_text())
    rows=a.get("episodes",[])
    seeds=list(range(first,first+8))
    if (a.get("task")!=task or a.get("checkpoint_sha256")!=sha or
            a.get("hf_revision")!=EXPECTED_REV or a.get("training_performed") is not False or
            a.get("backend")!="physx_cpu" or a.get("seed_list")!=seeds or
            a.get("external_fault_protocol")!="research/ACK_LOSS_PHYSX_RESYNC_PRECOMMIT_V1.json" or
            len(rows)!=8 or [e.get("seed") for e in rows]!=seeds):
        raise ValueError(f"Model/source or frozen seed/full denominator mismatch: {name}")
    outcomes={}
    for arm in ARMS:
        if any(type(r.get("success_once",{}).get(arm)) is not bool for r in rows
               if arm!="memory" or arm not in r.get("refusals",{})):
            raise ValueError(f"Missing actual physical outcome: {arm}")
        outcomes[arm]=sum(bool(row.get("success_once",{}).get(arm,False)) for row in rows)
        if outcomes[arm]!=a["success_count"][arm]:
            raise ValueError("Original success sum changed")
    triggered=[]
    max_pos=0.0
    max_rot=0.0
    for row in rows:
        for baseline,diff in row.get("initial_obs_diff",{}).items():
            if baseline not in ARMS[1:] or not 0<=diff<=5e-4:
                raise ValueError("Initial states were not paired")
        fault=row.get("ack_loss_fault",{})
        if fault.get("triggered"):
            if (fault.get("seed")!=row["seed"] or fault.get("action_index")!=2 or
                    fault.get("physical_env_step_completed") is not True or
                    fault.get("further_action_was_refused") is not True or
                    fault.get("authoritative_target_reads_for_recovery")!=1):
                raise ValueError("Fault recovery did not genuinely execute or refuse")
            triggered.append(row["seed"])
        elif fault.get("reason")!="observer_arm_never_reached_third_action":
            raise ValueError("Absent fault must have explicit reason, never discard")
        e=row.get("observer_end_target_error")
        if (not isinstance(e,dict) or any(
                type(e.get(k)) not in (int,float) or not math.isfinite(e[k]) or e[k]<0
                for k in ("max_position_abs","rotation_rad"))):
            raise ValueError("Missing original final controller target audit")
        max_pos=max(max_pos,e["max_position_abs"])
        max_rot=max(max_rot,e["rotation_rad"])
        for events in row.get("approximations",{}).values():
            if any(v.get("exactness")!="NOT_EXACT" for v in events):
                raise ValueError("Clipped approximation described as exact")
    if len(triggered)==0 or len(triggered)!=a.get("fault_triggered_episodes"):
        raise ValueError("Fault did not reach required physical controller steps")
    live_only=sum(x["success_once"].get("projected",False) and
                  not x["success_once"].get("observer",False) for x in rows)
    restored_only=sum(x["success_once"].get("observer",False) and
                      not x["success_once"].get("projected",False) for x in rows)
    matched=8-live_only-restored_only
    gate=("SOURCE_INCOMPETENT" if outcomes["source"]<5 else
          "SUPPORTED_WITH_PRIVILEGED_RESYNC" if (
            matched>=6 and max_pos<=3e-5 and max_rot<=3e-4
          ) else "FALSIFIED_OR_OUT_OF_TOLERANCE")
    return {
       "task":task,"n":8,"original_seed_list":seeds,"success":outcomes,
       "fault_reached_n":len(triggered),"fault_reached_seeds":triggered,
       "recovery_state_reads":len(triggered),
       "lost_ack_guard_failures":0,
       "matched_success":matched,"live_only":live_only,"recovered_only":restored_only,
       "max_final_position_error_m":max_pos,"max_final_rotation_error_rad":max_rot,
       "predeclared_gate":gate,"original_episode_rows":rows,
       "claim_limit":"Simulated physical command was delivered; ACK was unknown; recovery used one private authoritative target readback per fault; no sensor-free/real-hardware safety guarantee"
    }


def main():
    if len(sys.argv)!=3:
        raise SystemExit("Usage: ack_loss_physx_resync_audit.py RAW_FOLDER OUT.json")
    root,out=Path(sys.argv[1]),Path(sys.argv[2])
    data={
    "protocol":"research/ACK_LOSS_PHYSX_RESYNC_PRECOMMIT_V1.json",
    "status":"author-operated_simulation_not_independent_external_validation",
    "full_denominator":16,
    "results":{name:audit(name,spec,root) for name,spec in TASKS.items()},
    }
    out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("LOST_ACK_REAL_PHYSX_AGGREGATE",json.dumps({
       name:{k:result[k] for k in ("success","fault_reached_n","matched_success",
          "live_only","recovered_only","predeclared_gate")}
       for name,result in data["results"].items()},sort_keys=True))


if __name__=="__main__":
    main()
