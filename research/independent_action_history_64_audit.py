"""Strict full-denominator external audit of the precommitted independent observer cohort."""
import json
import math
import sys
from pathlib import Path

TASKS = {
    "pull_cube": ("PullCube-v1", 83001, "74ae6a09b9af5e9e50dc71944f2e99316a8b67b02f3a96ca45df4a6d53dc1bd7"),
    "stack_cube": ("StackCube-v1", 93001, "e63cc8d8ffdca3d03553a21ea615c759b2b224493a7e7e12bee7efc29d5bad9c"),
}
ARMS = ("source", "memory", "projected", "observer", "stateless", "naive")
REVISION = "6bdeb28810330ab5425ccd629bb561c58a56ff85"
PROTOCOL = "research/ACTION_ABI_HISTORY_OBSERVER_PREDECLARED_V1.json"


def audit_task(root, task, spec):
    name, first, sha = spec
    source = {}
    for chunk in range(4):
        file = root / f"independent_observer_{task}_{chunk}.json"
        if not file.is_file():
            raise ValueError(f"Missing original source artifact: {file.name}")
        data = json.loads(file.read_text())
        seeds = list(range(first + chunk * 8, first + chunk * 8 + 8))
        if (data.get("task") != name or data.get("checkpoint_sha256") != sha
            or data.get("hf_revision") != REVISION or data.get("protocol") != PROTOCOL
            or data.get("backend") != "physx_cpu" or data.get("training_performed") is not False
            or data.get("seed_list") != seeds or data.get("seed_chunk") != str(chunk)
            or data.get("all_preregistered_seeds") != [seeds[0], seeds[-1]]):
            raise ValueError(f"Frozen identity/chunk violation: {file.name}")
        rows = data.get("episodes", [])
        if len(rows) != 8 or [x.get("seed") for x in rows] != seeds:
            raise ValueError("Missing, reordered, or repeated source episodes")
        for arm in ARMS:
            if data["success_count"].get(arm) != sum(bool(x.get("success_once", {}).get(arm, False)) for x in rows):
                raise ValueError("Original source success count mismatch")
        for row in rows:
            seed = row["seed"]
            if seed in source:
                raise ValueError("Duplicate seed")
            for arm in ARMS:
                succ = row.get("success_once", {}).get(arm)
                if succ is None and arm == "memory" and "memory" in row.get("refusals", {}):
                    succ = False
                if type(succ) is not bool:
                    raise ValueError(f"Missing genuine binary outcome {seed} / {arm}")
                if row.get("refusals", {}).get(arm) and succ:
                    raise ValueError("Refused action cannot count as episode success")
            err = row.get("observer_end_target_error")
            if not isinstance(err, dict) or any(
                type(err.get(key)) not in (int,float)
                or not math.isfinite(err[key]) or err[key] < 0
                for key in ("max_position_abs", "rotation_rad")
            ):
                raise ValueError("Missing/nonfinite observer endpoint audit")
            for other, residual in row.get("initial_obs_diff", {}).items():
                if other not in ARMS[1:] or not 0 <= residual <= 5e-4:
                    raise ValueError("Mismatched initial physical task condition")
            for arm, events in row.get("approximations", {}).items():
                if any(event.get("exactness") != "NOT_EXACT" for event in events):
                    raise ValueError("Approximate controller action mislabeled exact")
            source[seed] = row
    if set(source) != set(range(first, first + 32)):
        raise ValueError("Incomplete prespecified full denominator")
    rows = [source[s] for s in sorted(source)]
    correct = lambda row, arm: bool(row.get("success_once", {}).get(arm, False))
    counts = {arm: sum(correct(row,arm) for row in rows) for arm in ARMS}
    pairs = {}
    for baseline in ("projected","stateless","naive"):
        pairs[baseline] = {
            "observer_only":sum(correct(r,"observer") and not correct(r,baseline) for r in rows),
            "baseline_only":sum(correct(r,baseline) and not correct(r,"observer") for r in rows),
        }
    maxpos = max(r["observer_end_target_error"]["max_position_abs"] for r in rows)
    maxrot = max(r["observer_end_target_error"]["rotation_rad"] for r in rows)
    agreements = 32 - pairs["projected"]["observer_only"] - pairs["projected"]["baseline_only"]
    competence = counts["source"] >= 24
    passed = agreements >= 30 and maxpos <= 3e-5 and maxrot <= 3e-4
    return {
        "n":32, "seeds":[first,first+31], "source_competent":competence,
        "evidence_gate": "SOURCE_INCOMPETENT" if not competence else
            "MATCHED" if passed else "FALSIFIED",
        "success":counts, "paired_discordances":pairs,
        "observer_vs_live_outcome_agreement":agreements,
        "max_terminal_target_position_error_m":maxpos,
        "max_terminal_target_rotation_error_rad":maxrot,
        "nonexact_projection_events":{arm:sum(len(r.get("approximations",{}).get(arm,[])) for r in rows)
            for arm in ("projected","observer","stateless")},
        "original_episode_records":rows,
    }


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: independent_action_history_64_audit.py INPUT_DIR OUTPUT.json")
    root, dest = Path(sys.argv[1]), Path(sys.argv[2])
    evidence = {
        "status":"owner_operated_not_independently_adopted",
        "preregistered_cohort":"research/INDEPENDENT_HISTORY_OBSERVER_REDACTED_64_PREREG_20261009.json",
        "preoutcome_amendment":"research/INDEPENDENT_OBSERVER_64_PREOUTCOME_AMENDMENT.json",
        "independent_observer_source_sha":"0865e6d50ec30d6a069e2d7dfee1f9be834c2c21",
        "not_a_nan_redaction_experiment":True,
        "results":{name:audit_task(root,name,spec) for name,spec in TASKS.items()},
    }
    dest.write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n")
    print("INDEPENDENT_HISTORY_64", json.dumps({
        k:{key:r[key] for key in ("evidence_gate","success","paired_discordances",
                                "max_terminal_target_position_error_m",
                                "max_terminal_target_rotation_error_rad")}
        for k,r in evidence["results"].items()
    }, sort_keys=True))


if __name__ == "__main__":
    main()
