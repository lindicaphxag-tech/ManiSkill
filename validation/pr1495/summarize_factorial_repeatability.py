#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import h5py

VARIANTS = ("old_old", "controller_only", "converter_only", "combined")


def jaccard(a, b):
    a, b = set(a), set(b)
    union = a | b
    return 1.0 if not union else len(a & b) / len(union)


def load_success(path: Path, source_ids: list[int]) -> dict:
    meta_path = path.with_suffix(".json")
    if not path.exists() or not meta_path.exists():
        raise FileNotFoundError(path)
    meta = json.loads(meta_path.read_text())
    episodes = meta.get("episodes", [])
    if len(episodes) != len(source_ids):
        raise RuntimeError(f"{path}: expected {len(source_ids)} episodes, got {len(episodes)}")
    json_success = [bool(ep.get("success", False)) for ep in episodes]
    h5_success = []
    with h5py.File(path, "r") as h5:
        keys = sorted(
            [k for k in h5.keys() if k.startswith("traj_")],
            key=lambda k: int(k.split("_", 1)[1]),
        )
        if len(keys) != len(source_ids):
            raise RuntimeError(f"{path}: expected {len(source_ids)} H5 trajectories, got {len(keys)}")
        for key in keys:
            group = h5[key]
            ok = bool(group["success"][-1]) if "success" in group and len(group["success"]) else False
            h5_success.append(ok)
    if json_success != h5_success:
        raise RuntimeError(f"{path}: JSON/H5 success mismatch")
    success_ids = [source_ids[i] for i, ok in enumerate(json_success) if ok]
    return {
        "success_count": len(success_ids),
        "success_rate": len(success_ids) / len(source_ids),
        "success_episode_ids": success_ids,
        "success_vector": json_success,
    }


def summarize_variant(root: Path, name: str, repeats: int, source_ids: list[int]) -> dict:
    runs = []
    for repeat in range(repeats):
        h5 = root / name / f"repeat_{repeat}" / "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
        run = load_success(h5, source_ids)
        run["repeat"] = repeat
        runs.append(run)
    counts = [r["success_count"] for r in runs]
    mean = sum(counts) / len(counts)
    variance = sum((x - mean) ** 2 for x in counts) / len(counts)
    distinct = sorted({tuple(r["success_episode_ids"]) for r in runs})
    pairwise = [
        jaccard(runs[i]["success_episode_ids"], runs[j]["success_episode_ids"])
        for i, j in combinations(range(repeats), 2)
    ]
    frequency = {
        str(ep): sum(ep in r["success_episode_ids"] for r in runs) / repeats
        for ep in source_ids
    }
    return {
        "runs": runs,
        "success_counts": counts,
        "mean_success_count": mean,
        "population_variance_success_count": variance,
        "distinct_success_sets": [list(x) for x in distinct],
        "distinct_success_set_count": len(distinct),
        "episode_success_frequency": frequency,
        "pairwise_success_set_jaccard": pairwise,
        "min_pairwise_jaccard": min(pairwise) if pairwise else 1.0,
        "exactly_repeatable": len(distinct) == 1,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--raw-json", type=Path, required=True)
    p.add_argument("--repeats", type=int, default=5)
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--identity-json", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()

    raw = json.loads(a.raw_json.read_text())
    raw_eps = raw.get("episodes", [])[: a.count]
    if len(raw_eps) != a.count:
        raise RuntimeError(f"raw metadata has only {len(raw_eps)} episodes")
    source_ids = [int(ep["episode_id"]) for ep in raw_eps]
    identities = json.loads(a.identity_json.read_text())
    if set(identities) != set(VARIANTS):
        raise RuntimeError("identity set does not match four factorial cells")

    variants = {
        name: summarize_variant(a.root, name, a.repeats, source_ids)
        for name in VARIANTS
    }

    interactions = []
    for repeat in range(a.repeats):
        rates = {name: variants[name]["runs"][repeat]["success_rate"] for name in VARIANTS}
        conv_old = rates["converter_only"] - rates["old_old"]
        conv_fixed = rates["combined"] - rates["controller_only"]
        did = conv_fixed - conv_old
        interactions.append({
            "repeat": repeat,
            "rates": rates,
            "converter_effect_old_controller": conv_old,
            "converter_effect_fixed_controller": conv_fixed,
            "difference_in_differences": did,
            "combined_ge_each_single": (
                rates["combined"] >= rates["controller_only"]
                and rates["combined"] >= rates["converter_only"]
            ),
            "combined_ge_baseline": rates["combined"] >= rates["old_old"],
        })

    exact = all(v["exactly_repeatable"] for v in variants.values())
    dids = [x["difference_in_differences"] for x in interactions]
    interaction_stable = len({round(x, 12) for x in dids}) == 1
    combined_beats_singletons = all(x["combined_ge_each_single"] for x in interactions)

    report = {
        "schema_version": 1,
        "protocol": {
            "repeats": a.repeats,
            "source_episode_count": a.count,
            "source_episode_ids": source_ids,
            "fresh_python_process_per_variant_repeat": True,
            "backend": "physx_cpu",
            "control_mode": "pd_ee_delta_pose",
            "use_first_env_state": True,
            "num_envs": 1,
        },
        "identities": identities,
        "variants": variants,
        "interactions": interactions,
        "repeatability_gate": {
            "all_four_cells_exact": exact,
            "interaction_did_exact": interaction_stable,
            "combined_ge_each_single_every_repeat": combined_beats_singletons,
            "pass": exact and interaction_stable and combined_beats_singletons,
        },
        "authorization_boundary": (
            "Repeatability qualifies the four-cell execution interaction measurement. "
            "It does not authorize either singleton or the combined repair; execution "
            "non-regression against old_old remains a separate gate."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

