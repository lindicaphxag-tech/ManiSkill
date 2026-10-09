"""Independent exact-4-state official LeRobot LIBERO task-competency audit.

No fault recovery; observational VLA task performance only.  Validation is
strict about the original official per-episode labels and denominators.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

class SourceError(ValueError):
    pass

def audit(raw, task_id: int, expected_n: int = 4):
    if type(raw) is not dict or set(raw) < {"per_task", "per_group", "overall"}:
        raise SourceError("Missing native LeRobot output")
    pts=raw["per_task"]
    if not isinstance(pts,list) or len(pts)!=1:
        raise SourceError("Exactly one original suite task required")
    t=pts[0]
    if t.get("task_group")!="libero_spatial" or type(t.get("task_id")) is not int or t["task_id"] != task_id:
        raise SourceError("Wrong native task")
    m=t.get("metrics")
    if not isinstance(m,dict): raise SourceError("Missing per-episode official metrics")
    successes=m.get("successes")
    rewards=m.get("sum_rewards")
    if not isinstance(successes,list) or len(successes)!=expected_n or any(type(b) is not bool for b in successes):
        raise SourceError("Missing official per-episode bool vector")
    if not isinstance(rewards,list) or len(rewards)!=expected_n or any(type(r) not in (int,float) or not math.isfinite(r) for r in rewards):
        raise SourceError("Invalid original reward vector")
    # Fail closed on unexpected task or summary selection; no dropped episodes.
    grp=raw.get("per_group")
    if type(grp) is not dict or set(grp)!={"libero_spatial"}: raise SourceError("Wrong group identity")
    n_ok=sum(successes)
    for name,v in [("task",t),("group",grp["libero_spatial"]),("overall",raw.get("overall"))]:
        if not isinstance(v,dict) or type(v.get("n_episodes")) is not int or v["n_episodes"]!=expected_n:
            raise SourceError(name+" original denominator mismatch")
        if type(v.get("n_success")) is not int or v["n_success"]!=n_ok:
            raise SourceError(name+" original task outcome mismatch")
        pct=v.get("pc_success")
        if type(pct) not in (int,float) or not math.isfinite(pct) or abs(pct-100.0*n_ok/expected_n)>1e-6:
            raise SourceError(name+" original success rate mismatch")
    return {
        "evidence_type": "REAL_FROZEN_PRETRAINED_VLA_NATIVE_LIBERO_4_EPISODE_COMPETENCE_PILOT",
        "task_suite": "libero_spatial", "task_id":task_id,
        "n_episodes":expected_n, "n_success":n_ok,
        "original_official_successes":successes, "original_rewards":rewards,
        "unknown_ack_faults":False, "beliefbridge_vla_recovery":False,
        "controller_target_memory_verified":False,
        "no_training":True, "pilot_not_full_suite":True,
        "not_independent_external_investigator":True,
    }

def selftest():
    b=[True,False,True,False]
    obj={"per_task":[{"task_group":"libero_spatial","task_id":1,"metrics":{"successes":b,"sum_rewards":[1.,0.,1.,0.]},
         "n_episodes":4,"n_success":2,"pc_success":50.}],
         "per_group":{"libero_spatial":{"n_episodes":4,"n_success":2,"pc_success":50.}},
         "overall":{"n_episodes":4,"n_success":2,"pc_success":50.}}
    assert audit(obj,1)["n_success"]==2
    probes=[
        lambda x:x["per_task"][0]["metrics"].update(successes=[True,False,1,False]),
        lambda x:x["overall"].update(n_success=3),
        lambda x:x["per_task"][0]["metrics"].update(successes=[True]),
        lambda x:x["per_task"][0].update(task_id=0),
        lambda x:x["per_group"].update(other={}),
        lambda x:x["overall"].update(pc_success=100.),
    ]
    for mutate in probes:
        x=json.loads(json.dumps(obj));mutate(x)
        try: audit(x,1)
        except SourceError: pass
        else: raise AssertionError("Bad original source accepted")
    print("ORIGINAL_LIBERO_NATIVE_COHORT_AUDITOR_TESTS_PASS",len(probes))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--task-id",type=int,default=1)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test: return selftest()
    if a.input is None or a.output is None: p.error("--input and --output required")
    out=audit(json.loads(a.input.read_text()),a.task_id)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("REAL_NATIVE_FROZEN_VLA_COMPLETE_COHORT",json.dumps(out,sort_keys=True))

if __name__=="__main__":main()
