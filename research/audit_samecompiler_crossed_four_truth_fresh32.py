"""Separate SHA-checked all-128 native physically stepped same-source 4-ACK truth auditor.

The nine controllers are instantiated and physically stepped in EACH of 128
task-seed/truth cells. This is author-run source-only review, not new physics,
not VLA fault recovery and not a proof of task noninferiority.
"""
from __future__ import annotations
import argparse,hashlib,json,math,random
from collections import defaultdict
from pathlib import Path

TASKS={"pull_cube":("PullCube-v1",3710001),"stack_cube":("StackCube-v1",3720001)}
A="fault_public_t3_fourhistory_or_t4_query"
B="fault_always_single_privileged_query"
TRUTHS={0:("held","held"),1:("applied","held"),2:("held","applied"),3:("applied","applied")}
EXPECTED_SOURCE={
    "pull_cube":"74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
    "stack_cube":"e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
}
def fullname(task,chunk):
    return f"samecompiler_crossed_{task}_chunk{chunk}_original16.json"

def as_finite_vec(x,expected_n=None):
    if not isinstance(x,list) or not x or (expected_n is not None and len(x)!=expected_n):
        raise ValueError("PHYSX_FOUR_TRUTH_MISSING_INITIAL_STATE_VECTOR")
    if not all(type(y) in (int,float) and math.isfinite(y) for y in x):
        raise ValueError("PHYSX_NONFINITE_INITIAL_VECTOR")
    return tuple(float(v) for v in x)

def physical_originals(root):
    actual={p.name for p in root.glob("samecompiler_crossed_*_original16.json")}
    expected={fullname(t,c) for t in TASKS for c in range(4)}
    if actual!=expected:
        raise ValueError(f"NOT_ALL_8_ORIGINAL_CROSS_ACK_PHYSX_SHARDS extra={sorted(actual-expected)} absent={sorted(expected-actual)}")
    groups=defaultdict(dict);digests=[]
    for t,(task_name,start) in TASKS.items():
        for chunk in range(4):
            p=root/fullname(t,chunk)
            raw=p.read_bytes()
            obj=json.loads(raw)
            ids=list(range(start+4*chunk,start+4*chunk+4))
            if (obj.get("schema")!="full_4_true_ack_same_source_seed_shared_compiler_physx_v1"
                or obj.get("preoutcome_protocol")!="research/SAME_COMPILER_CROSSED_4ACK_FRESH32_PREOUTCOME_V1.json"
                or obj.get("task")!=task_name or obj.get("original_reset_seed_population")!=ids
                or obj.get("complete") is not True or obj.get("original_episode_fail_closed_error") is not None
                or obj.get("physically_completed_trial_count")!=16
                or obj.get("frozen_model_retrained") is not False
                or obj.get("real_physx_simulator") is not True
                or obj.get("original_external_frozen_checkpoint_sha256")!=EXPECTED_SOURCE[t]
                or obj.get("full_shard_expected_physical_worlds")!=144
                or len(obj.get("episodes",[]))!=16):
                raise ValueError(f"INVALID_OR_INCOMPLETE_NATIVE_PHYSICS shard={p.name}")
            if [(z["seed"],z["physical_truth_index_forced_AUDIT_ONLY"]) for z in obj["episodes"]] != [
                (seed,truth) for seed in ids for truth in range(4)]:
                raise ValueError("Original registered complete per-seed truth schedule changed")
            digests.append({"file":p.name,"sha256":hashlib.sha256(raw).hexdigest(),"task":t,"first":ids[0]})
            for r in obj["episodes"]:
                key=(t,r["seed"])
                truth=r["physical_truth_index_forced_AUDIT_ONLY"]
                if truth in groups[key]:
                    raise ValueError("Duplicate original task/seed/ACK truth")
                if tuple(r[k] for k in ("original_precommitted_physical_t2_execution_truth",
                                        "original_precommitted_physical_t3_execution_truth"))!=TRUTHS[truth]:
                    raise ValueError("Incorrect actual physically applied/held t2/t3 ACK truth")
                groups[key][truth]=r
    if len(groups)!=32 or any(len(g)!=4 for g in groups.values()):
        raise ValueError("Incomplete true four-history same-seed population")
    return groups,digests

def episode(task,seed,truth,r):
    if r["task"]!=TASKS[task][0] or r["seed"]!=seed:
        raise ValueError("Task reset source misattributed")
    success=r["success_once"];reads=r["privileged_target_readback_decision_count"]
    if not all(type(success.get(n)) is bool and type(reads.get(n)) is int and reads[n] in (0,1) for n in (A,B)):
        raise ValueError("Unreliable task outcome or actual charged privileged target reads")
    if max([0]+list(r.get("initial_obs_diff",{}).values()))>5e-4:
        raise ValueError("Nine native world projected reset views not equal")
    xf=r["faults"].get(A,[]);yf=r["faults"].get(B,[])
    enough=(len(xf)==2 and len(yf)==2 and [f["step"] for f in xf]==[2,3]
            and [f["step"] for f in yf]==[2,3])
    pp=r.get("matched_prefix_physical_audit",{})
    matched=False
    if enough:
        if not (pp.get("valid_exact_prefix") is True and
                pp.get("audit_only_hidden_target_not_a_method_input") is True):
            raise ValueError("Public versus fixed physical prefix trace absent")
        diffs=[]
        for x,y in zip(xf,yf):
            av=as_finite_vec(x.get("actual_native_6d_dispatched"),6)
            bv=as_finite_vec(y.get("actual_native_6d_dispatched"),6)
            if x.get("step")!=y.get("step"):
                raise ValueError("Actually executed ACK faults not in same time")
            if x.get("actual_native_precommitted_execution_truth")!=y.get("actual_native_precommitted_execution_truth"):
                raise ValueError("Native true ACK status differs between methods")
            diffs.append(max(abs(a-b) for a,b in zip(av,bv)))
        if any(abs(a-b)>1e-8 for a,b in zip(diffs,pp["native_fault_dispatch_linf_each"])):
            raise ValueError("Frozen predecision original physical action source contradicts declared audit")
        for field in ("pre_t5_achieved_position_max_abs_m","pre_t5_achieved_orientation_geodesic_rad",
                      "pre_t5_target_position_max_abs_m","pre_t5_target_orientation_geodesic_rad"):
            val=pp.get(field)
            if type(val) not in (float,int) or not math.isfinite(val) or val>5e-5:
                raise ValueError("Predecision native achieved/target six-axis pose parity failed")
        matched=max(diffs)<=5e-5
    # This trace is generated by the ACTUAL native controller runner, not
    # inferred from task-level success. The two interventions must invoke the
    # same post-query state container and exact native inverse-compiler API.
    compiled=r.get("postquery_shared_compiler_trace",{})
    good_compiler="base.normalized_target_delta:approximate=True:old_override=single_belief_pose"
    for n in (A,B):
        for trace in compiled.get(n,[]):
            if (trace.get("compiler")!=good_compiler
                or trace.get("state_container")!="UncertainDeliveryBelief"
                or trace.get("acknowledge_path")!="prepare_acknowledge_common_for_all_postquery_steps"
                or trace.get("step",0)<5):
                raise ValueError("POSTDECISION_COMPILER_OR_BELIEF_IMPLEMENTATION_DIVERGED")
    if enough and not all(len(compiled.get(n,[]))>=1 for n in (A,B)):
        raise ValueError("Missing actual paired physical postdecision shared compiler trace")
    ev=r.get("public_t3_evidence",{})
    neutral=r.get("shared_neutral_probe_step4",{})
    an=neutral.get(A);bn=neutral.get(B)
    paid=r["public_motion_observation_cost_samples"].get(A,0)
    both_probe=(isinstance(an,dict) and isinstance(bn,dict)
       and an.get("physically_dispatched") is True and bn.get("physically_dispatched") is True
       and an.get("native_six_dim_arm")==[0.]*6 and bn.get("native_six_dim_arm")==[0.]*6
       and an.get("known_delivered_no_new_unknown_ack") is True
       and bn.get("known_delivered_no_new_unknown_ack") is True)
    confident=ev.get("authorized") is True
    wrong=ev.get("wrong_confident") is True
    if wrong and not confident:
        raise ValueError("Wrong history counted without a confident admission")
    if both_probe:
        if paid!=2 or reads[B]!=1 or reads[A]!=int(not confident):
            raise ValueError("Public or private state budget not faithfully charged")
        if ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True:
            raise ValueError("Leaked hidden native target into public method")
        if len(ev.get("audit_only_true_candidate_indices",[]))!=1:
            raise ValueError("Actual native hidden memory truth not in frozen hypothesis set")
        if wrong != (confident and ev.get("selected_candidate_index") not in ev["audit_only_true_candidate_indices"]):
            raise ValueError("Incorrect native truth confidence audit")
    else:
        if paid not in (0,1,2):
            raise ValueError("Public sensor sample cost invalid")
    return {
      "task":task,"seed":seed,"physical_truth_index":truth,
      "truth":"/".join(TRUTHS[truth]),
      "public_success":success[A],"fixed_success":success[B],
      "public_native_private_reads":reads[A],"fixed_native_private_reads":reads[B],
      "public_xyz_observation_sample_events":paid,
      "public_admitted_confident_history":confident,
      "audit_wrong_confident":wrong,
      "actually_reached_both_unknown_ACK_events":enough,
      "public_and_fixed_step4_neutral_probe_both_reached":both_probe,
      "actual_matched_native_fault_motor_and_achieved_target_before_t5":matched
    }

def percentiles(xs,p):
    a=sorted(xs)
    k=(len(a)-1)*p
    lo=int(k); hi=min(lo+1,len(a)-1)
    return a[lo]*(hi-k)+a[hi]*(k-lo)

def audit(root:Path):
    groups,digests=physical_originals(root)
    original_rows=[];seed_checks=[]
    all_hash_identical=0
    for (task,seed),g in sorted(groups.items()):
        arrays=[as_finite_vec(g[t]["initial_source_public_observation_f32"]) for t in range(4)]
        poses=[as_finite_vec(g[t]["initial_source_ee_pose7_xyz_xyzw"],7) for t in range(4)]
        if len({len(x) for x in arrays})!=1:
            raise ValueError("Seed's physical initial observation dimension differs by ACK truth")
        max_public=max(abs(a-b) for x in arrays[1:] for a,b in zip(arrays[0],x))
        max_ee=max(abs(a-b) for x in poses[1:] for a,b in zip(poses[0],x))
        if max_public>5e-5 or max_ee>5e-5:
            raise ValueError(f"SAME_SEED_DIFFERENT_PHYSICAL_INITIAL_STATE_NOT_CAUSAL task={task} seed={seed} diff={max_public}/{max_ee}")
        sha_same=len({g[t]["initial_source_physical_obs_sha256"] for t in range(4)})==1
        all_hash_identical+=int(sha_same)
        seed_checks.append({"task":task,"seed":seed,"all_four_truth_initial_sha_equal":sha_same,
           "largest_original_public_init_float_difference":max_public,"largest_source_ee_pose_component_difference":max_ee})
        for t in range(4):
            original_rows.append(episode(task,seed,t,g[t]))
    if len(original_rows)!=128 or len(digests)!=8:
        raise ValueError("Incomplete registered actual physical factorial")
    def stats(q):
        return {"n":len(q),
            "public_success":sum(x["public_success"] for x in q),
            "fixed_success":sum(x["fixed_success"] for x in q),
            "public_native_private_reads":sum(x["public_native_private_reads"] for x in q),
            "fixed_native_private_reads":sum(x["fixed_native_private_reads"] for x in q),
            "public_native_XYZ_samples":sum(x["public_xyz_observation_sample_events"] for x in q),
            "public_authorized":sum(x["public_admitted_confident_history"] for x in q),
            "public_wrong_confident":sum(x["audit_wrong_confident"] for x in q),
            "both_success":sum(x["public_success"] and x["fixed_success"] for x in q),
            "neither_success":sum(not x["public_success"] and not x["fixed_success"] for x in q),
            "public_only":sum(x["public_success"] and not x["fixed_success"] for x in q),
            "fixed_only":sum(x["fixed_success"] and not x["public_success"] for x in q),
            "matched_t2_t3_actual_native_motor_and_se3":sum(x["actual_matched_native_fault_motor_and_achieved_target_before_t5"] for x in q),
            "shared_physical_t4_neutral_probe":sum(x["public_and_fixed_step4_neutral_probe_both_reached"] for x in q),
            "both_physically_executed_ACK_interventions":sum(x["actually_reached_both_unknown_ACK_events"] for x in q),
        }
    overall=stats(original_rows)
    # Fail-close causal claim: any early refusal is preserved in the source, but
    # the ALL-population matched comparator attribution is not certified.
    causal_all=(
      overall["matched_t2_t3_actual_native_motor_and_se3"]==128
      and overall["shared_physical_t4_neutral_probe"]==128
      and overall["both_physically_executed_ACK_interventions"]==128
    )
    if not causal_all:
        raise ValueError("REAL_PHYSX_ALL128_MATCHED_QUERY_CAUSAL_POPULATION_INVALID source has early refusal or motor/pose mismatch; report as invalid, not cherry-pick")
    # Original four ACK-truth conditions from same seed are statistically
    # dependent. Illustrative seeded cluster-bootstrap only, not randomization.
    pairs=defaultdict(list)
    for row in original_rows:
        pairs[(row["task"],row["seed"])].append(row)
    blocks=list(pairs.values())
    rng=random.Random(20261009)
    boot=[]
    for i in range(10000):
        sample=[blocks[rng.randrange(len(blocks))] for _ in range(len(blocks))]
        val=sum(int(r["public_success"])-int(r["fixed_success"]) for block in sample for r in block)
        boot.append(val/128.0)
    return {
     "schema":"ORIGINAL_1152_PHYSX_FRESH32_FULL4ACK_COMMON_COMPILER_PHYSICAL_CAUSAL_AUDIT_V1",
     "genuine_original_native_PhysX_controller_worlds":1152,
     "registered_source_seed_clusters":32,
     "original_physical_task_truth_cells":128,
     "full_original_source_SHA256":digests,
     "same_source_seed_four_truth_numeric_parity_verified":True,
     "initial_public_identical_SHA_clusters":all_hash_identical,
     "source_initial_floats_max_abs":max(x["largest_original_public_init_float_difference"] for x in seed_checks),
     "source_initial_achieved_EE_pose_max_abs":max(x["largest_source_ee_pose_component_difference"] for x in seed_checks),
     "original_all_population_exact_motor_and_downstream_compiler_comparison_verified":causal_all,
     "all128":overall,
     "task":{"pull_cube":stats([x for x in original_rows if x["task"]=="pull_cube"]),
             "stack_cube":stats([x for x in original_rows if x["task"]=="stack_cube"])},
     "physical_ACK_truth_strata":{str(t):stats([x for x in original_rows if x["physical_truth_index"]==t]) for t in range(4)},
     "source_seed_cluster_bootstrap_95_percentile_public_minus_fixed_success_not_NI_proof":[percentiles(boot,.025),percentiles(boot,.975)],
     "all_source_original_episode_records":original_rows,
     "per_source_seed_four_ACK_initial_parity":seed_checks,
     "all_32_clustering_not_128_independent_resets":True,
     "policy_and_native_controller_family":"two frozen PPOs, Panda target-relative native PhysX chart only",
     "one_nonzero_active_probe_not_tested":True,
     "unseen_external_investigator_replication":False,
     "not_certified_safety_or_noninferiority":True,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    v=audit(args.source_dir)
    args.output.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("ACTUAL_1152_MATCHED_PREPREFIX_AND_POSTQUERY_COMPILER_CROSSED_REAL_PHYSX",json.dumps({
        "total_physical_worlds":v["genuine_original_native_PhysX_controller_worlds"],
        "original_seeds":v["registered_source_seed_clusters"],
        "original_fourtruth_cells":v["original_physical_task_truth_cells"],
        "public_vs_fixed":v["all128"],
        "seed_cluster_bootstrap95":v["source_seed_cluster_bootstrap_95_percentile_public_minus_fixed_success_not_NI_proof"],
        "exact_SHA_matched_initial":v["initial_public_identical_SHA_clusters"]},sort_keys=True))
if __name__=="__main__":main()
