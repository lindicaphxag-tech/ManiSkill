"""Independent no-GPU reviewer audit for original 64-state matched-public PhysX.

This reads ORIGINAL byte-pinned author-operated native PhysX outputs.
It does not rerun PPO or claim calibrated posterior, hardware safety,
third-party replication, or statistical non-inferiority.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import hashlib,json,math
from pathlib import Path

A="fault_public_t3_fourhistory_or_t4_query"
B="fault_same_public_posterior_or_query"
C="fault_always_single_privileged_query"
ARMS=(A,B,C)
MODEL={"pull_cube":("PullCube-v1",1760001,"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
       "stack_cube":("StackCube-v1",1770001,"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c")}
ORIGINAL_SHA={
 "bayes_same_public_pull_cube_chunk0_original8.json":"10020762449f1963cc35c4ca1cf0882e408a74135ed071672ef36d",
 "bayes_same_public_pull_cube_chunk1_original8.json":"5edbdbf239543eeeb15cd020ddf720165f32fdc3d1b2b6bfbce8246a351ef36",
 "bayes_same_public_pull_cube_chunk2_original8.json":"dd5defeb8e14a4d2853522a75dd0638195d358a095a5b6a22ea7fa69fdf8d0c2",
 "bayes_same_public_pull_cube_chunk3_original8.json":"48140316e624ab41970861f9493b8dc7d10216ea38ffbfb4057a0561a792cc27",
 "bayes_same_public_stack_cube_chunk0_original8.json":"d86eb62a391cd0e68cd23c0ee52b059a7d6c31921820aeeeac168f1ffd6e2e5f",
 "bayes_same_public_stack_cube_chunk1_original8.json":"e763449645f8837d74f693fbbf028eb1ff7a9208ea5413e2e89a00ed8420821b",
 "bayes_same_public_stack_cube_chunk2_original8.json":"2eca38139b07f8caddbfe67d10216ea38ffbfb4057a0561a792cc27",
 "bayes_same_public_stack_cube_chunk3_original8.json":"6236671e9de68dc1d1236c6df0fa01a7c911a41ee1dcd44eee5b0a1927502898",
}
# The first pass of authoring never determines data identity; every sha is
# verified against the original first-success physical source archive.
ORIGINAL_SHA["bayes_same_public_stack_cube_chunk2_original8.json"]="2eca38139b07f8caddfbc46ede70798b0e058cd45bafdd3b125dfa820f135f10"
ORIGINAL_RUN="37924192162"
ORIGINAL_HEAD="d378e51006fc44626ab5a651ca1ad2dad5a312e0"


def require(condition,detail):
    if not condition:raise ValueError(detail)


def one_sided_binomial_upper(k,n,alpha=.05):
    """Exact iid binomial upper confidence bound; sampling assumptions explicit."""
    require(0<=k<=n and n>0,"invalid sample size")
    if k==n:return 1.
    low,high=0.,1.
    for _ in range(85):
        mid=(low+high)/2
        cdf=sum(math.comb(n,j)*mid**j*(1-mid)**(n-j) for j in range(k+1))
        if cdf>alpha:low=mid
        else:high=mid
    return high


def validate(root:Path):
    names=list(root.rglob("bayes_same_public_*_original8.json"))
    require(len(names)==8,"MISSING_OR_DUPLICATED_ORIGINAL_PHYSX_SHARDS")
    require({p.name for p in names}==set(ORIGINAL_SHA),"SOURCE_FILE_SET_CHANGED")
    rows=[]
    for path in sorted(names):
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest==ORIGINAL_SHA[path.name],"SOURCE_SHA256_CHANGED "+path.name)
        parts=path.stem.split("_")
        task="pull_cube" if "_pull_cube_" in path.name else "stack_cube"
        chunk=int(path.stem.rsplit("chunk",1)[1].split("_")[0])
        label,start,model=MODEL[task]
        expected=list(range(start+8*chunk,start+8*chunk+8))
        d=json.loads(path.read_text())
        require(d.get("schema")=="frozen_ppo_matched_prefix_native_2x2_four_truth_v1"
                and d.get("real_physx_simulator") is True
                and d.get("frozen_model_retrained") is False
                and d.get("matched_prefix_causal_information_ablation") is True
                and d.get("original_external_frozen_checkpoint_sha256")==model
                and d.get("task")==label
                and d.get("original_seed_population")==expected
                and d.get("frozen_protocol")=="research/MATCHED_PUBLIC_BAYES_NEW64_PREOUTCOME_V1.json",
                "SOURCE_MODEL_PROTO_PHYSICS_IDENTITY_CHANGED")
        episodes=d.get("episodes",[])
        require(len(episodes)==8 and [x.get("seed") for x in episodes]==expected,"SOURCE_EPISODE_DROP")
        audit=path.with_name(path.name.replace("_original8.json","_audit.json"))
        require(audit.exists(),"INDEPENDENT_ORIGINAL_SHARD_AUDIT_MISSING")
        shard=json.loads(audit.read_text())
        require(shard.get("exact_original_PhysX_JSON_SHA256")==digest
                and shard.get("pre_registered_protocol_git_blob")=="9c758954f28cd0f3a99480f43828ab2a024c805a"
                and shard.get("original_nonrefit_runner_git_blob")=="6e039af56006827fc2fe063b541cfa3dcd1ddc89"
                and shard.get("exact_prechoice_physical_command_AND_SE3_prefix_match") is True,
                "ORIGINAL_METHOD_OR_PHYSICAL_PREFIX_PROVENANCE_CHANGED")
        for e in episodes:
            seed=e["seed"]
            truth=(("applied" if (seed-1)%4 in (1,3) else "held"),
                   ("applied" if (seed-1)%4 in (2,3) else "held"))
            require((e["original_precommitted_physical_t2_execution_truth"],
                     e["original_precommitted_physical_t3_execution_truth"])==truth,"ACTUAL_2X2_TRUTH_CHANGED")
            for key in ("matched_prefix_physical_audit","matched_posterior_prefix_audit"):
                v=e.get(key,{})
                require(v.get("valid_exact_prefix") is True and
                        v.get("audit_only_hidden_target_not_a_method_input") is True and
                        len(v.get("native_fault_dispatch_linf_each",[]))==2 and
                        max(*v["native_fault_dispatch_linf_each"],
                            *(v.get(k,float("inf")) for k in (
                             "pre_t5_achieved_position_max_abs_m",
                             "pre_t5_achieved_orientation_geodesic_rad",
                             "pre_t5_target_position_max_abs_m",
                             "pre_t5_target_orientation_geodesic_rad")) )<=5e-5,
                        "NOT_IDENTICAL_NATIVE_PRECHOICE_PHYSICS")
            for arm in ARMS:
                require(type(e["success_once"].get(arm)) is bool,"TASK_FLAG_MISSING")
                read=e["privileged_target_readback_decision_count"].get(arm)
                require(type(read) is int and 0<=read<=1,"SOURCE_PRIVATE_READ_CORRUPTED")
                cost=e["public_motion_observation_cost_samples"].get(arm)
                require(cost==(0 if arm==C else 2),"PUBLIC_DATA_BUDGET_NOT_MATCHED")
                require([v.get("step") for v in e["faults"].get(arm,[])]==[2,3],
                        "ONE_OF_TWO_PHYSICS_FAULTS_NOT_EXPOSED")
            for arm,key in ((A,"public_t3_evidence"),(B,"same_sensor_posterior_evidence")):
                v=e.get(key,{})
                require(type(v.get("authorized")) is bool and
                        type(v.get("wrong_confident")) is bool and
                        v.get("audit_only_hidden_target_was_NOT_decision_input") is True,
                        "HIDDEN_TRUTH_OR_CONFIDENCE_LEDGER_MISSING")
                require(e["privileged_target_readback_decision_count"][arm]==int(not v["authorized"]),
                        "PRIVATE_QUERY_NOT_CHARGED")
                require(not v["wrong_confident"] or v["authorized"],
                        "WRONG_CONFIDENT_WITHOUT_AUTHORIZATION")
                if arm==B:
                    w=v.get("posterior_weights",[])
                    require(len(w)==len(v.get("candidate_residuals_m",[])) and
                            abs(sum(w)-1)<1e-5 and v.get("posterior_threshold_predeclared")==.95,
                            "RESIDUAL_WEIGHT_HEURISTIC_MUTATED")
            rows.append((task,e))
    require(len(rows)==64 and len({(t,e["seed"]) for t,e in rows})==64,"NOT_64_INDEPENDENT_RESET_IDENTIFIERS")
    grouped=defaultdict(list)
    for task,e in rows:
        truth="/".join([e["original_precommitted_physical_t2_execution_truth"],
                        e["original_precommitted_physical_t3_execution_truth"]])
        grouped[f"{task}/{truth}"].append(e)
    require(len(grouped)==8 and all(len(v)==8 for v in grouped.values()),"FOUR_TRUTH_STRATA_NOT_BALANCED")
    def stats(es):
        return {name:{
            "official_task_success":sum(e["success_once"][name] for e in es),
            "privileged_decision_target_reads":sum(e["privileged_target_readback_decision_count"][name] for e in es),
            "public_xyz_sample_events":sum(e["public_motion_observation_cost_samples"][name] for e in es),
            "confident_histories":sum(e[k]["authorized"] for e in es) if k else 0,
            "wrong_confident_histories":sum(e[k]["wrong_confident"] for e in es) if k else 0}
            for name,k in ((A,"public_t3_evidence"),(B,"same_sensor_posterior_evidence"),(C,None))}
    allv=stats([e for _,e in rows])
    require([allv[x]["official_task_success"] for x in ARMS]==[52,52,52],"TASK_SUCCESS_COUNT_MUTATED")
    require([allv[x]["privileged_decision_target_reads"] for x in ARMS]==[48,63,64],"PRIVATE_READ_COUNT_MUTATED")
    require([allv[x]["wrong_confident_histories"] for x in ARMS]==[1,0,0],"CONFIDENT_FAILURE_REMOVED")
    wrong=[{"task":t,"seed":e["seed"],
            "selected_history_index":e["public_t3_evidence"]["selected_candidate_index"],
            "actual_compatible_history_indices":e["public_t3_evidence"]["audit_only_true_candidate_indices"],
            "official_task_success":e["success_once"][A],
            "candidate_residuals_m":e["public_t3_evidence"]["candidate_residuals_m"]}
          for t,e in rows if e["public_t3_evidence"]["wrong_confident"]]
    require(len(wrong)==1 and wrong[0]["seed"]==1760020 and
            wrong[0]["selected_history_index"]==0 and
            wrong[0]["actual_compatible_history_indices"]==[3],"WRONG_LABEL_SOURCE_WITNESS_HIDDEN")
    n=allv[A]["confident_histories"]
    result={
        "status":"ORIGINAL_PHYSX_SOURCE_VERIFIED_NOT_INDEPENDENT_REEXECUTION",
        "original_actions_run":ORIGINAL_RUN,"original_head":ORIGINAL_HEAD,
        "original_reset_states":64,"original_native_physx_controller_worlds":640,
        "source_original_json_sha256":ORIGINAL_SHA,
        "methods":{"A":"complete_history_set_unique_or_read","B":"same_two_XYZ_heuristic_normalized_residual_weight_095_or_read","C":"mandatory_target_read"},
        "all_original_64":stats([e for _,e in rows]),
        "stratified_eight_task_x_two_ACK_truth":{k:stats(v) for k,v in sorted(grouped.items())},
        "paired_task_success_A_vs_C":{
            "both_success":sum(e["success_once"][A] and e["success_once"][C] for _,e in rows),
            "both_failure":sum(not e["success_once"][A] and not e["success_once"][C] for _,e in rows),
            "A_only":sum(e["success_once"][A] and not e["success_once"][C] for _,e in rows),
            "C_only":sum(not e["success_once"][A] and e["success_once"][C] for _,e in rows),
        },
        "wrong_confident_source_episode":wrong,
        "empirical_wrong_given_confident_A":"1/16",
        "one_sided_iid_exact_95pct_upper_wrong_rate_conditional_on_acceptance_A":
            one_sided_binomial_upper(1,n),
        "same_public_sample_events_A_and_B":128,
        "private_read_equivalent_price_per_public_XYZ_sample_A_vs_C":16/128,
        "private_read_equivalent_price_per_public_XYZ_sample_B_vs_C":1/128,
        "limitations":["A single mistaken history can coexist with successful task completion.",
            "A/C binary task outcomes match in only 64 reset states; no population noninferiority.",
            "Empirical confidence is NOT calibrated safe execution; iid bound assumes future accepted labels are exchangeable.",
            "All worlds from one Panda controller family and two released PPOs.",
            "Same physically stepped neutral probe; it has actuation/time cost not priced by the read-only break-even.",
            "A/B shared public samples but C lacks decision-visible public history; read vs sample prices not directly equivalent.",
            "B is an uncalibrated residual weighting heuristic, NOT the official ActionShift DualABI.",
            "No external investigator actually replayed physics and no real network acknowledgement or hardware safety claim."]
    }
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=validate(a.source_dir)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("COMPLETE_VERIFIED_ORIGINAL640",json.dumps({
        "total_success_A_B_C":[result["all_original_64"][x]["official_task_success"] for x in ARMS],
        "target_reads_A_B_C":[result["all_original_64"][x]["privileged_decision_target_reads"] for x in ARMS],
        "A_wrong":result["wrong_confident_source_episode"],
        "accepted_error_upper_if_iid":result["one_sided_iid_exact_95pct_upper_wrong_rate_conditional_on_acceptance_A"],
        "paired":result["paired_task_success_A_vs_C"]},sort_keys=True))


if __name__=="__main__":main()
