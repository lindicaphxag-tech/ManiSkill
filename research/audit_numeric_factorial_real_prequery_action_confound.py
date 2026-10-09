"""Pre-query action confounding / charged observation reviewer audit for 128 original PhysX cells.

In a different new seed cohort, public and task-aware arms may share t2 but apply
DIFFERENT t3 native actions BEFORE public t5 target-read decision; raw data prove it.
Task-success effects are therefore END-TO-END METHOD differences, not a pure
effect of resynchronization policy. Never erase this fact or count pre-query
actions as identical when actual six native command channels differ.
"""
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
from research.audit_numeric_parity_ack_factorial import audit

PUBLIC="fault_public_t3_fourhistory_or_t4_query"
PULL_STRONG="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
TASKS=("pull_cube","stack_cube")

def command(q,arm,step):
    rows=q.get("faults",{}).get(arm,[])
    d=next((x for x in rows if x.get("step")==step),None)
    if d is None:return None
    vec=d.get("actual_native_6d_dispatched")
    if not isinstance(vec,list) or len(vec)!=6:
        raise ValueError("Missing actual PhysX dispatched six dimensional native command")
    return [float(x) for x in vec]

def same(a,b):
    if a is None or b is None:return False
    return max(abs(x-y) for x,y in zip(a,b))<1e-6

def read_verified_sources(folder):
    base=audit(folder)
    if base["registered_task_seed_truth_cells"]!=128 or base["registered_source_reset_clusters"]!=32:
        raise ValueError("Not the strict same-initial observation factorial original")
    records=[]
    for task in TASKS:
        for chunk in range(2):
            for t in range(4):
                p=folder/f"factorial_{task}_chunk{chunk}_truth{t}_original8.json"
                d=json.loads(p.read_text())
                for q in d["episodes"]:
                    strong=PULL_STRONG if task=="pull_cube" else FIXED
                    probes=q.get("shared_neutral_probe_step4",{})
                    for n in (PUBLIC,strong,FIXED):
                        z=probes.get(n)
                        if (not isinstance(z,dict) or
                            z.get("physically_dispatched") is not True or
                            z.get("native_six_dim_arm")!=[0.0]*6 or
                            z.get("step")!=4 or
                            z.get("known_delivered_no_new_unknown_ack") is not True):
                            raise ValueError(f"Main actual method {n} did not pay identical physical t4 neutral probe on {task} {q['seed']} truth{t}")
                    expected=q.get("public_motion_observation_cost_samples",{}).get(PUBLIC)
                    if expected!=2:raise ValueError("Public source did not pay actual before/after achieved XYZ samples")
                    a2,a3=command(q,PUBLIC,2),command(q,PUBLIC,3)
                    b2,b3=command(q,strong,2),command(q,strong,3)
                    c2,c3=command(q,FIXED,2),command(q,FIXED,3)
                    if any(x is None for x in (a2,a3,b2,b3,c2,c3)):
                        raise ValueError("Actually injected native t2/t3 physical action absent; do not substitute nominal fault label")
                    records.append({
                       "task":task,"seed":q["seed"],"actual_execution_truth_condition":t,
                       "public_and_strong_t2_native_identical":same(a2,b2),
                       "public_and_strong_t3_native_identical":same(a3,b3),
                       "public_and_fixed_t2_native_identical":same(a2,c2),
                       "public_and_fixed_t3_native_identical":same(a3,c3),
                       "public_strong_fixed_t4_physically_neutral_steps_all_dispatched":True,
                       "public_before_after_achieved_xyz_samples_paid":2,
                       "method_successes":{
                          "public":q["success_once"][PUBLIC],
                          "strong":q["success_once"][strong],
                          "fixed":q["success_once"][FIXED]}
                    })
    if len(records)!=128:raise ValueError("Original episodes missing")
    summary={}
    for task in TASKS:
        for truth in range(4):
            rows=[r for r in records if r["task"]==task and r["actual_execution_truth_condition"]==truth]
            if len(rows)!=16:raise ValueError("Full task/truth physical 16 population missing")
            summary[f"{task}_truth{truth}"]={
                "n":16,
                "matched_public_vs_strong_t2":sum(r["public_and_strong_t2_native_identical"] for r in rows),
                "matched_public_vs_strong_t3":sum(r["public_and_strong_t3_native_identical"] for r in rows),
                "matched_public_vs_fixed_t2":sum(r["public_and_fixed_t2_native_identical"] for r in rows),
                "matched_public_vs_fixed_t3":sum(r["public_and_fixed_t3_native_identical"] for r in rows),
                "all_three_actual_neutral_probes_physically_identical":len(rows),
                "public_vs_strong_paired_task_discordances":sum(r["method_successes"]["public"]!=r["method_successes"]["strong"] for r in rows)}
    by={key:sum(r[key] for r in records) for key in (
        "public_and_strong_t2_native_identical",
        "public_and_strong_t3_native_identical",
        "public_and_fixed_t2_native_identical",
        "public_and_fixed_t3_native_identical"
    )}
    # This is a truly NEW original source cohort. Never assume its
    # physical action-parity counts match the older exposed 131/132 cohort.
    # All observed actions remain in the denominator whether equal or not.

    return {
       "schema":"fresh_numeric_parity_2x2_actual_native_prequery_action_confound_v2",
       "first_failed_first_round_ref":"37930607707",
       "source_numeric_new_all_green_ref":"37932361044",
       "numerical_initial_source_observations_matched_under_precommitted_tolerance":True,
       "original_actual_seed_clusters":32,
       "actual_source_truth_cells":128,
       "all_three_main_controllers_identical_physically_stepped_neutral_probe":128,
       "public_extra_achieved_xyz_sample_events":256,
       "native_dispatched_command_identical_counts":by,
       "per_task_truth":summary,
       "original_per_condition":records,
       "not_identical_actions_prior_to_decision_for_all_competitors": any(x<128 for x in by.values()),
       "scientific_claim":"The original task-success and private-read differences may include actually different native t3 motor commands BEFORE t5 information selection. Report counts as measured and do not attribute a task win solely to public target history information.",
       "zero_all_faulted_neutral_probe_not_relevant_to_three_main_comparators":"Strict-common-exact arm refuses earlier and does not probe; all THREE primary comparators actually probed 128/128.",
       "no_policy_superiority_established":"New disjoint 32-cluster exact two-sided sensitivity p=.0556640625 (> .05), as independently audited.",
       "source_truth_used_ONLY_for_audit_after_actual_PhysX":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=read_verified_sources(a.source_dir)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("NATIVE_2X2_PHYSICAL_ACTION_CONFOUND_AND_CHARGED_PROBE_AUDIT",
          json.dumps({"sample":128,"matched_counts":result["native_dispatched_command_identical_counts"],
          "all_three_neutral":result["all_three_main_controllers_identical_physically_stepped_neutral_probe"],
          "public_XYZ_extra":result["public_extra_achieved_xyz_sample_events"]},sort_keys=True))
if __name__=="__main__":main()
