from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


REFS = {
    "00": "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
    "10": "a231074ef562a9638e24c3f9a4d35bb70d4960d1",
    "01": "cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b",
    "11": "24dcccba3d0aeae56b6fba1f5168e22cc340ab71",
}


def scalar_summary(run_dir: Path, tag: str):
    acc = EventAccumulator(str(run_dir))
    acc.Reload()
    points = acc.Scalars(tag)
    if not points:
        raise RuntimeError(f"{run_dir}: missing {tag}")
    return {
        "best": max(float(p.value) for p in points),
        "final": float(points[-1].value),
        "final_step": int(points[-1].step),
        "curve": [{"step": int(p.step), "value": float(p.value)} for p in points],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    manifest = json.loads((args.root / "factorial_dataset_manifest.json").read_text())
    result = {
        "schema_version": 1,
        "seed": args.seed,
        "task": "PegInsertionSide-v1",
        "policy": "ManiSkill state Diffusion Policy",
        "primary_common_episode_ids": manifest["selected_episode_ids"],
        "conditions": {},
        "claim_boundary": (
            "Maintainer-requested policy-level factorial validation. "
            "Does not count as upstream adoption until retained by ManiSkill."
        ),
    }

    for cond, ref in REFS.items():
        run_dir = (
            args.root
            / "worktrees"
            / cond
            / "examples"
            / "baselines"
            / "diffusion_policy"
            / "runs"
            / f"pr1495_factorial_{cond}_seed{args.seed}"
        )
        result["conditions"][cond] = {
            "source_commit": ref,
            "dataset_h5_sha256": manifest["datasets"][cond]["h5_sha256"],
            "dataset_json_sha256": manifest["datasets"][cond]["json_sha256"],
            "success_once": scalar_summary(run_dir, "eval/success_once"),
            "success_at_end": scalar_summary(run_dir, "eval/success_at_end"),
        }

    out = args.root / f"peg_insertion_factorial_seed{args.seed}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
