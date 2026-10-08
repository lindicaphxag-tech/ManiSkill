"""Fail-closed auditor for original PhysX frozen-policy ACK-loss treatments.

Native simulator outcomes are source evidence, NOT a certificate of robot safety.
A complete failed outcome remains in denominator.
"""
import argparse
import json
import math
from pathlib import Path

TASKS={
    "pull_cube":("PullCube-v1","74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",94001),
    "stack_cube":("StackCube-v1","e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",95001)
}
CONDITIONS=("applied_no_ack","neutral_arm_delta_no_ack")
ARMS=("source","oracle_live_memory","recovered_one_readback",
      "optimistic_assume_applied","pessimistic_assume_neutral","fail_closed_stop")
PROTOCOL="research/ACTION_ABI_UNKNOWN_ACK_PHYSX_PREREG_V1.json"
FROZEN_SHA="3ead83ecbb68eb6a405cdf768a42c617f649ddc4"
HF_REV="6bdeb28810330ab5425ccd629bb561c58a56ff85"

def audit(folder: Path)->dict:
    expected={f"ack_loss_{task}_{fault}_fresh8.json" for task in TASKS for fault in CONDITIONS}
    files=list(folder.glob("ack_loss_*_fresh8.json"))
    if len(files)!=4 or {x.name for x in files}!=expected:
        raise ValueError("Four original frozen task×fault condition files required")
    out={}
    for path in sorted(files):
        block=json.loads(path.read_text())
        task=next((x for x in TASKS if path.name.startswith(f"ack_loss_{x}_")),None)
        if task is None:
            raise ValueError("Unregistered task file")
        env,sha,first=TASKS[task]
        fault=next((c for c in CONDITIONS if path.name==f"ack_loss_{task}_{c}_fresh8.json"),None)
        if fault is None:
            raise ValueError("Unregistered fault condition")
        if (block.get("schema")!="action_abi_unknown_arm_command_ack_prospective_physx_v1"
            or block.get("preregistration")!=PROTOCOL
            or block.get("frozen_prereg_commit")!=FROZEN_SHA
            or block.get("task")!=env or block.get("fault")!=fault
            or block.get("checkpoint_sha256")!=sha
            or block.get("checkpoint_revision")!=HF_REV
            or block.get("training_performed") is not False
            or block.get("real_physx") is not True
            or block.get("backend")!="physx_cpu"):
            raise ValueError("Model/fault/experiment provenance mutated")
        seeds=list(range(first,first+8))
        if block.get("seeds")!=seeds:
            raise ValueError("Unregistered original seeds")
        rows=block.get("rows")
        if not isinstance(rows,list) or len(rows)!=8 or [r.get("seed") for r in rows]!=seeds:
            raise ValueError("All eight original source episodes required")
        totals={a:0 for a in ARMS}
        faults={a:0 for a in ARMS[1:]}
        readbacks=0
        worst_error=0.
        for row in rows:
            if row.get("task")!=env or row.get("fault")!=fault or row.get("fault_step")!=2:
                raise ValueError("Wrong fault condition or task in individual source episode")
            flags=row.get("success_once",{})
            if set(flags)!=set(ARMS):
                raise ValueError("Every source episode must contain all six completed success flags")
            for a in ARMS:
                if type(flags[a]) is not bool:
                    raise ValueError("Source task success must be a genuine boolean")
                totals[a]+=int(flags[a])
                if type(row.get("steps",{}).get(a)) is not int:
                    raise ValueError("Source rollout or explicit refusal must have at least one actual step")
            for a in ARMS[1:]:
                if row.get("fault_reached",{}).get(a) is not True:
                    raise ValueError("Prespecified time step fault was never executed: preserve failure")
                faults[a]+=1
                d=row.get("initial_obs_diff",{}).get(a)
                if not isinstance(d,(int,float)) or not math.isfinite(d) or d>5e-4:
                    raise ValueError("Source and destination task states are not initially matched")
            q=row.get("readback_queries",{})
            if set(q)!=set(ARMS[1:]) or q["recovered_one_readback"]!=1:
                raise ValueError("Exactly one recovery readback and explicitly zero other decision-time readbacks required")
            if q["oracle_live_memory"] != -1:
                raise ValueError("Oracle must disclose repeated privileged memory access")
            if any(q[a]!=0 for a in ARMS[1:]
                   if a not in ("recovered_one_readback","oracle_live_memory")):
                raise ValueError("Nonoracle observer accessed target-memory at action selection")
            readbacks+=1
            e=row.get("resync_position_error_m")
            if not isinstance(e,(int,float)) or not math.isfinite(e) or e>3e-5 or e<0:
                raise ValueError("Measured one-shot target readback mismatch")
            worst_error=max(worst_error,e)
            gap=row.get("ambiguity_diameter_m")
            if not isinstance(gap,(int,float)) or not math.isfinite(gap) or gap<0:
                raise ValueError("Missing possible-history separation evidence")
            for label in ("post_fault_optimistic_position_error_m",
                          "post_fault_pessimistic_position_error_m"):
                x=row.get(label)
                if not isinstance(x,(int,float)) or not math.isfinite(x) or x<0:
                    raise ValueError("Missing optimistic/pessimistic actual-goal audit")
            if "fail_closed_stop" not in row.get("refusals",{}):
                raise ValueError("Fail-closed arm must stop after unknown ACK")
            if row["steps"]["fail_closed_stop"] != 3:
                raise ValueError("Stop control executed after the fault")
            if any(e.get("exactness")!="NOT_EXACT"
                   for events in row.get("approximations",{}).values() for e in events):
                raise ValueError("False exact-action claim")
        if totals!=block.get("success_count"):
            raise ValueError("Reported source scores differ from original full rows")
        out[f"{task}:{fault}"]={
            "n":8,"success":totals,"fault_counts":faults,
            "readback_calls_total":readbacks,
            "max_attested_resync_error_m":worst_error,
            "source_competent_predeclared":totals["source"]>=5
        }
    return {"n_original_paired_state_conditions":32,"frozen_before_outcomes":True,
            "physx_original_author_run":True,"no_external_replication":True,
            "status":"FULL_SOURCE_COHORT_AUDITED_NOT_SAFETY_CERTIFIED",
            "results":out}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    z=audit(a.input_dir)
    a.output.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n")
    print("UNKNOWN_ACK_ORIGINAL_PHYSX_AUDIT",json.dumps(
        {k:{"source":v["success"]["source"],"recovered":v["success"]["recovered_one_readback"],
            "optimistic":v["success"]["optimistic_assume_applied"],
            "pessimistic":v["success"]["pessimistic_assume_neutral"],
            "stop":v["success"]["fail_closed_stop"]}
         for k,v in z["results"].items()},sort_keys=True))


if __name__=="__main__":
    main()
