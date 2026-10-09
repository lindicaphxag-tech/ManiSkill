"""Independent full-population source auditor for prospectively disjoint 64-state mixed ACK benchmark.

Do not mistake 576 simulator controller worlds for independent robots,
task policies or outside laboratories. All outcomes and failures retained.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from research.run_disjoint_mixed_ack_new64 import validate,select,PROTOCOL,PRECOMMITTED_BLOB

PUBLIC="fault_public_t3_fourhistory_or_t4_query"
SELECTIVE="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
HELD="fault_assume_held_without_query"

def audit(folder):
    wanted={f"disjoint_mixed_{task}_chunk{chunk}_{kind}.json"
        for task in ("pull_cube","stack_cube") for chunk in range(4)
        for kind in ("original8","audit")}
    found={p.name for p in folder.glob("disjoint_mixed_*.json")}
    if found!=wanted:raise ValueError(f"Original eight shards and eight audits required; missing={wanted-found} extraneous={found-wanted}")
    rows=[]; by_task={}
    for task in ("pull_cube","stack_cube"):
        sub=[]
        for chunk in range(4):
            original=folder/f"disjoint_mixed_{task}_chunk{chunk}_original8.json"
            raw=original.read_bytes()
            record=json.loads(raw)
            expected=validate(record,task,chunk)
            expected.update(schema="disjoint_mixed_ack_new64_shard_audit_v1",
                frozen_protocol_blob=PRECOMMITTED_BLOB,
                exact_original_physical_source_sha256=hashlib.sha256(raw).hexdigest(),
                original_physical_runner_blob="36e672446407435e656cbf8aba6fa2de7c1e9d0e")
            stored=json.loads((folder/f"disjoint_mixed_{task}_chunk{chunk}_audit.json").read_text())
            if stored!=expected:raise ValueError("Original PhysX shard and independent scorer disagree")
            sub.extend(expected["sample_rows"])
        expected_seeds=[x for chunk in range(4) for x in select(task,chunk)]
        if len(sub)!=32 or [x["seed"] for x in sub]!=expected_seeds:
            raise ValueError("Omitted or repeated original trial")
        strong=SELECTIVE if task=="pull_cube" else FIXED
        def arm(name):
            return {"success":sum(int(x["new_success"] if name==PUBLIC else
                         x["task_gate_success"] if name==strong else x["fixed_success"]) for x in sub),
                    "reads":sum(x["new_reads"] if name==PUBLIC else
                                x["task_gate_reads"] if name==strong else x["fixed_reads"] for x in sub)}
        # Separate actual nine-arm per-episode controls are verified by
        # validate() above. Keep all three primary comparison families.
        phase_stats={}
        for truth in ("applied","held"):
            pop=[x for x in sub if (x["seed"]%2==0)==(truth=="applied")]
            if len(pop)!=16:raise ValueError("One t2 truth stratum missing")
            phase_stats[truth]={"n":len(pop),
                "public_success":sum(int(x["new_success"]) for x in pop),
                "strong_success":sum(int(x["task_gate_success"]) for x in pop),
                "public_private_reads":sum(x["new_reads"] for x in pop),
                "strong_private_reads":sum(x["task_gate_reads"] for x in pop),
                "confident_public":sum(x["new_public_evidence"].get("authorized") is True for x in pop),
                "wrong_public":sum(x["new_public_evidence"].get("wrong_confident") is True for x in pop)}
        paired={"both":sum(x["new_success"] and x["task_gate_success"] for x in sub),
            "neither":sum(not x["new_success"] and not x["task_gate_success"] for x in sub),
            "new_only":sum(x["new_success"] and not x["task_gate_success"] for x in sub),
            "strong_only":sum(x["task_gate_success"] and not x["new_success"] for x in sub)}
        by_task[task]={"source_reset_states":32,"physically_stepped_controller_worlds":288,
                       "public_vs_strong_paired":paired,
                       "new_public":arm(PUBLIC),"strong_task_id":arm(strong),
                       "fixed_t4":arm(FIXED),
                       "true_t2_executed_strata":phase_stats}
        rows.extend(sub)
    if len(rows)!=64 or len(set((x["task"],x["seed"]) for x in rows))!=64:
        raise ValueError("Full 64 original seed denominator corrupted")
    ret={"schema":"disjoint_full64_physx_native_frozen_ppo_independent_source_audit_v1",
         "unseen_relative_to_earlier_860001_870032":True,
         "source_precommit_git_blob":PRECOMMITTED_BLOB,
         "physically_executed_actual_controller_worlds":576,
         "distinct_reset_states":64,
         "t2_applied":32,"t2_held":32,"t3_held":64,
         "true_joint_t2_t3_four_patterns_tested":False,
         "full_original_trial_records":rows,"by_task":by_task,
         "source_intended_not_automatic_external_reproduction":True}
    ret["outcomes"]={name:{"success":sum(by_task[t][name]["success"] for t in by_task),
                            "private_reads":sum(by_task[t][name]["reads"] for t in by_task)}
                      for name in ("new_public","strong_task_id","fixed_t4")}
    ret["public_confident"]=sum(
        by_task[t]["true_t2_executed_strata"][z]["confident_public"]
        for t in by_task for z in ("applied","held"))
    ret["wrong_confident"]=sum(
        by_task[t]["true_t2_executed_strata"][z]["wrong_public"]
        for t in by_task for z in ("applied","held"))
    ret["paired"]={label:sum(by_task[t]["public_vs_strong_paired"][label] for t in by_task)
                   for label in ("both","neither","new_only","strong_only")}
    return ret

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    d=audit(a.source_dir)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print("FULL_DISJOINT_64_ACTUAL_NATIVE_PHYSX",json.dumps({
        "n":d["distinct_reset_states"],"real_worlds":d["physically_executed_actual_controller_worlds"],
        "outcomes":d["outcomes"],"paired":d["paired"],
        "public_confident":d["public_confident"],"wrong_confident":d["wrong_confident"]},sort_keys=True))

if __name__=="__main__":
    main()
