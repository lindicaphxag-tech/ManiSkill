"""Byte-locked original native PhysX *two-consecutive unknown ACK* audit.

Validates the complete 16-state, 7-arm author-operated original run
#37898781176. Requires only Python standard library. Does not run physics,
does not constitute external reproduction, and certifies bounded controller
*setpoints*, not collision, force, trajectory, or real-robot safety.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
import shutil
import tempfile

ORIGINAL_RUN_ID=37898781176
METHOD_HEAD="b7670dd17037bbb94d208a40a1e068ce972b5484"
RUNNER_BLOB="99836af14205fe3e95e52a2e0d68237c7c8a9045"
CERTIFIER_BLOB="36707a177549104ba5b4bd9bcebc76518f0d2840"
PROTOCOL_BLOB="99e904c21a2c4c0b8e3ca15ee9da4ddd44d0caa4"
TASKS={
  "pull_cube":dict(
    name="PullCube-v1",start=400001,
    manifest="2e0d0ef11bbb559a5ed25941213f51f2ea444403e56ce3dca0922bc7e4f77095",
    original="b19376644e1ec20b63458b3168d7b043080eaf367c4e03f646b027cc646b7859",
    checkpoint="74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7",
    counts=(8,8,1,1)),
  "stack_cube":dict(
    name="StackCube-v1",start=410001,
    manifest="62353524018a049c20ac596946a707c7f70490e22404498087db33fe0199709c",
    original="19963c6fba4f16f437f166749f1134aa667415dea89a149825593f9d2eb6ab67",
    checkpoint="e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c",
    counts=(3,5,1,1)),
}
SOURCE="source_no_fault"
SEL="fault_robust_then_single_privileged_query"
FIXED="fault_always_single_privileged_query"
ZERO="fault_robust_two_history_without_query"
ORACLE="fault_oracle_private_target"
OPT="fault_optimistic_unverified_ack"
STRICT="fault_strict_common_exact"
ARMS=(SOURCE,ORACLE,OPT,STRICT,ZERO,SEL,FIXED)
BELIEF=(ZERO,SEL,FIXED,STRICT)
PROTOCOL="research/COMPOUND_ACK_MULTI_HYPOTHESIS_PRECOMMIT_V3.md"


def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def require(condition,why):
    if not condition:
        raise ValueError(why)


def verified_dir(path:Path,task:str):
    registered=TASKS[task]
    manifest=(path/"SHA256SUMS").read_bytes()
    require(digest(manifest)==registered["manifest"],
            "Published source manifest hash mismatch")
    lines=manifest.decode("utf-8").splitlines()
    seen=set()
    for line in lines:
        fields=line.split()
        require(len(fields)==2 and len(fields[0])==64,"Malformed source hash line")
        h,filename=fields
        require(filename not in seen,"Duplicate evidence file")
        seen.add(filename)
        require(digest((path/filename).read_bytes())==h,
                "Original native-PhysX file bytes changed: "+filename)
    for filename,expected in {
        "current_source_commit.txt":METHOD_HEAD,
        "compound_runner_blob.txt":RUNNER_BLOB,
        "multi_certifier_blob.txt":CERTIFIER_BLOB,
        "protocol_blob.txt":PROTOCOL_BLOB,
    }.items():
        require((path/filename).read_text().strip()==expected,
                "Invalid original source commit/blob: "+filename)
    original_file=(path/f"compound_multi_ack_{task}_original8.json")
    require(digest(original_file.read_bytes())==registered["original"],
            "Original untouched 8-state result JSON changed")
    return json.loads(original_file.read_text("utf-8"))


def verify_task(path:Path,task:str):
    spec=TASKS[task]
    r=verified_dir(path,task)
    require(r.get("schema")=="compound_two_unknown_ack_multihistory_physx_v1",
            "Bad original source schema")
    require(r.get("task")==spec["name"]
            and r.get("original_seed_population")==list(range(spec["start"],spec["start"]+8)),
            "Original task/seed identity changed")
    require(r.get("frozen_model_retrained") is False
            and r.get("real_physx_simulator") is True
            and r.get("fault_is_native_target_hold_not_network_loss") is True
            and r.get("two_consecutive_unknown_ack_target_hold_steps")==[2,3],
            "Original native fault/checkpoint contract changed")
    require(r.get("original_external_frozen_checkpoint_sha256")==spec["checkpoint"],
            "Frozen published PPO weights changed")
    require(r.get("preoutcome_protocol")==PROTOCOL,
            "Not the pre-outcome protocol")
    require(tuple(r.get("all_seven_actual_control_arms",()))==ARMS,
            "Missing/changed original matched controller worlds")
    rows=r.get("episodes")
    require(isinstance(rows,list) and len(rows)==8,"Not all eight original source episodes")
    require([x["seed"] for x in rows]==list(range(spec["start"],spec["start"]+8)),
            "Duplicate/missing/reordered original source seeds")
    outcomes={name:0 for name in ARMS}
    reads={name:0 for name in ARMS if name!=ORACLE}
    checks=0;masked=0
    for row in rows:
        flags=row["success_once"]
        require(set(flags)==set(ARMS)
                and all(type(flags[name]) is bool for name in ARMS),
                "Incomplete or invalid official ManiSkill task outcomes")
        for n in ARMS:
            outcomes[n]+=int(flags[n])
        q=row["privileged_target_readback_decision_count"]
        require(q[ORACLE]==-1,"Privileged continuous oracle incorrectly counted")
        require(all(type(q[n]) is int and q[n] in (0,1) for n in ARMS if n!=ORACLE),
                "Non-binary/invalid private target decision read count")
        require(all(q[n]==0 for n in (SOURCE,OPT,STRICT,ZERO)),
                "Forbidden privileged information given to no-query comparator")
        for n in reads:reads[n]+=q[n]
        fs=row["faults"]
        for n in ARMS[1:]:
            steps=[fault["step"] for fault in fs.get(n,[])]
            require(steps in ([2],[2,3]),"Invalid observed native target-hold timing")
            if n!=STRICT:
                require(steps==[2,3],"Dropped original second physical fault")
        widths=row["max_belief_width"]
        require(all(type(widths[n]) is int and 1<=widths[n]<=16 for n in BELIEF),
                "Missing/provenance-invalid finite belief width")
        require(all(widths[n]>=4 for n in (ZERO,SEL,FIXED)),
                "No actual four-state controller target belief")
        masked_by_arm=row.get("certified_action_masked_by_injected_fault",{})
        audited_by_arm=row.get("robust_native_target_bound_checks",{})
        for n,arr in masked_by_arm.items():
            require(n in BELIEF,"Unrelated arm claimed masked bounded action")
            for witness in arr:
                masked+=1
                require(witness["step"] in (2,3)
                        and witness["native_action_did_not_execute"] is True
                        and witness["postdispatch_certificate_check_not_applicable"] is True
                        and witness["claimed_physical_setpoint_certificate"] is False,
                        "Injected masked command falsely counted as executed")
                require(all(v["step"]!=witness["step"]
                            for v in audited_by_arm.get(n,[])),
                        "Counterfactual masked command illicitly passed native physical audit")
        for n,arr in audited_by_arm.items():
            require(n in BELIEF,"Unexpected certified-world audit")
            for witness in arr:
                checks+=1
                require(witness["step"] not in (2,3)
                        and witness["only_audit_after_physical_dispatch"] is True,
                        "Nonexecuted or non-postdispatch native controller check")
                require(
                    witness["position_error_m"] <= witness["worst_case_position_limit_m"]+1e-4+1e-10,
                    "Measured controller position target violated claimed bound")
                require(
                    witness["rot_error_rad"] <= witness["worst_case_rot_limit_rad"]+1e-4+1e-10,
                    "Measured controller orientation target violated claimed bound")
    require(outcomes==r.get("success_counts"),
            "Official full-denominator totals disagree with original worlds")
    expected=(spec["counts"][0],spec["counts"][1],spec["counts"][2],spec["counts"][3])
    require(tuple(outcomes[n] for n in (SEL,FIXED,ZERO,OPT))==expected,
            "Frozen original outcome totals changed")
    require((reads[SEL],reads[FIXED])==
            ((7,8) if task=="pull_cube" else (4,8)),
            "Privileged read costs changed")
    return {
        "task":spec["name"],"original_seeds":r["original_seed_population"],
        "official_task_successes":outcomes,
        "privileged_decision_reads":reads,
        "after_real_dispatch_setpoint_audits":checks,
        "fault_masked_certificate_attempts_not_audited":masked,
        "episodes":rows,
    }


def audit(pull:Path,stack:Path):
    tasks={key:verify_task(path,key) for key,path in
           (("pull_cube",pull),("stack_cube",stack))}
    cases=[(task,row) for task,v in tasks.items() for row in v["episodes"]]
    require(len(cases)==16 and len({(t,x["seed"]) for t,x in cases})==16,
            "Original independent physical reset states missing")
    def contingency(control):
        c=Counter((int(x["success_once"][SEL]),
                   int(x["success_once"][control])) for _,x in cases)
        return {
          "both_success":c[(1,1)],"adaptive_only":c[(1,0)],
          "comparator_only":c[(0,1)],"both_fail":c[(0,0)],
        }
    result={
      "run_id":ORIGINAL_RUN_ID,
      "nature":"author-run unchanged frozen PPO, real ManiSkill PhysX; NOT third-party lab replication",
      "source_commit":METHOD_HEAD,
      "n_original_independent_reset_states":16,
      "n_matched_controller_worlds":112,
      "n_frozen_published_PPOs":2,
      "real_controller_setpoint_postdispatch_audits":
        sum(x["after_real_dispatch_setpoint_audits"] for x in tasks.values()),
      "fault_masked_actions_never_counted_as_real_controller_audits":
        sum(x["fault_masked_certificate_attempts_not_audited"] for x in tasks.values()),
      "successes_by_task":{key:t["official_task_successes"] for key,t in tasks.items()},
      "reads_by_task":{key:t["privileged_decision_reads"] for key,t in tasks.items()},
      "paired_adaptive_vs_fixed":contingency(FIXED),
      "paired_adaptive_vs_zero":contingency(ZERO),
      "four_state_belief_reached_in_every_original_source_state":True,
      "conclusion":"Mixed outcomes: Pull adaptive 8/8 vs fixed 8/8; Stack adaptive 3/8 vs fixed 5/8. Do NOT assert adaptive superiority.",
      "limits":[
        "one Panda embodiment, two task/checkpoint families only",
        "two simulated commanded-target arm holds, not actual network packet loss",
        "pretrained policy frozen; no new VLA training",
        "private target readback is privileged, not free",
        "setpoint certificate does not verify trajectory, force, collision or hardware safety",
        "auditor cannot independently rerun PhysX, and no outside researcher has accepted this new study",
      ],
    }
    require(result["real_controller_setpoint_postdispatch_audits"]==384,
            "Original real native physical setpoint audit count changed")
    require(result["fault_masked_actions_never_counted_as_real_controller_audits"]==48,
            "Original fault-mask audit denominator changed")
    require(result["paired_adaptive_vs_fixed"]==
            {"both_success":10,"adaptive_only":1,"comparator_only":3,"both_fail":2},
            "Original paired query-timing outcome changed")
    return result


def self_test(pull,stack):
    baseline=audit(pull,stack)
    with tempfile.TemporaryDirectory() as d:
        copied=Path(d)/"pull"
        shutil.copytree(pull,copied)
        changed=copied/"compound_multi_ack_pull_cube_original8.json"
        changed.write_bytes(changed.read_bytes()+b"\n")
        try:audit(copied,stack)
        except ValueError: pass
        else:raise AssertionError("Tampered original JSON accepted")
        changed.write_bytes((pull/"compound_multi_ack_pull_cube_original8.json").read_bytes())
        sha=copied/"SHA256SUMS"
        sha.write_bytes(sha.read_bytes()+b"\n")
        try:audit(copied,stack)
        except ValueError: pass
        else:raise AssertionError("Tampered original checksum manifest accepted")
    return baseline


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pull",type=Path,required=True,help="Extracted original PullCube GitHub artifact")
    p.add_argument("--stack",type=Path,required=True,help="Extracted original StackCube GitHub artifact")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    result=self_test(args.pull,args.stack) if args.self_test else audit(args.pull,args.stack)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("MULTI_ACK_AUTHENTIC_NATIVE_PHYSX_AUDIT",json.dumps({
        "states":result["n_original_independent_reset_states"],
        "physical_checks":result["real_controller_setpoint_postdispatch_audits"],
        "masked_not_counted":result["fault_masked_actions_never_counted_as_real_controller_audits"],
        "paired_selective_vs_fixed":result["paired_adaptive_vs_fixed"],
        "destructive_checks_passed":bool(args.self_test),
    },sort_keys=True))


if __name__=="__main__":
    main()
