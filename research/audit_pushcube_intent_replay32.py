"""No-retuning analysis of 32 new PushCube actual PhysX native episodes."""
import json
from math import comb
from pathlib import Path
NAME=("source_no_fault","fault_oracle_private_target",
"fault_fixed_readback_canonical","fault_robust_then_single_privileged_query",
"fault_replay_unconditional_one_readback","fault_replay_alignment_gated_one_readback")
SHA="a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf"
FIRST=2026760001
def exact_p(a,b):
    n=a+b
    return min(1.0,2*sum(comb(n,k) for k in range(min(a,b)+1))/2**n) if n else 1.0
def summarize(folder):
    folder=Path(folder);rows=[]
    for shard in range(4):
        path=folder/f"pushcube_causal_replay_push_cube_chunk{shard}_original8.json"
        d=json.loads(path.read_text())
        if d["schema"]!="pushcube_causal_intent_replay_6arm_v1" or d["task"]!="PushCube-v1":
            raise RuntimeError("Wrong task/schema")
        if d["original_external_frozen_checkpoint_sha256"]!=SHA:
            raise RuntimeError("Frozen published PushCube model sha drift")
        if set(d["all_six_actual_control_arms"])!=set(NAME):
            raise RuntimeError("Missing strong comparator")
        eight=d["episodes"]
        if len(eight)!=8 or [r["seed"] for r in eight]!=list(range(FIRST+8*shard,FIRST+8*shard+8)):
            raise RuntimeError("Incomplete or repeated source reset")
        rows+=eight
    if len(rows)!=32 or len({r["seed"] for r in rows})!=32:
        raise RuntimeError("Wrong number of independently seeded reset clusters")
    results=dict(task="PushCube-v1", original_unique_reset_clusters=len(rows),
        originally_stepped_native_controller_worlds=len(rows)*len(NAME),
        no_policy_training=True,not_external_lab=True,
        source_only_native_actions_without_true_ack=True,
        task_type_previously_one_seed_geometry_only=True,
        no_hardware_collision_or_real_network_fault_claim=True,
        arms={},paired={},fair_public_prefix={},primary_frozen_gates={})
    for arm in NAME:
        reads=[r["privileged_target_readback_decision_count"][arm] for r in rows]
        results["arms"][arm]=dict(
            task_successes=sum(int(r["success_once"][arm]) for r in rows),
            actual_target_decision_reads=("unrestricted" if arm==NAME[1] else sum(reads)),
            true_native_two_fault_exposures=(sum(len(r["faults"].get(arm,[]))==2 for r in rows)
                if arm!=NAME[0] else None),
            one_time_replay_changed=(sum(int(r["replay_decisions"].get(arm,{}).get("actual_command_changed",False))
                for r in rows) if arm in NAME[-2:] else None))
        if arm==NAME[1] and any(x!=-1 for x in reads):
            raise RuntimeError("Oracle cannot be disguised as free query")
    for control in (NAME[1],NAME[2],NAME[3],NAME[4]):
        new=NAME[-1]
        plus=sum(bool(r["success_once"][new]) and not bool(r["success_once"][control]) for r in rows)
        minus=sum(not bool(r["success_once"][new]) and bool(r["success_once"][control]) for r in rows)
        results["paired"][control]={"new_only":plus,"control_only":minus,
                                    "exploratory_exact_p":exact_p(plus,minus)}
    for control in NAME[-2:]:
        matching=0
        for r in rows:
            new_action=r["actual_step_action_trace"][control]
            fixed_action=r["actual_step_action_trace"][NAME[2]]
            same=len(new_action)>=4 and len(fixed_action)>=4
            if same:
                for a,b in zip(new_action[:4],fixed_action[:4]):
                    same &= (a["step"]==b["step"] and
                        max(abs(q-z) for q,z in zip(
                            a["dispatched_native_controller_action"],
                            b["dispatched_native_controller_action"]))<1e-6)
            matching+=int(same)
        results["fair_public_prefix"][control]={"identical_first_four_actions":matching,
                                                  "denominator":len(rows)}
    s=results["arms"];new=NAME[-1]
    results["primary_frozen_gates"]={
        "32_of_32_injected_twice":all(s[a]["true_native_two_fault_exposures"]==32 for a in NAME[1:]),
        "new_beat_correct_fixed_success":s[new]["task_successes"]>s[NAME[2]]["task_successes"],
        "new_beat_fully_informed_oracle_success":s[new]["task_successes"]>s[NAME[1]]["task_successes"],
        "new_reads_at_most_fixed":s[new]["actual_target_decision_reads"]<=s[NAME[2]]["actual_target_decision_reads"],
        "new_real_controller_action_difference":s[new]["one_time_replay_changed"]>0,
        "new_same_public_initial_physics":results["fair_public_prefix"][new]["identical_first_four_actions"]==32}
    results["primary_frozen_gates"]["all_pass"]=all(results["primary_frozen_gates"].values())
    return results
if __name__=="__main__":
    import sys
    r=summarize(sys.argv[1])
    Path(sys.argv[2]).write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("FROZEN_PUSH_ORIGINAL32",json.dumps(r,sort_keys=True))
