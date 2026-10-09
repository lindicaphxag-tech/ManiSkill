"""Retrospective OLD 32-state native PhysX diagnostic; NOT new policy outcome.

No new physical simulation is executed. Uses byte-locked prior source with
already observed task outcomes only to identify a candidate design correction.
Never include this in prospective heldout/new64 success counts.
"""
import hashlib,json
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence/public_fourhistory_frozen_ppo_original32_780001_790016")
FULL_SHA1_GIT_BLOB="4a20442c1bea6100aa935084b7c7c8afac94e6b2"

def main():
    source=ROOT/"full_original_new32_task_ack_public_audit.json"
    raw=source.read_bytes()
    # Git source blob identity: the archived per-row aggregate is immutable.
    got=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    if got!=FULL_SHA1_GIT_BLOB:
        raise ValueError("Original source-audited old physical population changed")
    j=json.loads(raw)
    result={}
    for task,group in j["by_task"].items():
        allowed=wrong=total=0
        for row in group["original_all_trial_rows"]:
            total+=1
            evidence=row.get("new_public_evidence",{})
            distances=evidence.get("candidate_residuals_m",[])
            eps=evidence.get("prior_training_epsilon_m")
            matches=evidence.get("accepted_position_indices",[])
            if not isinstance(eps,(float,int)) or len(distances)!=4 or not isinstance(matches,list):
                raise ValueError("Missing prior actual full four-history PhysX records")
            if (len(matches)==1
                and all(d>eps+.002 for i,d in enumerate(distances) if i!=matches[0])):
                allowed+=1
                wrong+=int(matches[0] not in evidence["audit_only_true_candidate_indices"])
        result[task]=dict(development_seen_original_trials=total,
                          retrospective_unique_full_hypothesis_indices=allowed,
                          retrospective_wrong_against_post_physics_audit_only_truth=wrong)
    assert result["pull_cube"]==dict(
        development_seen_original_trials=16,
        retrospective_unique_full_hypothesis_indices=4,
        retrospective_wrong_against_post_physics_audit_only_truth=0)
    assert result["stack_cube"]==dict(
        development_seen_original_trials=16,
        retrospective_unique_full_hypothesis_indices=8,
        retrospective_wrong_against_post_physics_audit_only_truth=0)
    print("OUTCOME_EXPOSED_PRIOR32_DIAGNOSTIC_NOT_NEW_REAL_PHYSX",json.dumps(result,sort_keys=True))
    print("ZERO NEW POLICY TASK SUCCESSES OR PRIVATE READ SAVINGS HAVE BEEN PHYSICALLY EXECUTED BY THIS ANALYSIS")

if __name__=="__main__":
    main()
