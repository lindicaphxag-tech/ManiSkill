"""Independent SOURCE-ONLY native re-anchor dev pilot auditor.
Requires original JSONs and their SHA256 files from physically stepped shards.
Counts original RESETs, NEVER four ACK truths as independent population n.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

TASKS={"pull_cube":tuple(range(4500001,4500005)),
       "stack_cube":tuple(range(4600001,4600005))}
def audit(root):
    root=Path(root)
    report={}
    digest_provenance={}
    for task,seeds in TASKS.items():
        path=root/f"native_mode_refresh_{task}_original.json"
        digest_path=root/f"native_mode_refresh_{task}_original.sha256"
        if not path.is_file() or not digest_path.is_file():
            raise ValueError("Missing original task producer artifacts")
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest_path.read_text().strip()!=sha:raise ValueError("Original source SHA256 changed")
        digest_provenance[task]=sha
        obj=json.loads(path.read_text())
        if (obj.get("schema")!="native_mode_refresh_development_frozen_ppo_physical_v1"
            or obj.get("task")!=task or obj.get("no_PPO_training") is not True
            or obj.get("cost_model_two_privileged_mode_writes_and_zero_hidden_state_writes") is not True
            or obj.get("actual_independent_reset_clusters")!=4
            or obj.get("actual_correlated_ACK_task_pairs")!=16
            or obj.get("actually_physical_native_controller_worlds")!=336):
            raise ValueError("Wrong physical run or denominator")
        rows=obj.get("rows",[])
        if len(rows)!=16 or {(r["seed"],r["actual_ack_truth"]) for r in rows}!={(s,t) for s in seeds for t in range(4)}:
            raise ValueError("Missing or duplicate native physical trials")
        for r in rows:
            if (r.get("task")!=task or
                r.get("pre_t4_native_action_prefix_max_abs",float("inf"))>1e-6 or
                r.get("pre_t4_public_ee_xyz_max_abs_m",float("inf"))>5e-5 or
                r.get("privileged_internal_write_count")!=0 or
                r.get("privileged_runtime_mode_writes")!=2 or
                r.get("proposed_decision_getter_count")!=0 or
                r.get("proposed_public_achieved_pose_read_count")!=1 or
                r.get("all_actual_PhysX_steps_completed") is not True or
                r.get("source_original_full_runner_worlds")!=10 or
                r.get("proposed_full_runner_worlds")!=11):
                raise ValueError("Malformed actual controller recovery authority/event accounting")
            for k in ("source_baseline_zero_success",
                      "source_baseline_privileged_getter_success",
                      "proposed_mode_refresh_success"):
                if type(r.get(k)) is not bool:raise ValueError("Nonphysical task success type")
        report[task]=dict(independent_reset_clusters=4,correlated_ack_trials=16,
            zero_success=sum(r["source_baseline_zero_success"] for r in rows),
            trusted_getter_success=sum(r["source_baseline_privileged_getter_success"] for r in rows),
            mode_refresh_success=sum(r["proposed_mode_refresh_success"] for r in rows),
            unique_mode_refresh_saves_over_zero=sum(
                r["proposed_mode_refresh_success"] and not r["source_baseline_zero_success"] for r in rows),
            zero_only_success=sum(
                r["source_baseline_zero_success"] and not r["proposed_mode_refresh_success"] for r in rows),
            both_failed=sum(
                not r["source_baseline_zero_success"] and not r["proposed_mode_refresh_success"] for r in rows),
            native_internal_target_writes=sum(r["privileged_internal_write_count"] for r in rows),
            charged_runtime_controller_mode_writes=sum(r["privileged_runtime_mode_writes"] for r in rows),
            privileged_getter_baseline_reads=sum(r["privileged_getter_comparator_count"] for r in rows))
    return dict(status="SOURCE_SHA_AUDITED_FIRST_NATIVE_MODE_REFRESH_PHYSX_DEVELOPMENT_PILOT",
      total_physx_controller_worlds=672,independent_reset_clusters=8,
      ack_trials_repeated_correlated=32,all_shard_original_source_sha256=digest_provenance,
      by_task=report,real_robot_evidence=False,privileged_mode_reconfiguration_is_not_hardware_command=True,
      success_improvement_claim_not_statistically_certified=True,
      not_external_replication=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    a=audit(args.root)
    Path(args.out).write_text(json.dumps(a,indent=2,sort_keys=True)+"\n")
    print("NATIVE_MODE_REFRESH_ORIGINAL_PHYSX_SOURCE_AUDIT",json.dumps(a,sort_keys=True))
