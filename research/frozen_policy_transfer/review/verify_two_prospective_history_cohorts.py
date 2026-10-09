"""Recompute BOTH published frozen-PPO native-PhysX source cohorts from unmodified bytes.

Python stdlib only. The two cohorts were independently preregistered and
tested, and use closely related but separately implemented history-selection
rules; a pooled figure is descriptive, NOT one identical pooled estimator.

This tool audits archive integrity, EVERY original task-state row, actual
two-command hold intervention on the studied adapter, private query
provenance, whole-history selection and matched task-level outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "research/frozen_policy_transfer/evidence"
NEW = "fault_public_t3_fourhistory_or_t4_query"
FIXED = "fault_always_single_privileged_query"
SELECTIVE = "fault_robust_then_single_privileged_query"
NO_QUERY = "fault_robust_two_history_without_query"
STUDIES = {
    "primary64": {
        "folder": "discrete_hypothesis_ppo_original64_840001_850032",
        "prefix": "public_hypothesis", "suffix": "original8",
        "audit": "independent_new64_full_source_audit.json",
        "per_task": 32, "per_shard": 8, "starts": {"pull_cube": 840001, "stack_cube": 850001},
        "expected": {"new_success": 58,"new_reads": 39,"gated_success": 58,
                     "gated_reads": 57,"public_unique": 25,"wrong_confident": 0,"fixed_success": 58},
    },
    "replication32": {
        "folder": "survivor_fullpose_original32_860001_870016",
        "prefix": "survivor_fullpose", "suffix": "original4",
        "audit": "full_original_survivor_fullpose_new32_audit.json",
        "per_task": 16, "per_shard": 4, "starts": {"pull_cube": 860001, "stack_cube": 870001},
        "expected": {"new_success": 28,"new_reads": 22,"gated_success": 28,
                     "gated_reads": 27,"public_unique": 10,"wrong_confident": 0,"fixed_success": 28},
    }
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_manifest(folder: Path, config: dict) -> dict[str, str]:
    """Never trust a new summary if a raw byte or source filename changes."""
    manifest = folder / "SHA256SUMS"
    require(manifest.is_file(), "Original full-source SHA-256 manifest missing")
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        chunks = line.strip().split(maxsplit=1)
        require(len(chunks) == 2 and len(chunks[0]) == 64, "Malformed original SHA-256 manifest")
        digest, filename = chunks
        filename = filename.removeprefix("./")
        require("/" not in filename and "\\" not in filename, "Invalid nested input filename")
        require(filename not in entries, "Duplicate original file manifest item")
        entries[filename] = digest
    wanted = {config["audit"]}
    for task in config["starts"]:
        for i in range(4):
            stem = f"{config['prefix']}_{task}_chunk{i}"
            wanted.add(f"{stem}_{config['suffix']}.json")
            wanted.add(f"{stem}_audit.json")
    require(set(entries) == wanted, "Manifest does not cover exactly 17 original source files")
    require({f.name for f in folder.glob("*.json")} == wanted,
            "Source archive has an unexpected/missing raw JSON file")
    for filename, digest in entries.items():
        require(hashlib.sha256((folder / filename).read_bytes()).hexdigest() == digest,
                f"Original PhysX source bytes changed: {filename}")
    return entries


def exact_one_sided_zero_upper(n: int, alpha=0.05) -> float:
    """Exact iid Bernoulli one-sided upper bound for ZERO observed events.

    This does NOT establish random seed exchangeability, future hardware
    reliability, policy population transfer or model-certification.
    """
    require(isinstance(n, int) and not isinstance(n, bool) and n >= 1,
            "Need at least one valid observation")
    return 1.0 - alpha ** (1.0/n)


def check(config: dict, root: Path) -> dict:
    folder = root / config["folder"]
    hashes = sha_manifest(folder, config)
    saved = json.loads((folder / config["audit"]).read_text(encoding="utf-8"))
    n = 2 * config["per_task"]
    require(saved["genuine_source_physx_reset_states"] == n and
            saved["genuine_physics_controller_worlds"] == 8*n and
            saved["double_fault_exposure_population"] == n and
            saved["complete_double_fault_gate_passes"] is True,
            "Missing original physics task populations / twice-held actual actuator faults")
    task_report = {}
    all_rows = []
    all_seeds = []
    for task,first in config["starts"].items():
        rows = []
        for chunk in range(4):
            stem = f"{config['prefix']}_{task}_chunk{chunk}"
            file = folder / f"{stem}_{config['suffix']}.json"
            shard = json.loads(file.read_text(encoding="utf-8"))
            seeds = list(range(first + chunk*config["per_shard"],
                               first + (chunk+1)*config["per_shard"]))
            require(shard["task"] == ("PullCube-v1" if task=="pull_cube" else "StackCube-v1")
                    and shard["original_seed_population"] == seeds
                    and shard["real_physx_simulator"] is True
                    and shard["frozen_model_retrained"] is False
                    and shard["fault_is_native_target_hold_not_network_loss"] is True,
                    "Unregistered fake or retrained physics source")
            require(len(shard["episodes"]) == config["per_shard"] and
                    [x["seed"] for x in shard["episodes"]] == seeds,
                    "Original task shard denominator changed")
            for row in shard["episodes"]:
                require(row["task"] == shard["task"], "Row task identity changed")
                require(set(row["success_once"]) == set(row["privileged_target_readback_decision_count"]),
                        "Incomplete original controller arm comparison")
                require(all(type(v) is bool for v in row["success_once"].values()),
                        "Not an actual binary native task success observation")
                faults = row["faults"].get(NEW)
                require(isinstance(faults,list) and len(faults)==2
                        and [e.get("step") for e in faults] == [2,3],
                        "Native actuator faults are not both physically executed")
                require(all(e.get("actual_native_arm_command")=="all_zero_hold"
                            and e.get("controller_execution_ack_seen_by_adapter")=="unknown"
                            and e.get("actual_native_target_hold_verified") is True
                            for e in faults),
                        "Incorrect native physical command hold/ACK truth")
                public = row["public_t3_evidence"]
                require(public["physical_candidate_count"]==4 and
                        public["empirical_motion_envelope_NOT_physical_safety_certificate"] is True
                        and public["audit_only_hidden_target_was_NOT_decision_input"] is True,
                        "One of four complete possible target histories or public evidence provenance absent")
                q = row["privileged_target_readback_decision_count"]
                label = public.get("authorized")
                require(type(label) is bool and q[NEW] == int(not label),
                        "Physical public inference/actual private controller-read budget mismatch")
                if label:
                    idx = public.get("selected_candidate_index")
                    require(type(idx) is int and 0 <= idx < 4 and
                            public.get("wrong_confident") is False,
                            "Public history label is invalid or falsely confident")
                else:
                    require(public.get("selected_candidate_index") is None,
                            "History claimed confidently on ambiguous physical public movement")
                require(q[FIXED]==1 and q[SELECTIVE] in (0,1) and q[NO_QUERY]==0,
                        "Fixed/old selective/zero-query information cost not faithful")
                rows.append(row)
                all_rows.append(row)
                all_seeds.append((task,row["seed"]))
        require(len(rows) == config["per_task"], "Expected full task denominator")
        gated = SELECTIVE if task=="pull_cube" else FIXED
        def succ(key):
            return sum(int(row["success_once"][key]) for row in rows)
        def reads(key):
            return sum(row["privileged_target_readback_decision_count"][key] for row in rows)
        summary = {
            "n": len(rows), "new_success": succ(NEW), "gated_success": succ(gated),
            "new_reads": reads(NEW), "gated_reads": reads(gated),
            "fixed_success": succ(FIXED), "fixed_reads": reads(FIXED),
            "public_unique": sum(int(row["public_t3_evidence"]["authorized"]) for row in rows),
            "wrong_confident": sum(int(row["public_t3_evidence"].get("wrong_confident") is True) for row in rows),
            "new_only": sum(row["success_once"][NEW] and not row["success_once"][gated] for row in rows),
            "task_gated_only": sum(row["success_once"][gated] and not row["success_once"][NEW] for row in rows),
            "same_task_outcomes": sum(row["success_once"][NEW]==row["success_once"][gated] for row in rows),
        }
        prior = saved["by_task"][task]
        require(summary["new_success"]==prior["outcomes"]["new_public"]["success"] and
                summary["new_reads"]==prior["outcomes"]["new_public"]["private_reads"] and
                summary["gated_success"]==prior["outcomes"]["task_preselected"]["success"] and
                summary["gated_reads"]==prior["outcomes"]["task_preselected"]["private_reads"] and
                summary["public_unique"]==prior["public_confident_authorizations"] and
                summary["wrong_confident"]==prior["public_wrong_confident_authorizations"],
                "Original per-seed recomputation differs from archived independent task audit")
        task_report[task] = summary
    require(len(all_seeds)==n and len(set(all_seeds))==n, "Repeated original seed identity")
    summary = {
        "n":n, "physical_worlds":8*n,
        **{k:sum(task_report[t][k] for t in task_report)
           for k in ("new_success","gated_success","new_reads","gated_reads",
                      "fixed_success","fixed_reads","public_unique","wrong_confident",
                      "new_only","task_gated_only","same_task_outcomes")},
    }
    exp = config["expected"]
    for name,want in exp.items():
        require(summary[name]==want, f"Pre-reported {name} was incorrect")
    require(summary["new_only"]==summary["task_gated_only"]==0 and
            summary["same_task_outcomes"]==n,
            "Original task success discordance was suppressed")
    require(summary["new_reads"]+summary["public_unique"]==n,
            "Public history identification/query accounting not exhaustive")
    return {
        "descriptive_paired_full_source": summary,
        "by_task": task_report,
        "exact_one_sided_95pct_upper_on_unobserved_future_label_error_CONDITIONAL_iid":
            exact_one_sided_zero_upper(summary["public_unique"]),
        "exact_one_sided_95pct_upper_on_unobserved_future_binary_discordance_CONDITIONAL_iid":
            exact_one_sided_zero_upper(n),
        "source_integrity_original_sha256_files":len(hashes),
        "source_provenance_NOT_external_lab":True,
    }


def analyze(root:Path=EVIDENCE):
    studies = {name:check(cfg,root) for name,cfg in STUDIES.items()}
    summaries = [v["descriptive_paired_full_source"] for v in studies.values()]
    total={k:sum(q[k] for q in summaries) for k in
           ("n","physical_worlds","new_success","gated_success","new_reads",
            "gated_reads","public_unique","wrong_confident","new_only","task_gated_only")}
    total["read_reduction_fraction_descriptive"]=1-total["new_reads"]/total["gated_reads"]
    return {
       "schema":"reviewer_paired_original_source_64_plus_32_two_separate_protocols_v1",
       "studies":studies,
       "descriptive_sum_of_TWO_SEPARATELY_PREREGISTERED_protocols_NOT_one_joint_trial":total,
       "strict_claim_limits":[
          "No future physics/calibration envelope safety guarantee",
          "Upper bounds only under hypothetical iid within corresponding simulated cohort",
          "These are TWO related but separately implemented frozen controllers, NOT a single pooled estimator",
          "Observations limited to frozen PPO on one Panda controller chart",
          "No real hardware, packet reordering, VLA tasks, collision/force safety or external independent reproduction",
          "Zero paired discordances does NOT demonstrate statistical noninferiority",
          "Second 32-state PullCube task gated baseline spends TWO FEWER reads than new method",
       ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=EVIDENCE)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    d=analyze(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("TWO_PROSPECTIVE_COHORTS_SOURCE_AUTHENTICATED",json.dumps({
      "summary":d["descriptive_sum_of_TWO_SEPARATELY_PREREGISTERED_protocols_NOT_one_joint_trial"],
      "by_study":{k:v["descriptive_paired_full_source"] for k,v in d["studies"].items()}
    },sort_keys=True))


if __name__=="__main__":main()
