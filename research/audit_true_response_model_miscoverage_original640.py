"""Original source-locked AFTER-OUTCOME physics model-coverage failure audit.

Separate from the live controller admission process. True target labels are
obtained only AFTER each real native PhysX step in ORIGINAL archived trials;
do not include these getters in an online VLA/robot policy.

Crucial distinction: (a) truth residual OUTSIDE empirical model envelope,
(b) a confidently WRONG full native target-history authorization, and
(c) official task failure are DIFFERENT events with different denominators.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
PATH=Path("research/frozen_policy_transfer/evidence/validity_first_prior32_new64_physx_original_940001_950032/INDEPENDENT_64_VALIDITY_FIRST_ORIGINAL_AUDIT.json")
PINNED_ORIGINAL_GIT_BLOB="76fc1f07aff16b1f96fdf34a3861d93ebe069afb"
NARROW={"pull_cube":.006944262561376447,"stack_cube":.00719087965534261}
CALIBRATED={"pull_cube":.006944262561376447,"stack_cube":.02126739483653302}
def git_blob(content):
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\x00"+content).hexdigest()

def audit():
    raw=PATH.read_bytes()
    if git_blob(raw)!=PINNED_ORIGINAL_GIT_BLOB:
        raise ValueError("Original 64 true physical samples or full source audit CHANGED")
    a=json.loads(raw)
    if a.get("genuine_source_physx_reset_states")!=64 or a.get("genuine_independently_stepped_native_controller_worlds")!=640:
        raise ValueError("Not actual complete native PhysX original population")
    rows=a["all_actual_original_source_episode_records"]
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Missing original native physical trials or duplicate reset")
    per=[]
    for row in rows:
        task=row["task"]
        if task not in NARROW:
            raise ValueError("Unknown original task")
        x=row["narrow_public_evidence"]
        y=row["calibrated_public_evidence"]
        def score(ev,epsilon):
            cand=ev["candidate_residuals_m"]
            truth=ev["audit_only_true_candidate_indices"]
            if (len(truth)!=1 or len(cand)!=4 or
                not isinstance(ev.get("prior_training_epsilon_m"),(float,int)) or
                abs(ev["prior_training_epsilon_m"]-epsilon)>1e-12 or
                ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True):
                raise ValueError("Source true target provenance/threshold invalid")
            target_index=truth[0]
            tr=float(cand[target_index])
            if not math.isfinite(tr) or tr<0:
                raise ValueError("Source physical score impossible")
            accepted=[i for i,d in enumerate(cand) if d<=epsilon+1e-12]
            predicted=bool(len(accepted)==1 and all(d>epsilon+.002 for i,d in enumerate(cand) if i!=accepted[0]))
            if ev["accepted_position_indices"]!=accepted or ev["authorized"] is not predicted:
                raise ValueError("Source public decision cannot be reconstructed")
            wrong=bool(predicted and accepted[0]!=target_index)
            if wrong!=ev["wrong_confident"]:
                raise ValueError("Original actual hidden target labels contradict claimed error")
            return tr,tr>epsilon,predicted,wrong
        na=score(x,NARROW[task])
        ca=score(y,CALIBRATED[task])
        if abs(na[0]-ca[0])>1e-6:
            raise ValueError("Pair does not share real native achieved motion response")
        per.append({"task":task,"seed":row["seed"],"actual_joint_ack":row["true_joint_ack"],
                    "source_true_response_residual_m":na[0],
                    "narrow_out_of_envelope":na[1],
                    "calibrated_out_of_envelope":ca[1],
                    "narrow_confident_authorization":na[2],
                    "calibrated_confident_authorization":ca[2],
                    "narrow_wrong_confident":na[3],
                    "calibrated_wrong_confident":ca[3],
                    "narrow_task_success":row["narrow_success"],
                    "calibrated_task_success":row["calibrated_success"]})
    def summary(z):
        return {
            "n":len(z),
            "narrow_true_model_residual_outside":sum(x["narrow_out_of_envelope"] for x in z),
            "calibrated_true_model_residual_outside":sum(x["calibrated_out_of_envelope"] for x in z),
            "narrow_confident_authorizations":sum(x["narrow_confident_authorization"] for x in z),
            "calibrated_confident_authorizations":sum(x["calibrated_confident_authorization"] for x in z),
            "narrow_wrong_confident":sum(x["narrow_wrong_confident"] for x in z),
            "calibrated_wrong_confident":sum(x["calibrated_wrong_confident"] for x in z),
            "max_true_response_residual_m":max((x["source_true_response_residual_m"] for x in z),default=0),
            "narrow_task_success":sum(x["narrow_task_success"] for x in z),
            "calibrated_task_success":sum(x["calibrated_task_success"] for x in z)}
    tasks={task:summary([r for r in per if r["task"]==task]) for task in NARROW}
    assert [(tasks[t]["n"],tasks[t]["narrow_true_model_residual_outside"],
             tasks[t]["calibrated_true_model_residual_outside"]) for t in NARROW]==[(32,6,6),(32,6,0)]
    assert summary(per)["narrow_wrong_confident"]==0==summary(per)["calibrated_wrong_confident"]
    assert summary(per)["narrow_confident_authorizations"]==13
    assert summary(per)["calibrated_confident_authorizations"]==11
    assert summary(per)["narrow_task_success"]==58==summary(per)["calibrated_task_success"]
    return {
        "schema":"authentic_native_physx_response_envelope_miscoverage_not_equal_wrong_authorization_v1",
        "original_source_git_blob":PINNED_ORIGINAL_GIT_BLOB,
        "source_native_physics_worlds":640,
        "holdout_truly_unseen_prior_calibration_ids":True,
        "only_after_physical_execution_actual_native_target_used_for_truth":True,
        "training_calibration_n_each_task":32,
        "rank_bound_next_trial_unconditional_only_IF_exchangeable":1/33,
        "true_score_exchangeability_not_automatically_established":True,
        "model_coverage_not_synonymous_with_authorized_action_correctness_or_task_success":True,
        "total":summary(per),
        "by_task":tasks,
        "by_task_and_actual_joint_ACK":{
            f"{task}:{combo}":summary([r for r in per if r["task"]==task and r["actual_joint_ack"]==combo])
            for task in NARROW for combo in ("AA","AH","HA","HH")},
        "all_original_trial_source_only_rows":per,
        "physical_robot_safety_or_statistical_noninferiority_PROVED":False}
if __name__=="__main__":
    print("SOURCE_ORIGINAL_640_TRUE_TARGET_MODEL_MISCOVERAGE_EXPLORATORY",json.dumps(audit(),sort_keys=True))
