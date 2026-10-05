from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h5py


REL = Path("assets") / "{cond}" / "demos" / "PegInsertionSide-v1" / "motionplanning"
STEM = "trajectory.state.pd_ee_delta_pose.physx_cpu"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(root: Path, cond: str):
    path = root / Path(str(REL).format(cond=cond)) / f"{STEM}.json"
    return path, json.loads(path.read_text())


def episode_ids(data):
    return [int(ep["episode_id"]) for ep in data["episodes"]]


def copy_subset(src_h5: Path, dst_h5: Path, ids: list[int]):
    with h5py.File(src_h5, "r") as src, h5py.File(dst_h5, "w") as dst:
        for key, value in src.attrs.items():
            dst.attrs[key] = value
        for episode_id in ids:
            key = f"traj_{episode_id}"
            if key not in src:
                raise KeyError(f"{src_h5}: missing {key}")
            src.copy(key, dst, name=key)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--n-common", type=int, default=100)
    parser.add_argument("--attempted-prefix", type=int, default=150)
    args = parser.parse_args()

    conditions = ["00", "10", "01", "11"]
    loaded = {}
    for cond in conditions:
        json_path, data = load_json(args.root, cond)
        loaded[cond] = (json_path, data)

    sets = {cond: set(episode_ids(data)) for cond, (_, data) in loaded.items()}
    common = set.intersection(*(sets[c] for c in conditions))

    # Preserve the original episode order from the baseline condition.
    baseline_order = episode_ids(loaded["00"][1])
    selected = [ep for ep in baseline_order if ep in common][: args.n_common]

    report = {
        "attempted_prefix": args.attempted_prefix,
        "requested_common": args.n_common,
        "saved_counts": {c: len(sets[c]) for c in conditions},
        "common_count": len(common),
        "selected_count": len(selected),
        "selected_episode_ids": selected,
    }

    if len(selected) < args.n_common:
        out = args.root / "factorial_dataset_manifest.json"
        out.write_text(json.dumps(report, indent=2) + "\n")
        raise SystemExit(
            f"only {len(selected)} common episodes; primary {args.n_common}-demo comparison is invalid"
        )

    for cond in conditions:
        base = args.root / Path(str(REL).format(cond=cond))
        src_h5 = base / f"{STEM}.h5"
        src_json, data = loaded[cond]
        out_h5 = base / f"{STEM}.common{args.n_common}.h5"
        out_json = base / f"{STEM}.common{args.n_common}.json"

        by_id = {int(ep["episode_id"]): ep for ep in data["episodes"]}
        subset_json = dict(data)
        subset_json["episodes"] = [by_id[i] for i in selected]
        copy_subset(src_h5, out_h5, selected)
        out_json.write_text(json.dumps(subset_json, indent=2) + "\n")

        report.setdefault("datasets", {})[cond] = {
            "source_h5": str(src_h5),
            "source_json": str(src_json),
            "h5": str(out_h5),
            "json": str(out_json),
            "h5_sha256": sha256(out_h5),
            "json_sha256": sha256(out_json),
        }

    (args.root / "factorial_dataset_manifest.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
