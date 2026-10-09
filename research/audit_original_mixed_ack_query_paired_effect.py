"""Independent stdlib-only paired source query analysis for ORIGINAL mixed-ACK 64.

The 64 observations are within TWO tasks and ONE destination robot, therefore
the exact sign test is DESCRIPTIVE/EXPLORATORY, not independent-task inference.
Never interpret an observed equal task success as statistical noninferiority.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
SOURCE=Path("research/frozen_policy_transfer/evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032/ORIGINAL_MIXED_ACK_ALL64_FULL_AUDIT.json")
EXPECTED_GIT_BLOB="c86dce6fc381369817e97ef299cb3df2ca543374"

def git_blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()

def analysis():
    original=SOURCE.read_bytes()
    if git_blob_sha(original)!=EXPECTED_GIT_BLOB:
        raise ValueError("Primary original source audit changed; no exploratory test allowed")
    a=json.loads(original)
    assert a["complete_double_fault_gate_passes"] is True
    assert a["first_physical_ACK_truth_balance"]=={"applied":32,"held":32}
    rows=[]
    task_results={}
    for task,part in a["by_task"].items():
        arr=part["original_all_trial_rows"]
        if len(arr)!=32 or len({r["seed"] for r in arr})!=32:
            raise ValueError("Source experiment incomplete in one task")
        for r in arr:
            if any(type(r[k]) is not bool for k in ("new_success","task_gate_success")):
                raise ValueError("Missing actual physical success bit")
            if any(type(r[k]) is not int or r[k] not in (0,1) for k in ("new_reads","task_gate_reads")):
                raise ValueError("Missing actual privileged read counts")
            rows.append(dict(task=task,seed=r["seed"],
                             gain=r["task_gate_reads"]-r["new_reads"],
                             new_success=r["new_success"],strong_success=r["task_gate_success"]))
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Missing or duplicate true paired source reset")
    def sign_test(x):
        positive=sum(r["gain"]>0 for r in x)
        negative=sum(r["gain"]<0 for r in x)
        ties=sum(r["gain"]==0 for r in x)
        n=positive+negative
        p=min(1., 2*sum(math.comb(n,k) for k in range(min(positive,negative)+1))/2**n) if n else 1.
        return dict(private_read_savings_new_positive=positive,private_read_savings_strong_positive=negative,
                    read_ties=ties,net_private_reads_saved=sum(r["gain"] for r in x),
                    exact_two_sided_unadjusted_sign_test_p=p,
                    actual_new_successes=sum(r["new_success"] for r in x),
                    actual_strong_successes=sum(r["strong_success"] for r in x),
                    actual_paired_both_success=sum(r["new_success"] and r["strong_success"] for r in x),
                    original_true_physical_episodes=len(x))
    overall=sign_test(rows)
    assert overall["private_read_savings_new_positive"]==30
    assert overall["private_read_savings_strong_positive"]==3
    assert overall["read_ties"]==31
    assert overall["net_private_reads_saved"]==27
    assert overall["actual_new_successes"]==58==overall["actual_strong_successes"]
    by_task={task:sign_test([r for r in rows if r["task"]==task])
             for task in ("pull_cube","stack_cube")}
    return dict(schema="exploratory_paired_64_source_read_cost_not_task_noninferiority_v1",
                source_archive_exact_git_blob=EXPECTED_GIT_BLOB,
                executed_source_physx_only_not_outside_replication=True,
                independence_of_64_reset_states_not_guaranteed=True,
                single_destination_Panda_and_two_PPO_tasks=True,
                hypothesis_generated_after_observing_full_original_data=True,
                unadjusted_p_exploratory_not_confirmatory=True,
                binary_task_noninferiority_not_demonstrated=True,
                all=overall,by_task=by_task)

if __name__=="__main__":
    print("ORIGINAL_MIXED_ACK_PAIRED_64_READ_COST_EXPLORATORY",json.dumps(analysis(),sort_keys=True))
