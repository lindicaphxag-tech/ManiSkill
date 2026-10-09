"""Auditable PRE-TEST task response error calibration. Training original past
32/task only. True native target getter is used to build an OFFLINE calibration
set, NEVER for a future holdout policy decision.

The order statistic is MAX of n=32 true target residuals, with the original
previous ε as floor. Exchangeable one-step coverage is MARGINAL only; this
DOES NOT imply a certified physics envelope, conditional OOD guarantee or
a newly proved conformal theorem.
"""
import hashlib, json, math
from pathlib import Path

ROOT=Path("research/frozen_policy_transfer/evidence/four_joint_truths_first_physx64_880001_890032")
HASHES={
"pull_cube":(
"e98d8d9fcf93e59aa98ba0185f7080d28d561d66",
"fe4f25210270ebfc4aa3081d33818f8180366cd1",
"02d57f1948ea8099cf96255b88219ef1207ebe22",
"473415eece5f0f45f7a3870ef1c5c902b0377451"),
"stack_cube":(
"a9e18b7858c520825c470c0731f4b06db6fa745f",
"4b7e80e6b76f4aeb4b8bac0e74cfd19ab0edefdb",
"9509ffdfbcf9c6a555479dad482093973bceb29a",
"0922836a7edee0f3413ca6b48bbc5c40ee41d8b3")}
OLD={"pull_cube":.006944262561376447,"stack_cube":.00719087965534261}
FROZEN={"pull_cube":.006944262561376447,"stack_cube":.02126739483653302}

def git_sha(contents):
    return hashlib.sha1(b"blob "+str(len(contents)).encode()+b"\x00"+contents).hexdigest()

def measure():
    ans={}
    for task,start in (("pull_cube",880001),("stack_cube",890001)):
        scores=[]
        seen=set()
        for chunk,sha in enumerate(HASHES[task]):
            path=ROOT/f"full_joint_ack_{task}_chunk{chunk}_original8.json"
            raw=path.read_bytes()
            if git_sha(raw)!=sha:
                raise ValueError("Original prior training physical source SHA changed: "+str(path))
            obj=json.loads(raw)
            if obj["original_seed_population"]!=list(range(start+8*chunk,start+8*chunk+8)):
                raise ValueError("Training has wrong ORIGINAL native PhysX physical state population")
            for episode in obj["episodes"]:
                seed=episode["seed"]
                if seed in seen:
                    raise ValueError("Duplicate physical training state")
                seen.add(seed)
                ev=episode["public_t4_evidence"]
                if (ev.get("audit_only_hidden_target_was_NOT_decision_input") is not True
                    or len(ev.get("candidate_residuals_m",[]))!=4):
                    raise ValueError("No complete real physics public history source")
                truth=ev.get("audit_only_true_candidate_indices",[])
                if len(truth)!=1:
                    raise ValueError("No unique old actual target audit-only label")
                score=ev["candidate_residuals_m"][truth[0]]
                if not isinstance(score,(float,int)) or not math.isfinite(score) or score<0:
                    raise ValueError("Nonfinite calibration truth residual")
                scores.append(float(score))
        if len(scores)!=32 or seen!=set(range(start,start+32)):
            raise ValueError("Not exactly 32 past actual known target residuals")
        mx=max(scores);chosen=max(OLD[task],mx)
        if chosen!=FROZEN[task]:
            raise ValueError("New method preregistered calibration is not source-derived")
        ans[task]={"n":32,"original_eps_m":OLD[task],"max_true_history_residual_m":mx,
                   "selected_authority_epsilon_m":chosen,
                   "physical_training_model_coverage":sum(x<=OLD[task] for x in scores),
                   "external_model_attestation":False,
                   "exchangeability_guaranteed":False,
                   "nominal_next_sample_one_sided_marginal_miscoverage_if_exchangeable_at_most":1/33}
    assert ans["pull_cube"]["physical_training_model_coverage"]==32
    assert ans["stack_cube"]["physical_training_model_coverage"]==23
    return ans

if __name__=="__main__":
    print("ORIGINAL_OLD32_TRUE_HISTORY_OFFLINE_CALIBRATION_NOT_TEST_OUTCOME",
          json.dumps(measure(),sort_keys=True))
