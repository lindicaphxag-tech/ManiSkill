"""Compare FIRST preregistered PhysX run with a SAME-SEED no-tuning reexecution.

Reads only public original JSONs. Never counts repeat as independent cohort.
For source provenance and exact file digests, see
research/frozen_policy_transfer/BOUNDED_QUERY_PHYSX_16_ORIGINAL_RESULT.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CANONICAL = {
    "pull_cube": "bcbdcf8eea1f214dd4e6106402f45eaf19bcfe46fbff3edf9b74cad0e31da4cc",
    "stack_cube": "8c0ff8cd0096562622c515619853c1939ac073d5c77a9deba597921c05d486ac",
}
REPEAT = {
    "pull_cube": "bcbdcf8eea1f214dd4e6106402f45eaf19bcfe46fbff3edf9b74cad0e31da4cc",
    "stack_cube": "017168fe746ecbe568a328a49814b7aa01157eaa269aa5eea4b54ac679f811f3",
}
ROOT = Path("research/frozen_policy_transfer/evidence/unknown_ack_bounded_query_16")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def exact_or_float_diff(a, b, path, changes):
    # bool is intentionally distinct from int; no success flags can change.
    if type(a) is not type(b):
        raise ValueError(f"Type change {path}: {type(a)} != {type(b)}")
    if isinstance(a, dict):
        if a.keys() != b.keys():
            raise ValueError(f"Field schema changed at {path}")
        for k in a:
            exact_or_float_diff(a[k], b[k], f"{path}.{k}", changes)
    elif isinstance(a, list):
        if len(a) != len(b):
            raise ValueError(f"Trial denominator/sequence changed at {path}")
        for i, (x, y) in enumerate(zip(a, b)):
            exact_or_float_diff(x, y, f"{path}[{i}]", changes)
    elif isinstance(a, float):
        if a != b:
            if not (abs(a-b) <= 1e-12):
                raise ValueError(f"Floating numerical difference exceeded 1e-12 at {path}")
            changes.append((path, abs(a-b)))
    elif a != b:
        raise ValueError(f"NONFLOAT/BOOLEAN difference at {path}: {a!r} != {b!r}")


def compare(repeat_dir: Path):
    summary = {}
    for task in ("pull_cube", "stack_cube"):
        filename = f"unknown_ack_bounded_query_{task}_original8.json"
        orig_raw = (ROOT/filename).read_bytes()
        repeat_raw = (repeat_dir/filename).read_bytes()
        if sha256(orig_raw) != CANONICAL[task]:
            raise ValueError(f"{task} first source bytes changed")
        if sha256(repeat_raw) != REPEAT[task]:
            raise ValueError(f"{task} same-seed rerun bytes changed")
        original = json.loads(orig_raw)
        repeated = json.loads(repeat_raw)
        delta = []
        exact_or_float_diff(original, repeated, task, delta)
        original_pairs = [(row["seed"], row["success_once"]) for row in original["episodes"]]
        repeat_pairs = [(row["seed"], row["success_once"]) for row in repeated["episodes"]]
        if original_pairs != repeat_pairs or len(original_pairs) != 8:
            raise ValueError("Task success or source/target cohort was not identical")
        summary[task] = {
            "truly_new_task_states": 0,
            "same_original_task_states": 8,
            "all_paired_official_success_flags_identical": True,
            "changed_numeric_float_leaves": len(delta),
            "max_abs_numeric_float_difference": max([v for _, v in delta], default=0.0),
            "non_numeric_or_boolean_changes": 0,
            "first_run_source_sha256": CANONICAL[task],
            "same_seed_repeat_source_sha256": REPEAT[task],
        }
    if summary["pull_cube"]["changed_numeric_float_leaves"] != 0:
        raise ValueError("Unanticipated PullCube changes")
    if summary["stack_cube"]["changed_numeric_float_leaves"] != 107:
        raise ValueError("Unanticipated StackCube numeric changes")
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--repeat-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    result={
        "status":"SAME_SEED_REPRODUCIBILITY_NOT_INDEPENDENT_REPLICATION",
        "first_preregistered_run":37826881229,
        "later_same_seed_repeat_run":37828004254,
        "identical_experimental_runner_git_blob":"1dc653cdc44e422c8340475ad00f828b3a41eb4f",
        "new_sample_count":0,
        "trials":compare(args.repeat_dir),
    }
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    print(json.dumps(result, sort_keys=True))


if __name__=="__main__":
    main()
