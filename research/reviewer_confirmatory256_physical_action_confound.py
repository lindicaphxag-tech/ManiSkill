"""Pre-information physical action confound and true t3-HELD matched-prefix check.

This is source-only forensic of 256 previously physically stepped original
ManiSkill PPO trials. Never select/truncate individual cases based on outcome;
fault-truth strata are deterministic preassigned experiments. True ACK labels
are AUDIT ONLY, not used to select controller actions. Same early command
does not prove future action is identical; all paired outcomes are END-TO-END.
"""
from __future__ import annotations
import argparse,json,math,random
from collections import defaultdict
from pathlib import Path
from research.audit_confirmatory_four_truth_new64clusters import audit,exact_cluster_swap_p

PUBLIC="fault_public_t3_fourhistory_or_t4_query"
PULL_STRONG="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
TASKS=("pull_cube","stack_cube")

def six(q,name,step):
    fs=q.get("faults",{}).get(name,[])
    v=next((f.get("actual_native_6d_dispatched") for f in fs if f.get("step")==step),None)
    if not isinstance(v,list) or len(v)!=6 or any(not isinstance(x,(float,int)) or not math.isfinite(x) for x in v):
        raise ValueError("Actual physical controller command missing, not a real full 2-ACK exposure")
    return tuple(v)

def same(x,y):
    return max(abs(a-b) for a,b in zip(x,y))<=1e-6

def neutral(q,name):
    x=q.get("shared_neutral_probe_step4",{}).get(name,{})
    return x.get("step")==4 and x.get("physically_dispatched") is True and x.get("known_delivered_no_new_unknown_ack") is True and x.get("native_six_dim_arm")==[0.]*6

def quantile(xs,p):
    s=sorted(xs);k=(len(s)-1)*p;lo=int(k);z=k-lo
    return (1-z)*s[lo]+z*s[min(lo+1,len(s)-1)]

def audit_source(folder:Path):
    full=audit(folder)
    if full["registered_source_reset_clusters"]!=64 or full["registered_task_seed_truth_cells"]!=256:
        raise ValueError("Need all 64 original task-reset clusters and four real ACK truths")
    rows=[]
    for task in TASKS:
        for chunk in range(4):
            for t in range(4):
                d=json.loads((folder/f"factorial_{task}_chunk{chunk}_truth{t}_original8.json").read_text())
                for trial in d["episodes"]:
                    strong=PULL_STRONG if task=="pull_cube" else FIXED
                    commands={}
                    for n in (PUBLIC,strong,FIXED):
                        if not neutral(trial,n):
                            raise ValueError("Public/strong/fixed not all physically performed the same known-delivered t4 neutral action")
                        commands[n]={k:six(trial,n,k) for k in (2,3)}
                    if trial["physical_truth_index_factorial_condition_AUDIT_ONLY"]!=t:
                        raise ValueError("Truth index not original assigned intervention")
                    truth_t3="applied" if t in (2,3) else "held"
                    if trial["original_precommitted_physical_t3_execution_truth"]!=truth_t3:
                        raise ValueError("Original true second ACK falsified")
                    matched_AB={k:same(commands[PUBLIC][k],commands[strong][k]) for k in (2,3)}
                    matched_AC={k:same(commands[PUBLIC][k],commands[FIXED][k]) for k in (2,3)}
                    if truth_t3=="held" and not all(
                        all(abs(x)<1e-12 for x in commands[n][3]) for n in (PUBLIC,strong,FIXED)):
                        raise ValueError("Physically held t3 was not an actual all-zero native controller command")
                    rows.append({
                        "task":task,"seed":trial["seed"],"truth_index":t,
                        "true_t3_held_precommitted":truth_t3=="held",
                        "before_inference_t2_same_AB":matched_AB[2],
                        "before_inference_t3_same_AB":matched_AB[3],
                        "before_inference_t2_same_AC":matched_AC[2],
                        "before_inference_t3_same_AC":matched_AC[3],
                        "all_three_known_delivered_neutral_t4_physically_applied":True,
                        "all_three_target_before_t5_physical_prefix_actions_same_AB":all(matched_AB.values()),
                        "official_public_task_success":trial["success_once"][PUBLIC],
                        "official_strong_task_success":trial["success_once"][strong],
                        "official_fixed_task_success":trial["success_once"][FIXED],
                        "privileged_public_reads":trial["privileged_target_readback_decision_count"][PUBLIC],
                        "privileged_strong_reads":trial["privileged_target_readback_decision_count"][strong],
                        "privileged_fixed_reads":trial["privileged_target_readback_decision_count"][FIXED],
                        "public_achieved_XYZ_events":trial["public_motion_observation_cost_samples"][PUBLIC]
                    })
    if len(rows)!=256 or len({(r["task"],r["seed"],r["truth_index"]) for r in rows})!=256:
        raise ValueError("Repeated/missing source condition cells")
    def section(items):
        matched=defaultdict(list)
        for r in items:matched[(r["task"],r["seed"])].append(r)
        # Cluster all repeated true-ACK conditions by 64 physical initial resets.
        vals=[sum(int(r["official_public_task_success"])-int(r["official_strong_task_success"]) for r in z) for z in matched.values()]
        rng=random.Random(20261009)
        n=len(matched);clusters=list(matched.values())
        boots=[]
        for i in range(5000):
            draw=[clusters[rng.randrange(n)] for _ in range(n)]
            total=sum(len(z) for z in draw)
            boots.append(sum(int(r["official_public_task_success"])-int(r["official_strong_task_success"]) for z in draw for r in z)/total)
        return {
            "task_truth_cells":len(items),"different_original_seed_clusters":len(matched),
            "public_success":sum(r["official_public_task_success"] for r in items),
            "strong_success":sum(r["official_strong_task_success"] for r in items),
            "fixed_success":sum(r["official_fixed_task_success"] for r in items),
            "public_reads":sum(r["privileged_public_reads"] for r in items),
            "strong_reads":sum(r["privileged_strong_reads"] for r in items),
            "fixed_reads":sum(r["privileged_fixed_reads"] for r in items),
            "public_XYZ_event_count":sum(r["public_achieved_XYZ_events"] for r in items),
            "t2_AB_identical_native_command":sum(r["before_inference_t2_same_AB"] for r in items),
            "t3_AB_identical_native_command":sum(r["before_inference_t3_same_AB"] for r in items),
            "t2_AC_identical_native_command":sum(r["before_inference_t2_same_AC"] for r in items),
            "t3_AC_identical_native_command":sum(r["before_inference_t3_same_AC"] for r in items),
            "all_three_physically_same_neutral_t4":len(items),
            "all_preinformation_native_commands_AB_identical":sum(r["all_three_target_before_t5_physical_prefix_actions_same_AB"] for r in items),
            "public_only_success":sum(r["official_public_task_success"] and not r["official_strong_task_success"] for r in items),
            "strong_only_success":sum(r["official_strong_task_success"] and not r["official_public_task_success"] for r in items),
            "exact_cluster_sign_swap_two_sided_SENSITIVITY_p":exact_cluster_swap_p(vals),
            "exploratory_seed_cluster_95pct_bootstrap_difference":[quantile(boots,.025),quantile(boots,.975)]
        }
    sections={
       "original_full_256_all_exposed":section(rows),
       "preassigned_TRUE_second_ACK_HELD_128cells":section([r for r in rows if r["true_t3_held_precommitted"]]),
       "preassigned_TRUE_second_ACK_APPLIED_128cells":section([r for r in rows if not r["true_t3_held_precommitted"]]),
       "OBSERVATIONALLY_matched_native_t2_t3_AB_do_not_claim_random_subset":section([
           r for r in rows if r["all_three_target_before_t5_physical_prefix_actions_same_AB"]])
    }
    for t in TASKS:
        sections[t+"_ALL_true_patterns"]=section([r for r in rows if r["task"]==t])
    for t in (0,1,2,3):
        sections["physical_two_ACK_truth_"+str(t)]=section([r for r in rows if r["truth_index"]==t])
    if sections["original_full_256_all_exposed"]["public_success"]!=full["primary_outcomes"]["public"]["official_task_success"]:
        raise ValueError("Original end-to-end 256 source task success changed")
    return {
      "schema":"256_phyisically_true_ACK_predecision_native_command_confound_and_preassigned_HELD_t3_analysis_v1",
      "first_run_original_all32_shards":"37934425888",
      "source_only_unchanged_original_physx":True,
      "all_64_original_seed_clusters_and_four_physical_truths_required":True,
      "native_actions_read_from_physically_DISPATCHED_six_channels_not_labels":True,
      "t3_HELD_subgroup_is_PREASSIGNED_before_task_not_hindsight_matching":True,
      "observational_matched_action_subset_is_NOT_randomly_assigned":True,
      "actual_native_t2_t3_and_t4_steps_checked":True,
      "quasi_causal_differences_beyond_query_can_remain_after_t5":True,
      "subgroups":sections,
      "rows":rows,
      "cannot_attribute_all_overall_gain_solely_to_hidden_state_inference":True,
      "no_hardware_or_real_packetloss_or_learned_VLA_or_external_investigator":True
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    a=audit_source(args.source_dir)
    args.output.write_text(json.dumps(a,sort_keys=True,indent=2)+"\n")
    print("TRUE_256_PHYSX_ACTION_CONFOUND_CAUSAL_STRATA",json.dumps({k:{
        "n":v["task_truth_cells"],
        "public_success":v["public_success"],"strong_success":v["strong_success"],
        "native_t3_matched_AB":v["t3_AB_identical_native_command"],
        "native_t3_matched_AC":v["t3_AC_identical_native_command"],
        "p_exact":v["exact_cluster_sign_swap_two_sided_SENSITIVITY_p"],
        "success_delta_bootstrap95":v["exploratory_seed_cluster_95pct_bootstrap_difference"]}
        for k,v in a["subgroups"].items()},sort_keys=True))
if __name__=="__main__":main()
