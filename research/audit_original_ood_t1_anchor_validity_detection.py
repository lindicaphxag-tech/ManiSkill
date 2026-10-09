"""Source-only failure audit: t1 known-action model-validity proxy vs t4
TRUE response-model coverage, after actual reconfigured 7-joint Panda PhysX.

The original t4 actual native target labels are NEVER available to the
controller: this is a retrospective model error detector audit only.
"""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
SOURCE=Path("research/frozen_policy_transfer/evidence/ood_pd_drive_known_ack_anchor_original64_960101_970132/INDEPENDENT_PANDA_PHYSX_OOD_ANCHOR_REAL640.json")
ORIGINAL_GIT_BLOB="2fbbd40b7a91a347fd7afa004a8b1c1c4042b749"

def git_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def independent_detector_audit():
    raw=SOURCE.read_bytes()
    if git_sha(raw)!=ORIGINAL_GIT_BLOB:
        raise ValueError("Changed genuine source-only original all64 / 640 actual PhysX physical worlds")
    original=json.loads(raw)
    if original["source_original_native_physx_worlds"]!=640 or len(original["all_original_trial_rows"])!=64:
        raise ValueError("Incomplete original real PhysX study")
    rows=[]
    for z in original["all_original_trial_rows"]:
        e=z["narrow_public_evidence"]
        history=e["audit_only_true_candidate_indices"]
        if len(history)!=1:
            raise ValueError("Actual target not represented by exactly one complete target-history candidate")
        truthscore=e["candidate_residuals_m"][history[0]]
        eps=e["prior_training_epsilon_m"]
        if not all(map(math.isfinite,[truthscore,eps])) or eps<=0:
            raise ValueError("Invalid frozen response model source provenance")
        invalid=bool(truthscore>eps)
        a=z["anchor_known_t1_evidence"]
        if a.get("source_ack_at_t1_known_delivered") is not True or a.get(
                "native_private_target_getter_NOT_USED_in_anchor") is not True:
            raise ValueError("Pre-fault anchor used untrusted or private physical source")
        if z["narrow_public_evidence"]["wrong_confident"] or z["anchor_public_evidence"]["wrong_confident"]:
            raise ValueError("Audit in this cohort observed an incorrect confident history; re-evaluate detector claim")
        rows.append({"task":z["task"],"seed":z["seed"],"drive_gain_mode":z["physics_drive_mode"],
                    "joint_truth":z["true_joint_ack"],
                    "response_invalid_ACTUAL_NATIVE_TARGET_AUDIT_ONLY":invalid,
                    "known_t1_anchor_passed_FROM_PUBLIC_ONLY":bool(a["passes"]),
                    "actual_post_t4_true_history_residual_m":truthscore,
                    "frozen_epsilon_m":eps,
                    "old_authorized_public_history":e["authorized"],
                    "anchor_authorized_public_history":z["anchor_public_evidence"]["authorized"],
                    "old_success":z["narrow_success"],
                    "anchor_success":z["anchor_success"]})
    def g(xs):
        tp=sum(x["response_invalid_ACTUAL_NATIVE_TARGET_AUDIT_ONLY"] and not x["known_t1_anchor_passed_FROM_PUBLIC_ONLY"] for x in xs)
        fn=sum(x["response_invalid_ACTUAL_NATIVE_TARGET_AUDIT_ONLY"] and x["known_t1_anchor_passed_FROM_PUBLIC_ONLY"] for x in xs)
        fp=sum(not x["response_invalid_ACTUAL_NATIVE_TARGET_AUDIT_ONLY"] and not x["known_t1_anchor_passed_FROM_PUBLIC_ONLY"] for x in xs)
        tn=sum(not x["response_invalid_ACTUAL_NATIVE_TARGET_AUDIT_ONLY"] and x["known_t1_anchor_passed_FROM_PUBLIC_ONLY"] for x in xs)
        return {"n":len(xs),
                "invalid_native_response_correctly_flagged_before_unknown_ACK":tp,
                "invalid_native_response_MISSED_by_known_t1_anchor":fn,
                "valid_response_false_alerted_by_known_t1_anchor":fp,
                "valid_response_anchor_correct_pass":tn,
                "sensitivity_to_later_model_failure":tp/(tp+fn) if tp+fn else None,
                "specificity_to_later_validity":tn/(tn+fp) if tn+fp else None}
    total=g(rows)
    if total!={"n":64,
                "invalid_native_response_correctly_flagged_before_unknown_ACK":4,
                "invalid_native_response_MISSED_by_known_t1_anchor":4,
                "valid_response_false_alerted_by_known_t1_anchor":30,
                "valid_response_anchor_correct_pass":26,
                "sensitivity_to_later_model_failure":.5,
                "specificity_to_later_validity":26/56}:
        raise ValueError("Original source evidence does not reproduce published model-validity negative claim")
    return {"schema":"original_true_640_PhysX_response_domain_anchor_model_validity_confusion_NEGATIVE_v1",
            "original_actual_physx_independent_source_all64_blob":ORIGINAL_GIT_BLOB,
            "source_truly_physical_Panda_PD_drive_shift_and_4_ACK_truths":True,
            "source_post_step_private_true_target_is_ONLY_label_not_detector_input":True,
            "training_and_new_OOD_source_reset_disjoint":True,
            "total":total,
            "task":{task:g([x for x in rows if x["task"]==task]) for task in ("pull_cube","stack_cube")},
            "physical_drive_gain":{m:g([x for x in rows if x["drive_gain_mode"]==m]) for m in ("slow","fast")},
            "by_actual_joint_truth":{t:g([x for x in rows if x["joint_truth"]==t]) for t in ("AA","AH","HA","HH")},
            "all_individually_audited_original_true_native_studies":rows,
            "t1_anchor_does_not_certify_t4_response_regime_under_dynamics_shift":True,
            "no_risk_guarantee_or_statistically_supported_safety_improvement":True}
if __name__=="__main__":
    print("TRUE_PANDA_PHYSX_PRE_FAULT_ANCHOR_FAILURE_CONFUSION",
          json.dumps(independent_detector_audit(),sort_keys=True))
