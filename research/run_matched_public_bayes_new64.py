"""Prospectively preregistered untouched-source 64 original matched-information PhysX PPO rolls.

No inference/probe/hidden-read/threshold modification: patch only new reset
identities in the pristine 16-state source, after frozen-source Git blob check.
This study is NOT part of the 16-state development cohort.
"""
from __future__ import annotations
import argparse,hashlib,importlib,json,os,subprocess
from pathlib import Path

PRE="research/MATCHED_PUBLIC_BAYES_NEW64_PREOUTCOME_V1.json"
PRE_BLOB="9c758954f28cd0f3a99480f43828ab2a024c805a"
SOURCE="research/frozen_ppo_matched_public_bayes_physx.py"
SOURCE_BLOB="6e039af56006827fc2fe063b541cfa3dcd1ddc89"
MOTION_BLOB="064bb46831b61af73ad445bc836326837ec5468f"
SEED_FIRST={"pull_cube":1760001,"stack_cube":1770001}
TASKS={"pull_cube":"PullCube-v1","stack_cube":"StackCube-v1"}
MODELS={"pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
        "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"

def hash_git(path):
    return subprocess.check_output(("git","hash-object",path),text=True).strip()

def pin_sources():
    for path,sha in ((PRE,PRE_BLOB),(SOURCE,SOURCE_BLOB),
                     ("research/empirical_probe_response_classifier.py",MOTION_BLOB)):
        if hash_git(path)!=sha:raise ValueError("UNFROZEN ORIGINAL METHOD OR PROTOCOL: "+path)

def accepted(task,chunk):
    if task not in SEED_FIRST or type(chunk) is not int or not 0<=chunk<=3:
        raise ValueError("Require 2 named tasks x 4 exactly 8-reset shards")
    s=SEED_FIRST[task]+chunk*8
    return list(range(s,s+8))

def independent_eight(record,task,chunk):
    ids=accepted(task,chunk)
    ten=("source_no_fault","fault_oracle_private_target",
         "fault_optimistic_unverified_ack","fault_strict_common_exact",
         "fault_robust_two_history_without_query",
         "fault_robust_then_single_privileged_query",A,B,C,
         "fault_assume_held_without_query")
    if not (record.get("schema")=="frozen_ppo_matched_prefix_native_2x2_four_truth_v1"
            and record.get("original_seed_population")==ids
            and record.get("task")==TASKS[task]
            and record.get("original_external_frozen_checkpoint_sha256")==MODELS[task]
            and record.get("all_nine_actual_control_arms")==list(ten)
            and record.get("frozen_protocol")==PRE
            and record.get("real_physx_simulator") is True
            and record.get("frozen_model_retrained") is False
            and record.get("matched_prefix_causal_information_ablation") is True):
        raise ValueError("Source/native frozen PPO or physical matched prefix metadata changed")
    original=record.get("episodes",[])
    if len(original)!=8 or [x.get("seed") for x in original]!=ids:
        raise ValueError("Original eight reset denominator must be exact")
    totals={n:{"official_success":0,"private_reads":0,
               "public_xyz_events":0,"confident":0,"wrong_confident":0}
            for n in (A,B,C)}
    witnesses=[]
    for row in original:
        seed=row["seed"]
        intended=(seed-1)%4
        if (row["original_precommitted_physical_t2_execution_truth"]!=
            ("applied" if intended in (1,3) else "held") or
            row["original_precommitted_physical_t3_execution_truth"]!=
            ("applied" if intended in (2,3) else "held")):
            raise ValueError("Physically executed ACK truth violates preoutcome balance")
        succ=row.get("success_once",{})
        reads=row.get("privileged_target_readback_decision_count",{})
        samples=row.get("public_motion_observation_cost_samples",{})
        for name in (A,B,C):
            if type(succ.get(name)) is not bool or type(reads.get(name)) is not int or not 0<=reads[name]<=1:
                raise ValueError("Invalid actual full task success/private read count")
            totals[name]["official_success"]+=int(succ[name])
            totals[name]["private_reads"]+=reads[name]
            cost=samples.get(name)
            if cost not in (0,2):raise ValueError("Public samples unaccounted")
            # Physical probe t4 is equalized; decision-visible cost only A/B.
            if name in (A,B) and cost!=2:
                raise ValueError("A/B use unequal or missing public XYZ samples")
            if name==C and cost!=0:
                raise ValueError("Private-only C was given extra decision public data")
            totals[name]["public_xyz_events"]+=cost
        for key in ("matched_prefix_physical_audit","matched_posterior_prefix_audit"):
            compare=row.get(key,{})
            if compare.get("valid_exact_prefix") is not True or compare.get("audit_only_hidden_target_not_a_method_input") is not True:
                raise ValueError("False physical/evidence matched-prefix declaration")
            deltas=compare.get("native_fault_dispatch_linf_each",[])
            if len(deltas)!=2 or max(*deltas,
                compare.get("pre_t5_achieved_position_max_abs_m",float("inf")),
                compare.get("pre_t5_achieved_orientation_geodesic_rad",float("inf")),
                compare.get("pre_t5_target_position_max_abs_m",float("inf")),
                compare.get("pre_t5_target_orientation_geodesic_rad",float("inf")))>5e-5:
                raise ValueError("ACTUAL t2/t3 native physical commands or SE3 prefixes differ")
        for name,evidence_key in ((A,"public_t3_evidence"),(B,"same_sensor_posterior_evidence")):
            ev=row.get(evidence_key,{})
            if type(ev.get("authorized")) is not bool or type(ev.get("wrong_confident")) is not bool:
                raise ValueError("Missing original public decision/confident-wrong proof")
            if len(ev.get("candidate_residuals_m",[]))<1:raise ValueError("Missing latent history model")
            if ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
                raise ValueError("Private model truth leaked to public decision")
            if ev["authorized"] and reads[name]!=0:
                raise ValueError("Public confidence used private read")
            if name==B:
                weights=ev.get("posterior_weights",[])
                if len(weights)!=len(ev["candidate_residuals_m"]) or abs(sum(weights)-1)>1e-5:
                    raise ValueError("Not the predeclared normalized residual-score competitor")
                if ev.get("posterior_threshold_predeclared")!=.95:
                    raise ValueError("Post-outcome score threshold change")
            totals[name]["confident"]+=int(ev["authorized"])
            totals[name]["wrong_confident"]+=int(ev["wrong_confident"])
        witnesses.append({"task":task,"seed":seed,"true_fault_pattern":intended,
                          "official_task_success":{n:succ[n] for n in (A,B,C)},
                          "private_reads":{n:reads[n] for n in (A,B,C)},
                          "same_public_samples":samples[A]==samples[B]==2,
                          "empirical_public_confident":row["public_t3_evidence"]["authorized"],
                          "posterior_score_confident":row["same_sensor_posterior_evidence"]["authorized"],
                          "empirical_wrong_confident":row["public_t3_evidence"]["wrong_confident"],
                          "posterior_wrong_confident":row["same_sensor_posterior_evidence"]["wrong_confident"]})
    return {"schema":"matched_public_two_methods_and_one_fixed_new64_eight_original_audit_v1",
            "task":task,"chunk":chunk,"seeds":ids,"truly_physically_stepped_control_worlds":80,
            "private_model_getter_for_public_A_B_is_audit_only":True,
            "exact_prechoice_physical_command_AND_SE3_prefix_match":True,
            "uncalibrated_residual_pseudo_posterior_not_true_probabilities":True,
            "source_outcomes":totals,"original_all_eight":witnesses}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--task",choices=tuple(SEED_FIRST),required=True)
    p.add_argument("--chunk",type=int,choices=range(4),required=True)
    a=p.parse_args()
    pin_sources()
    ids=accepted(a.task,a.chunk)
    os.environ["ABI_TASK"]=a.task
    mod=importlib.import_module("research.frozen_ppo_matched_public_bayes_physx")
    if mod.PUBLIC_ARM!=A or mod.POST_ARM!=B or tuple(mod.FAULT_STEPS)!=(2,3) or mod.HORIZON!=50:
        raise ValueError("Source frozen methods changed")
    mod.SEEDS=ids
    mod.COHORT[a.task]=(TASKS[a.task],ids)
    mod.PROTO=PRE
    mod.main()
    f=Path(f"mixed_ack_{a.task}_original8.json")
    raw=f.read_bytes()
    report=independent_eight(json.loads(raw),a.task,a.chunk)
    report.update(pre_registered_protocol_git_blob=PRE_BLOB,
                  original_nonrefit_runner_git_blob=SOURCE_BLOB,
                  exact_original_PhysX_JSON_SHA256=hashlib.sha256(raw).hexdigest())
    f.rename(f"bayes_same_public_{a.task}_chunk{a.chunk}_original8.json")
    Path(f"bayes_same_public_{a.task}_chunk{a.chunk}_audit.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("PROSPECTIVE_64_MATCHED_PUBLIC_REAL_PHYSX",json.dumps({
        "task":a.task,"chunk":a.chunk,"n":8,
        "same_public":True,"n_physical_worlds":80,
        "totals":report["source_outcomes"]},sort_keys=True))

if __name__=="__main__":main()
