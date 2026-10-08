"""Independent offline verification of the 64-state frozen shadow observer result.

This is an author-written deterministic auditor of the original source JSONs,
NOT an independent simulator rerun, external replication, or safety certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from research.action_abi_shadow_aggregate import aggregate

EXPECTED = {
    "pull_cube": {
        "source": 32, "memory": 13, "projected": 32,
        "stateless": 12, "naive": 12, "shadow": 32,
    },
    "stack_cube": {
        "source": 29, "memory": 14, "projected": 29,
        "stateless": 1, "naive": 1, "shadow": 29,
    },
}
ORIGINAL_RUN = 37818985343
ORIGINAL_COMMIT = "f2bee90ef7ff2550351f579056688bd441044857"
ORIGINAL_ARTIFACT = 11568143703
ORIGINAL_ARTIFACT_ZIP_SHA256 = (
    "f5164ebe8e2ddf0db0acb0cefa5f11f90ac02ad39743959a19fda06829fb3420"
)
SOURCE_BLOB = "285a7457e4aa05240b970e5550bcf06942535ceb"
SOURCE_FILE_NAMES = [
    *(f"abi_shadow_{task}_chunk_{j}.json"
      for task in ("pull_cube", "stack_cube") for j in range(4)),
    "shadow-64-full-aggregate.json",
]


def verify(folder: Path) -> tuple[dict, list[str]]:
    present = sorted(x.name for x in folder.glob("*.json"))
    if present != sorted(SOURCE_FILE_NAMES):
        raise ValueError(f"Original nine-JSON source inventory changed: {present}")
    recalculated = aggregate(folder)
    recorded = json.loads((folder / "shadow-64-full-aggregate.json").read_text())
    if recalculated != recorded:
        raise ValueError("Original complete aggregate does not match 64 source rows")
    if (recorded.get("n_original_task_states") != 64 or
            recorded.get("third_party_independently_reproduced") is not False or
            recorded.get("no_policy_training") is not True or
            recorded.get("source_commit") != "9ffa86c6d3a86d2cee44b6e13c560033a8b373cf"):
        raise ValueError("Source-protocol or third-party execution claim changed")
    for task, expected in EXPECTED.items():
        row = recorded["results"][task]
        if (row["n"] != 32 or row["success"] != expected
                or row["matched_episode_outcomes"] != 32
                or row["live_only"] != 0 or row["shadow_only"] != 0
                or row["max_goal_position_residual_m"] > 1e-4
                or row["shadow_observer_gate"] != "MATCHED"
                or row["source_competent"] is not True):
            raise ValueError(f"Unexpected original {task} method outcome")
    checksums = [
        hashlib.sha256((folder / f).read_bytes()).hexdigest() + "  " + f
        for f in SOURCE_FILE_NAMES
    ]
    return recorded, checksums


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--sha256-file", type=Path, default=None)
    args = parser.parse_args()
    result, checksums = verify(args.input_dir)
    if args.sha256_file is not None:
        args.sha256_file.write_text("\n".join(checksums) + "\n")
    for name in EXPECTED:
        s = result["results"][name]
        print(name, json.dumps({
            "success": s["success"],
            "live_shadow_matches": s["matched_episode_outcomes"],
            "goal_position_residual_m": s["max_goal_position_residual_m"],
            "goal_rotation_residual_rad": s["max_goal_rotation_residual_rad"],
            "bounded_steps": s["nonexact_projection_steps"],
        }, sort_keys=True))
    print("VERIFIED: nine unchanged source JSONs in complete 64-state cohort")
    if args.sha256_file is not None:
        print(f"Source SHA256SUMS written: {args.sha256_file}")


if __name__ == "__main__":
    main()
