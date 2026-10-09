"""Independent stdlib reviewer audit of outsider-selected eight native PhysX resets.

This audit DOES NOT make an author-operated run external replication. The
investigator must own the fork/run and select unused seeds BEFORE running.
The 10-arm source runner/teacher PPO must remain SHA-pinned and unchanged.
"""
import argparse
import json
from pathlib import Path

NAMES = (
    "source_no_fault", "fault_oracle_private_target",
    "fault_optimistic_unverified_ack", "fault_strict_common_exact",
    "fault_robust_two_history_without_query",
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
    "fault_authority_slack_proactive_query", "fault_phase_value_query",
    "fault_fixed_readback_canonical",
)
PHASE = "fault_phase_value_query"
CANON = "fault_fixed_readback_canonical"
LEGACY = "fault_always_single_privileged_query"
HASHES = {
    "pull_cube": ("PullCube-v1", "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube": ("StackCube-v1", "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
RUNNER_ORIGIN_BLOB = "7de4ef9be172c2e4e63bd043318f53e9e2ede688"
PREIMPLEMENTATION = "d664ec2fe4bb3a5d86ff4de3b1e7797c199f3037"


def select(task, first_seed, *, for_original_self_test=False):
    if task not in HASHES or type(first_seed) is not int:
        raise ValueError("Select one of the two registered frozen PPO tasks and an integer first seed")
    if not for_original_self_test and not 1000001 <= first_seed <= 9999992:
        raise ValueError("Outsider-run seed starts must be between 1000001 and 9999992")
    return list(range(first_seed, first_seed + 8))


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def independent_audit(record, task, first_seed, *, self_test=False):
    seeds=select(task, first_seed, for_original_self_test=self_test)
    env,ckpt=HASHES[task]
    require(record.get("schema") == "canonical_post_readback_10arm_fresh64_v1", "Protocol/schema changed")
    require(record.get("original_seed_population") == seeds and
            record.get("task") == env and
            record.get("original_external_frozen_checkpoint_sha256") == ckpt and
            record.get("precommitted_protocol_commit") == PREIMPLEMENTATION and
            record.get("original_frozen_runner_blob") == RUNNER_ORIGIN_BLOB and
            record.get("frozen_model_retrained") is False and
            record.get("real_physx_simulator") is True and
            record.get("two_consecutive_unknown_ack_target_hold_steps") == [2,3] and
            record.get("fault_is_native_target_hold_not_network_loss") is True and
            record.get("all_ten_actual_control_arms") == list(NAMES),
            "Original source, checkpoint, physical fault or controller provenance invalid")
    rows=record.get("episodes")
    require(isinstance(rows,list) and len(rows)==8 and
            [r.get("seed") for r in rows]==seeds,
            "Must retain all eight new prospective source states and no duplicates")
    result={"schema":"outsider_canonical_eight_state_independent_audit_v1",
            "investigator_selected_task":task,"seed_first":first_seed,
            "seed_last":first_seed+7,"independently_stepped_physical_worlds_if_source_trusted":80,
            "fault_is_simulated_native_target_hold":True,
            "not_network_packet_loss":True,
            "not_hardware_safety":True,
            "origin_study_precommit":PREIMPLEMENTATION,
            "per_seed":[],"official_success":{n:0 for n in NAMES},
            "private_reads":{n:0 for n in NAMES if n!="fault_oracle_private_target"},
            "complete_stack_action_equivalence":None if task=="pull_cube" else True}
    for row in rows:
        success=row.get("success_once",{})
        reads=row.get("privileged_target_readback_decision_count",{})
        require(set(success)==set(NAMES) and all(type(success[n]) is bool for n in NAMES),
                "Missing actual real episode success truth")
        require(reads.get("fault_oracle_private_target")==-1, "Private oracle read misaccounted")
        for n in NAMES:
            result["official_success"][n]+=int(success[n])
            if n!="fault_oracle_private_target":
                require(type(reads.get(n)) is int and reads[n] in (0,1),
                        "Incorrect authoritative query budget or source ledger")
                result["private_reads"][n]+=reads[n]
        t=row.get("actual_step_action_trace",{})
        require(set(t)=={PHASE,CANON,LEGACY},"Missing three physical comparator native action logs")
        a,b=t[PHASE],t[CANON]
        require(all(len(x.get("dispatched_native_controller_action",[]))==7
                    for v in t.values() for x in v),"Unrecorded native 7D action")
        equal=len(a)==len(b) and all(
            x.get("step")==y.get("step") and
            max(abs(float(u)-float(v)) for u,v in zip(
                x["dispatched_native_controller_action"],y["dispatched_native_controller_action"]))<=1e-6
            for x,y in zip(a,b))
        invariant=row.get("stack_post_readback_canonical_invariant",{})
        if task=="stack_cube":
            valid=(equal and success[PHASE]==success[CANON] and reads[PHASE]==reads[CANON])
            require(invariant.get("passed") is valid and
                    invariant.get("same_controller_action_every_executed_step") is equal,
                    "Original source mismatched actual independently computed action equivalence")
            result["complete_stack_action_equivalence"] &= valid
            require(valid,"FALSIFICATION: identical controller read/belief did NOT give equivalent Stack action")
        result["per_seed"].append({
            "seed":row["seed"],"phase_success":success[PHASE],
            "canonical_fixed_success":success[CANON],"legacy_fixed_success":success[LEGACY],
            "phase_reads":reads[PHASE],"canonical_fixed_reads":reads[CANON],
            "phase_and_canonical_actions_equal":equal,
            "physical_fault_steps":{n:[f.get("step") for f in row.get("faults",{}).get(n,[])]
                                    for n in NAMES[1:]},
        })
    require(record.get("success_counts")==result["official_success"],
            "Source per-arm count inconsistent with full eight episodes")
    if task=="stack_cube":
        require(result["complete_stack_action_equivalence"] is True and
                record.get("stack_post_readback_canonical_invariant_all_pass") is True,
                "Stack source reported a failed phase-vs-canonical control equivalence")
    result["causal_scope"]="Matched simulator worlds, not independent lab unless outside person genuinely ran own fork"
    return result


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--task", choices=list(HASHES), default="stack_cube")
    a.add_argument("--first-seed",type=int,default=1000001)
    a.add_argument("--input",type=Path)
    a.add_argument("--output",type=Path)
    a.add_argument("--self-test",action="store_true")
    v=a.parse_args()
    if v.self_test:
        root=Path("research/frozen_policy_transfer/evidence/canonical_post_read_original64_970001_980032")
        for task,first in (("pull_cube",970001),("stack_cube",980001)):
            p=root/f"canonical_post_read_{task}_chunk0_original8.json"
            independent_audit(json.loads(p.read_text()),task,first,self_test=True)
        try:select("stack_cube",970001)
        except ValueError:pass
        else:raise AssertionError("Original published seeds must not be selected for outside replay")
        print("PASS original source records and outsider-only unused-seed selector")
        return
    require(v.input is not None and v.output is not None,"Require true source input and output")
    out=independent_audit(json.loads(v.input.read_text()),v.task,v.first_seed)
    v.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OUTSIDER_CANONICAL_FRESH_EIGHT_AUDIT",json.dumps({
        "task":v.task,"physical_worlds":80,"official_success":{
            PHASE:out["official_success"][PHASE],CANON:out["official_success"][CANON]},
        "reads":{PHASE:out["private_reads"][PHASE],CANON:out["private_reads"][CANON]},
        "stack_physical_trace_equivalence":out["complete_stack_action_equivalence"],
        "evidence_scope":"outside run must belong to independent investigator"},sort_keys=True))


if __name__=="__main__":
    main()
