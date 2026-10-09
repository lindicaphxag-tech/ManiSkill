"""PHYSICALLY re-step 2x2 unknown ACK truth under EXACT same source init.

Companion of 2026-10-09 preregistered truly NEW 301/302xxxxx seed cohorts.
Changes NO original PPO/model/response classifier/action policy. Original
source is byte-pinned; candidate method only overrides explicit two-bit
truth schedule and task/protocol; all 10 physical worlds step per truth.

A/B/C share physically identical native command prefix and audited full
SE3 controller/achieved state before t5. NOT an official DualABI adaptation.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,random,subprocess,sys
from pathlib import Path

PRE="research/ISOLATED_QUERY_FACTORIAL128_PREOUTCOME_V1.json"
OLD="research/frozen_sources/matched_public_bayes_640_original_exact.py"
NEW="research/frozen_ppo_matched_public_factorial128_physx.py"
OLD_SHA="6e039af56006827fc2fe063b541cfa3dcd1ddc89"
CLASSIFIER_SHA="064bb46831b61af73ad445bc836326837ec5468f"
TASKS={"pull_cube":("PullCube-v1",3010001),
       "stack_cube":("StackCube-v1",3020001)}
MODELS={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
        "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
ARMS=(A,B,C)
REG=("source_no_fault","fault_oracle_private_target",
    "fault_optimistic_unverified_ack","fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",A,B,C,
    "fault_assume_held_without_query")

def git_sha(path:str)->str:
    return subprocess.check_output(("git","hash-object",path),text=True).strip()

def frozen_preflight():
    require= lambda cond,msg:None if cond else (_ for _ in ()).throw(ValueError(msg))
    require(git_sha(OLD)==OLD_SHA,"Original source Git blob changed")
    require(git_sha("research/empirical_probe_response_classifier.py")==CLASSIFIER_SHA,
            "Previously trained response model/tolerances changed")
    old=Path(OLD).read_text(encoding="utf-8")
    patched=old.replace(
        "    truth_index=(int(seed)-1)%4",
        '    # Only the external physical ACK truth is overridden; every policy\n'
        '    # weight, action and inference rule is otherwise byte-identical to the\n'
        '    # preregistered original 640-world source.\n'
        '    truth_index=int(os.environ["ABI_TRUTH_INDEX"])'
    ).replace('PROTO="research/MATCHED_PUBLIC_BAYES_NATIVE16_PREOUTCOME_V1.json"',
              'PROTO="research/ISOLATED_QUERY_FACTORIAL128_PREOUTCOME_V1.json"')
    require(patched==Path(NEW).read_text(encoding="utf-8"),
            "Policy source differs by more than explicit truth override and protocol constant")
    protocol=json.loads(Path(PRE).read_text())
    require(protocol["created_before_any_new_physx_outcome"] is True and
            protocol["original_matched_public_PPO_runner_git_blob"]==OLD_SHA and
            protocol["expected_actual_native_controller_worlds"]==1280 and
            protocol["task_reset_register"]==
            {"pull_cube":[3010001,3010016],"stack_cube":[3020001,3020016]},
            "Prospective cohort/real physics contract was altered")
    return protocol

def selected(task,chunk):
    if task not in TASKS or type(chunk) is not int or chunk not in (0,1):
        raise ValueError("Unsupported task/shard")
    begin=TASKS[task][1]+chunk*8
    return list(range(begin,begin+8))

def validate_shard(raw,task,chunk,truth_index):
    req=selected(task,chunk)
    if not(raw.get("schema")=="frozen_ppo_matched_prefix_native_2x2_four_truth_v1"
       and raw.get("real_physx_simulator") is True
       and raw.get("frozen_model_retrained") is False
       and raw.get("task")==TASKS[task][0]
       and raw.get("original_external_frozen_checkpoint_sha256")==MODELS[task]
       and raw.get("frozen_protocol")==PRE
       and raw.get("all_nine_actual_control_arms")==list(REG)
       and raw.get("original_seed_population")==req):
        raise ValueError("Source PPO/original physical 10-arm/frozen truth population changed")
    rows=raw.get("episodes")
    if not isinstance(rows,list) or len(rows)!=8 or [r["seed"] for r in rows]!=req:
        raise ValueError("Dropped/extra/reordered original source reset")
    outcome={a:{"task_success":0,"private_reads":0,"wrong_authorizations":0,
                "authorized":0,"public_XYZ_events":0} for a in ARMS}
    for r in rows:
        t2=("applied" if truth_index in (1,3) else "held")
        t3=("applied" if truth_index in (2,3) else "held")
        if (r["original_precommitted_physical_t2_execution_truth"],
            r["original_precommitted_physical_t3_execution_truth"])!=(t2,t3):
            raise ValueError("SOURCE ACTUAL APPLIED/HELD ACK truth drift")
        for a in ARMS:
            if (type(r["success_once"].get(a)) is not bool
                or type(r["privileged_target_readback_decision_count"].get(a)) is not int
                or r["privileged_target_readback_decision_count"][a] not in (0,1)
                or [z["step"] for z in r["faults"].get(a,[])]!=[2,3]
                or r["public_motion_observation_cost_samples"].get(a)!=(0 if a==C else 2)
                or r["shared_neutral_probe_step4"].get(a,{}).get("physically_dispatched") is not True):
                raise ValueError("Original PhysX fault, public cost or completion corrupt")
            outcome[a]["task_success"]+=int(r["success_once"][a])
            outcome[a]["private_reads"]+=r["privileged_target_readback_decision_count"][a]
            outcome[a]["public_XYZ_events"]+=r["public_motion_observation_cost_samples"][a]
        for k in ("matched_prefix_physical_audit","matched_posterior_prefix_audit"):
            x=r.get(k,{})
            vals=[*x.get("native_fault_dispatch_linf_each",[])]
            for field in ("pre_t5_achieved_position_max_abs_m",
                          "pre_t5_achieved_orientation_geodesic_rad",
                          "pre_t5_target_position_max_abs_m",
                          "pre_t5_target_orientation_geodesic_rad"):
                vals.append(x.get(field,float("inf")))
            if len(vals)!=6 or max(vals)>5e-5 or x.get("valid_exact_prefix") is not True or x.get("audit_only_hidden_target_not_a_method_input") is not True:
                raise ValueError("Main information policies had ACTUAL mismatched physical native predecision prefix")
        for a,k in ((A,"public_t3_evidence"),(B,"same_sensor_posterior_evidence")):
            e=r.get(k,{})
            if type(e.get("authorized")) is not bool or type(e.get("wrong_confident")) is not bool:
                raise ValueError("Missing evidence authority/error")
            if e.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                raise ValueError("Hidden privileged target was a method input")
            if e["authorized"] and r["privileged_target_readback_decision_count"][a]!=0:
                raise ValueError("Same action both authorized and queried")
            if a==B and e.get("posterior_threshold_predeclared")!=.95:
                raise ValueError("Posterior competitor score tuned after protocol")
            outcome[a]["authorized"]+=int(e["authorized"])
            outcome[a]["wrong_authorizations"]+=int(e["wrong_confident"])
    return {"task":task,"chunk":chunk,"forced_truth":truth_index,
            "original_reset_ids":req,"n_original_actual_controller_worlds":80,
            "source_outcome":outcome,
            "all_8_valid_matched_A_B_C_native_prefixes":True,
            "source_initial_public_observation_hash_per_reset":{
                str(r["seed"]):r["initial_source_physical_obs_sha256"] for r in rows}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",choices=tuple(TASKS),required=True)
    ap.add_argument("--chunk",type=int,choices=(0,1),required=True)
    args=ap.parse_args()
    frozen_preflight()
    ids=selected(args.task,args.chunk)
    import numpy as np
    import torch
    os.environ["ABI_TASK"]=args.task
    sys.path.insert(0,str(Path.cwd()/"research"))
    module=importlib.import_module("research.frozen_ppo_matched_public_factorial128_physx")
    if tuple(module.FAULT_STEPS)!=(2,3) or tuple(module.NAMES)!=REG or module.HORIZON!=50:
        raise RuntimeError("Controller physical world definition changed")
    module.SEEDS=ids
    module.COHORT[args.task]=(TASKS[args.task][0],ids)
    base_trial=module.trial
    def physical_trial(policy,seed):
        # ALL truths in ONE process, reset RNG before each original physical trial.
        # This is prespecified, not a post-hoc repair of a failed first study.
        random.seed(seed)
        np.random.seed(seed % (2**32))
        torch.manual_seed(seed)
        return base_trial(policy,seed)
    module.trial=physical_trial
    seen={}
    all_source=[]
    for truth in range(4):
        os.environ["ABI_TRUTH_INDEX"]=str(truth)
        module.main()  # REAL frozen PPO inference + 10 ManiSkill PhysX worlds for each of 8 original states
        source=Path(f"mixed_ack_{args.task}_original8.json")
        raw=source.read_bytes()
        report=validate_shard(json.loads(raw),args.task,args.chunk,truth)
        report["source_sha256"]=hashlib.sha256(raw).hexdigest()
        report["original_frozen_unmodified_PPO_git_blob"]=OLD_SHA
        prefix=f"query_isolated_{args.task}_chunk{args.chunk}_truth{truth}"
        source.rename(prefix+"_original8.json")
        Path(prefix+"_audit.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        all_source.append((prefix,report["source_sha256"]))
        for seed,obs_sha in report["source_initial_public_observation_hash_per_reset"].items():
            seen.setdefault(seed,{})[str(truth)]=obs_sha
        print("TRUE_2x2_MATCHED_PUBLIC_NATIVE_PHYSX_SHARD",json.dumps({
              "task":args.task,"chunk":args.chunk,"truth":truth,
              "original_actual_controller_worlds":80,"outcomes":report["source_outcome"],
              "source_sha256":report["source_sha256"]},sort_keys=True),flush=True)
    failed={seed:records for seed,records in seen.items()
            if len(records)!=4 or len(set(records.values()))!=1}
    ledger={"task":args.task,"chunk":args.chunk,"source_reset_ids":ids,
            "four_physical_truths_executed_all_10_controllers":True,
            "source_registry_sha256":all_source,
            "exact_original_public_obs_hash_equal_across_truths":not failed,
            "source_initial_hash_by_seed_truth":seen,"failures":failed,
            "model_unchanged_source_git_blob":OLD_SHA,
            "not_independently_operated_third_party":True}
    Path(f"query_isolated_{args.task}_chunk{args.chunk}_full_truth_prefix_provenance.json").write_text(
        json.dumps(ledger,indent=2,sort_keys=True)+"\n")
    if failed:raise RuntimeError("FIRST ORIGINAL FACTORIAL SHARD FAILED TRUE SAME RESET equality. Preserve source and DO NOT promote")

if __name__=="__main__":main()
