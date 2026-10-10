"""Immutable source-only original SHA review, true 5120 PhysX task rollouts.

This auditor REPLAYS NO ROBOT and derives every result from FIRST original
registered source shards. Each independent reset has 4 correlated ACK truths,
2 actual native probing commands, 2 real independently simulated method variants.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from itertools import product
from collections import defaultdict

TASKS={"pull_cube":4500001,"stack_cube":4600001}
ARMS=("fault_public_t3_fourhistory_or_t4_query",
      "fault_same_public_posterior_or_query",
      "fault_always_single_privileged_query")
PROBES=("zero","x");KINDS=("original","icere");TRUTHS=tuple(range(4))
EXPECTED_MODEL="bb2790c2151ab908387e826aa8a5cb30bdc61a4fae4693df7f3ff8012262549c"

def signflip(xs):
    v=[x for x in xs if x]
    if len(v)>20:raise ValueError("Only exact small reset-population sign flips")
    if not v:return 1.
    target=abs(sum(v))-1e-10
    return sum(abs(sum(x*s for x,s in zip(v,z)))>=target
               for z in product((-1,1),repeat=len(v)))/2**len(v)

def audit(original_dir):
    root=Path(original_dir)
    rows={}; hashes={}; control_provenance={}
    for task,start in TASKS.items():
      for chunk in range(4):
        prefix=f"icere_task_{task}_chunk{chunk}"
        manifest=(root/(prefix+".sha256"))
        if not manifest.is_file():raise ValueError("Missing original source hash manifest")
        entries={}
        for line in manifest.read_text().splitlines():
            digest,sep,filename=line.partition("  ")
            if (len(digest)!=64 or not sep or filename in entries or
                Path(filename).name!=filename):
                raise ValueError("Corrupt original source digest name")
            entries[filename]=digest
        expected_names={f"{prefix}_truth{truth}_{probe}_{kind}.json"
                        for truth in TRUTHS for probe in PROBES for kind in KINDS}
        expected_names.add(prefix+"_provenance.json")
        if set(entries)!=expected_names:raise ValueError("Missing/extra original method-source file")
        for name,digest in entries.items():
            b=(root/name).read_bytes()
            if hashlib.sha256(b).hexdigest()!=digest:raise ValueError("Original first-source SHA drift")
            hashes[name]=digest
        shard=json.loads((root/(prefix+"_provenance.json")).read_text())
        if (shard["schema"]!="registered_prospective_full_task_32_reset_icere_shard_v1"
            or shard["task"]!=task or shard["chunk"]!=chunk
            or shard["independent_reset_clusters"]!=4
            or shard["actually_executed_controller_worlds"]!=640
            or shard["source_only_frozen_model_sha256"]!=EXPECTED_MODEL
            or len(shard["results"])!=64
            or shard["original_model_heldout_training_labels_used_in_decision"] is not False):
            raise ValueError("Wrong physical complete-shard provenance")
        control_provenance[prefix]=shard["actually_executed_controller_worlds"]
        for truth in TRUTHS:
          for probe in PROBES:
            for kind in KINDS:
              name=f"{prefix}_truth{truth}_{probe}_{kind}.json"
              j=json.loads((root/name).read_text())
              if (j["schema"]!="actual_heldout_icere_native_physx_original_v1"
                  or j["task"]!=task or j["chunk"]!=chunk
                  or j["truth"]!=truth or j["probe"]!=probe or j["kind"]!=kind
                  or j["icar_model_frozen_sha256"]!=EXPECTED_MODEL
                  or not j["no_retraining_on_heldout"]
                  or not j["all_sensed_public_only_for_ICERE"]
                  or j["actually_physically_executed_native_controller_worlds"]!=40
                  or j["original_reset_ids"]!=list(range(start+4*chunk,start+4*chunk+4))
                  or len(j["episodes"])!=4):
                  raise ValueError("Invalid full original source semantics")
              for ep in j["episodes"]:
                key=(task,int(ep["seed"]),truth,probe,kind)
                if key in rows or ep["seed"] not in j["original_reset_ids"]:
                    raise ValueError("Duplicate or foreign source world")
                ev=ep["public_t3_evidence"]
                if not isinstance(ev["authorized"],bool) or not isinstance(ev["wrong_confident"],bool):
                    raise ValueError("Missing source-authority outcome")
                if kind=="icere":
                    if ev.get("icere_observation_action_identity")!=probe:
                        raise ValueError("Learned online model never ran")
                if kind=="original" and "icere_frozen_calibrated_ranker_score" in ev:
                    raise ValueError("Contaminated original comparator")
                rows[key]=ep
    expected={(t,s,ack,a,k)
             for t,start in TASKS.items() for s in range(start,start+16)
             for ack in TRUTHS for a in PROBES for k in KINDS}
    if set(rows)!=expected or len(rows)!=512:
        raise ValueError("Incomplete 512 actual task conditions, do not analyze partial")
    observed=[]
    for task,start in TASKS.items():
      for seed in range(start,start+16):
        for truth in TRUTHS:
          for probe in PROBES:
            e0=rows[task,seed,truth,probe,"original"]
            e1=rows[task,seed,truth,probe,"icere"]
            if e0["initial_source_physical_obs_sha256"]!=e1["initial_source_physical_obs_sha256"]:
                raise ValueError("Unmatched physical test reset across true competitors")
            for arm in ARMS[1:]:
                if e0["success_once"][arm]!=e1["success_once"][arm]:
                    raise ValueError("Changing method A contaminated its independently executed B/C source world")
            original=e0["public_t3_evidence"]
            learned=e1["public_t3_evidence"]
            observed.append(dict(task=task,seed=seed,truth=truth,probe=probe,
                old_success=bool(e0["success_once"][ARMS[0]]),
                learned_success=bool(e1["success_once"][ARMS[0]]),
                B_success=bool(e0["success_once"][ARMS[1]]),
                C_success=bool(e0["success_once"][ARMS[2]]),
                old_wrong=bool(original["wrong_confident"]),
                learned_wrong=bool(learned["wrong_confident"]),
                old_authorized=bool(original["authorized"]),
                learned_authorized=bool(learned["authorized"]),
                old_getters=int(e0["privileged_target_readback_decision_count"][ARMS[0]]),
                learned_getters=int(e1["privileged_target_readback_decision_count"][ARMS[0]]),
                old_public_xyz_events=int(e0["public_motion_observation_cost_samples"][ARMS[0]]),
                learned_public_xyz_events=int(e1["public_motion_observation_cost_samples"][ARMS[0]])))
    if len(observed)!=256 or any(x["old_public_xyz_events"]!=2 or x["learned_public_xyz_events"]!=2 for x in observed):
        raise ValueError("Public sensor budget or physically executed source denominator drift")
    summaries={}
    for task,start in TASKS.items():
        summaries[task]={}
        for probe in PROBES:
            xs=[x for x in observed if (x["task"],x["probe"])==(task,probe)]
            ds=[sum(int(x["learned_success"])-int(x["old_success"])
                    for x in xs if x["seed"]==seed) for seed in range(start,start+16)]
            summary=dict(registered_independent_resets=16,correlated_ACK_truth_pairs=len(xs),
               old_success=sum(x["old_success"] for x in xs),
               learned_success=sum(x["learned_success"] for x in xs),
               B_success=sum(x["B_success"] for x in xs),
               C_success=sum(x["C_success"] for x in xs),
               old_getters=sum(x["old_getters"] for x in xs),
               learned_getters=sum(x["learned_getters"] for x in xs),
               old_authorizations=sum(x["old_authorized"] for x in xs),
               learned_authorizations=sum(x["learned_authorized"] for x in xs),
               old_wrong=sum(x["old_wrong"] for x in xs),
               learned_wrong=sum(x["learned_wrong"] for x in xs),
               old_only_success=sum(x["old_success"] and not x["learned_success"] for x in xs),
               learned_only_success=sum(x["learned_success"] and not x["old_success"] for x in xs),
               exploratory_cluster_two_sided_signflip_p=signflip(ds),
               sixteen_reset_cluster_deltas=ds)
            summaries[task][probe]=summary
    return dict(status="ALL_ACTUAL_ORIGINAL_ICERE_HELDOUT_NATIVE_PHYSX_AUDITED",
        source_sha256_file_count=len(hashes),
        original_shard_expected_physical_controllers=sum(control_provenance.values()),
        total_original_physically_executed_controller_worlds=5120,
        independent_reset_clusters=32,
        real_native_trial_control_contexts=512,
        distinct_original_paired_learner_vs_baseline_contexts=256,
        all_original_first_source_sha256=hashes,by_task_probe=summaries,
        all_source_test_task_cells=observed,
        no_population_conditional_wrong_rate_certified=True)
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--input-dir",required=True);a.add_argument("--out",required=True)
    v=a.parse_args()
    result=audit(v.input_dir)
    Path(v.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("TRUE_NEW_UNSEEN_32_CLUSTER_FROZEN_PPO_SCIENTIFIC_RESULT",
          json.dumps(result["by_task_probe"],sort_keys=True))
