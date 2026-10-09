"""Independent stdlib-only auditor of ten actual native-controller PhysX worlds.

Reconstructs the ORIGINAL discrete full-history selection for a single probe
and the new TWO-probe intersection witness, with zero test-time tuning.
All four applied/held physical truth patterns and all task failures retained.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
PPO={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
     "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
START={"pull_cube":900001,"stack_cube":910001}
EPS={"pull_cube":.006944262561376447,"stack_cube":.00719087965534261}
SOURCE_BLOB="fa7b5cbe15fa4406ffeeb3fd4a60e11d2bd35836"
PROTO_BLOB="2998c9312210a2c7b20d3d257153c9c08783032f"
PROTO="research/SEQUENTIAL_TWO_PUBLIC_PROBES_NEW64_PREOUTCOME_V1.json"
NAMES=("source_no_fault","fault_oracle_private_target",
       "fault_optimistic_unverified_ack","fault_strict_common_exact",
       "fault_robust_two_history_without_query","fault_robust_then_single_privileged_query",
       "fault_always_single_privileged_query","fault_assume_held_without_query",
       "fault_public_single_t4_or_t6_query","fault_public_two_t4t5_or_t6_query")
SINGLE=NAMES[-2]
DUAL=NAMES[-1]
STRONG={"pull_cube":NAMES[5],"stack_cube":NAMES[6]}
def physical_truth(seed,step):
    if step==2:return seed%2==0
    if step==3:return (seed//2)%2==0
    raise ValueError("Unplanned native fault")
def eligible(res,eps):
    return [i for i,v in enumerate(res) if v<=eps+1e-12]
def proposed_witness(first,second,eps):
    # Joint compatibility with one hypothesis across BOTH physically
    # executed public response steps, separating each other candidate by
    # the predefined fixed +2mm margin on at least one observation.
    matches=[i for i,(a,b) in enumerate(zip(first,second))
             if a<=eps+1e-12 and b<=eps+1e-12]
    return bool(len(matches)==1 and all(
        first[i]>eps+.002 or second[i]>eps+.002
        for i in range(len(first)) if i!=matches[0])),matches
def audit(folder):
    expected={f"dual_public_ack_{task}_chunk{chunk}_original8.json"
              for task in START for chunk in range(4)}
    got={p.name for p in folder.glob("dual_public_ack_*_original8.json")}
    if got!=expected:raise ValueError("Missing original genuine native PhysX source or duplicated dataset")
    per=[]
    hashes={}
    for task,start in START.items():
        for chunk in range(4):
            path=folder/f"dual_public_ack_{task}_chunk{chunk}_original8.json"
            b=path.read_bytes(); hashes[path.name]=hashlib.sha256(b).hexdigest()
            x=json.loads(b)
            seeds=list(range(start+8*chunk,start+8*chunk+8))
            if (x.get("schema")!="frozen_ppo_full_joint_dual_public_neutral_t4t5_physx_v5"
                or x.get("preoutcome_protocol")!=PROTO
                or x.get("original_seed_population")!=seeds
                or x.get("all_ten_actual_control_arms")!=list(NAMES)
                or x.get("original_external_frozen_checkpoint_sha256")!=PPO[task]
                or x.get("real_physx_simulator") is not True
                or x.get("frozen_model_retrained") is not False
                or len(x.get("episodes",[]))!=8):
                raise ValueError("Original physical source/controller identity or policy changed")
            manifest=folder/f"dual_public_ack_{task}_chunk{chunk}_manifest.json"
            if not manifest.exists(): raise ValueError("Original shard manifest missing")
            m=json.loads(manifest.read_text())
            if (m.get("original_sha256")!=hashes[path.name]
                or m.get("seeds")!=seeds
                or m.get("preoutcome_protocol_git_blob")!=PROTO_BLOB
                or m.get("executed_method_git_blob")!=SOURCE_BLOB):
                raise ValueError("Original physical source digest does not match frozen method")
            for seed,r in zip(seeds,x["episodes"]):
                if (r.get("seed")!=seed or
                    r.get("original_precommitted_physical_t2_execution_truth")!=("applied" if physical_truth(seed,2) else "held") or
                    r.get("original_precommitted_physical_t3_execution_truth")!=("applied" if physical_truth(seed,3) else "held")):
                    raise ValueError("Actual physical t2/t3 truth does not match source preregistered seeds")
                flags=r.get("success_once",{}); reads=r.get("privileged_target_readback_decision_count",{})
                if set(flags)!=set(NAMES) or set(reads)!=set(NAMES):
                    raise ValueError("Missing method physical comparator")
                for name in NAMES:
                    if type(flags[name]) is not bool or type(reads[name]) is not int or (reads[name] not in (0,1) and not (name==NAMES[1] and reads[name]==-1)):
                        raise ValueError("Invalid official task success or decision query receipt")
                for name in (DUAL,SINGLE,STRONG[task],NAMES[6],NAMES[7]):
                    es=r.get("faults",{}).get(name,[])
                    if len(es)!=2 or [v.get("step") for v in es]!=[2,3]:
                        raise ValueError("Missing two actual native ACK physical events")
                    for step,event in zip((2,3),es):
                        got=event.get("actual_native_execution_truth") if name==NAMES[6] and step==3 else event.get("actual_native_precommitted_execution_truth")
                        if got!=("applied" if physical_truth(seed,step) else "held") or event.get("controller_execution_ack_seen_by_adapter")!="unknown":
                            raise ValueError("Native execution truth or hidden ACK leaked to adapter")
                neutral=r.get("known_delivered_zero_probe",{})
                for name in (DUAL,SINGLE,STRONG[task],NAMES[6]):
                    if set(neutral.get(name,{}))!={"4","5"}:
                        raise ValueError("Primary fully executed comparator missing physically known-delivered t4 and t5 probe")
                for name,sp in neutral.items():
                    if name not in NAMES: raise ValueError("Invalid native controller")
                    for step in ("4","5"):
                        if step not in sp: raise ValueError("Physically skipped neutral within non-stopped controller")
                        q=sp[step]
                        if (q.get("step")!=int(step) or q.get("actual_native_6d_dispatched")!=[0.]*6
                            or q.get("acknowledgement")!="known_applied"
                            or q.get("is_extra_common_physical_action") is not True
                            or (name!="source_no_fault" and q.get("audit_only_native_target_unchanged") is not True)):
                            raise ValueError("Probe not actually physically executed")
                for name in set(NAMES)-set(neutral):
                    f=r.get("refusals",{}).get(name)
                    if not (f and type(f.get("step")) is int and f["step"]<=5):
                        if not (flags[name] and r.get("steps",{}).get(name,50)<=5):
                            raise ValueError("Invented t4/t5 action for refused or missing source control")
                e1=r.get("public_t4_single_evidence",{});e2=r.get("public_t4_evidence",{})
                if not e1 or not e2:raise ValueError("Original two separately stepped public controllers absent")
                if r.get("public_motion_observation_cost_samples",{}).get(SINGLE)!=2 or r.get("public_motion_observation_cost_samples",{}).get(DUAL)!=4:
                    raise ValueError("Unlogged extra actual achieved XYZ information cost")
                e=EPS[task]
                for ev in (e1,e2):
                    d=ev.get("candidate_residuals_m",[])
                    if (len(d) not in (2,3,4) or len(d)!=ev.get("physical_candidate_count")
                        or ev.get("prior_training_epsilon_m")!=e
                        or any(type(z) not in (float,int) or not math.isfinite(z) or z<0 for z in d)
                        or ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True):
                        raise ValueError("Invalid public empirical response modeling provenance")
                first1=e1["candidate_residuals_m"]
                single_index=eligible(first1,e)
                single_authorized=bool(len(single_index)==1 and all(
                    d>e+.002 for i,d in enumerate(first1) if i!=single_index[0]))
                if (e1.get("accepted_position_indices")!=single_index
                    or e1.get("authorized") is not single_authorized
                    or e1.get("selected_candidate_index")!=(single_index[0] if single_authorized else None)):
                    raise ValueError("Single-probe original PPO authorization algorithm changed")
                first2=e2["candidate_residuals_m"]
                second=e2.get("second_candidate_residuals_m",[])
                if not second or len(first2)!=len(second):
                    raise ValueError("Second actually stepped neutral model response missing")
                joint_authorized,joint_index=proposed_witness(first2,second,e)
                if (e2.get("joint_accepted_full_history_indices")!=joint_index
                    or e2.get("authorized") is not joint_authorized
                    or e2.get("selected_candidate_index")!=(joint_index[0] if joint_authorized else None)
                    or e2.get("decision_only_both_physically_sampled_neutral_probes") is not True):
                    raise ValueError("Joint public history compatibility witness not reproducible")
                for name,ev,authorized,indices in ((SINGLE,e1,single_authorized,single_index),
                        (DUAL,e2,joint_authorized,joint_index)):
                    audit_truth=[i for i,(p,rot) in enumerate(
                        ev.get("after_physics_audit_pose_errors_after_second_probe",
                               ev.get("after_physics_audit_pose_errors",[])))
                        if p<=1e-4 and rot<=1e-3]
                    if ev.get("audit_only_true_candidate_indices")!=audit_truth:
                        raise ValueError("Actual AFTER native physical hidden controller pose falsified")
                    wrong=bool(authorized and indices[0] not in audit_truth)
                    if ev.get("wrong_confident") is not wrong:
                        raise ValueError("Confident wrong physical controller history mislabeled")
                    state=ev.get("resync_source")
                    if state=="empirical_public_achieved_motion":
                        if not authorized or reads[name]!=0: raise ValueError("Undisclosed private read")
                    elif state=="one_counted_authoritative_controller_target_read":
                        if authorized or reads[name]!=1: raise ValueError("Private read incorrectly counted")
                    elif state is None:
                        if reads[name]!=0: raise ValueError("Nonexecuted private query fabricated")
                    else: raise ValueError("Unknown hidden evidence source")
                per.append(dict(task=task,seed=seed,
                    joint_true=("A" if physical_truth(seed,2) else "H")+
                               ("A" if physical_truth(seed,3) else "H"),
                    two_success=flags[DUAL],single_success=flags[SINGLE],
                    strong_success=flags[STRONG[task]],fixed_success=flags[NAMES[6]],
                    always_held_success=flags[NAMES[7]],
                    two_reads=reads[DUAL],single_reads=reads[SINGLE],strong_reads=reads[STRONG[task]],
                    two_unique=joint_authorized,single_unique=single_authorized,
                    two_wrong_confident=e2["wrong_confident"],single_wrong_confident=e1["wrong_confident"],
                    two_extra_public_XYZ_samples=4,single_extra_public_XYZ_samples=2,
                    physical_neutral_controller_count=len(neutral),
                    genuine_early_stopped_arms=sorted(set(NAMES)-set(neutral))))
    if len(per)!=64 or len({(r["task"],r["seed"]) for r in per})!=64:
        raise ValueError("Incomplete original 64 physical states")
    outcomes={}
    for task in TASKS:
        for truth in ("AA","AH","HA","HH"):
            rr=[r for r in per if r["task"]==task and r["joint_true"]==truth]
            if len(rr)!=8:raise ValueError("Full four-joint physical ACK group not balanced")
            outcomes[f"{task}:{truth}"]={k:sum(r[k] for r in rr) for k in (
                "two_success","single_success","strong_success","fixed_success",
                "always_held_success","two_reads","single_reads","strong_reads",
                "two_unique","single_unique","two_wrong_confident","single_wrong_confident")}
            outcomes[f"{task}:{truth}"]["n"]=8
    overall={k:sum(r[k] for r in per) for k in (
        "two_success","single_success","strong_success","fixed_success","always_held_success",
        "two_reads","single_reads","strong_reads","two_unique","single_unique",
        "two_wrong_confident","single_wrong_confident","two_extra_public_XYZ_samples",
        "single_extra_public_XYZ_samples")}
    pair={x:0 for x in ("both_success","two_only","single_only","neither")}
    for r in per:
        key=("both_success" if r["two_success"] and r["single_success"]
             else "two_only" if r["two_success"] else "single_only"
             if r["single_success"] else "neither")
        pair[key]+=1
    return dict(schema="original_dual_public_new64_full_truth_native_physx_audit_v1",
                source_protocol_git_blob=PROTO_BLOB,
                source_executor_git_blob=SOURCE_BLOB,
                original_source_file_sha256=hashes,
                actual_reset_states=64,real_native_controller_worlds=640,
                four_joint_truths_each_16_actual_worlds=True,
                all_genuine_PPO_tasks_original_and_unfiltered=True,
                empirical_gain_model_not_certified_for_physical_dynamics=True,
                no_real_network_transport_fault_or_hardware_safety=True,
                no_external_independent_replication=True,
                paired_two_vs_single=pair,overall=overall,
                truth_task_strata=outcomes,original_full_per_seed=per)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=audit(a.source_dir)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("FULL_DUAL_PUBLIC_ORIGINAL_640_NATIVE_PHYSX_SOURCE",json.dumps(
        {"overall":d["overall"],"strata":d["truth_task_strata"],
         "paired":d["paired_two_vs_single"]},sort_keys=True),flush=True)
if __name__=="__main__":main()
