#!/usr/bin/env python3
"""Run the frozen ManiSkill #1472/#1495 PegInsertionSide 2x2 experiment.

This script is validation-only. It deliberately regenerates the converted
pd_ee_delta_pose dataset independently under each code variant so the converter
fix in #1495 is actually exercised.

It fails closed before official training if replayed episode counts differ.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

VARIANTS = {
    "A_old_old": "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3",
    "B_old_pr1472": "a231074ef562a9638e24c3f9a4d35bb70d4960d1",
    "C_pr1495_old": "cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b",
    "D_pr1495_pr1472": "24dcccba3d0aeae56b6fba1f5168e22cc340ab71",
}

PROFILES = {
    "smoke": {
        "num_demos": 10,
        "total_iters": 100,
        "eval_freq": 50,
        "num_eval_episodes": 10,
        "num_eval_envs": 2,
    },
    "pilot": {
        "num_demos": 100,
        "total_iters": 5000,
        "eval_freq": 1000,
        "num_eval_episodes": 20,
        "num_eval_envs": 5,
    },
    "official": {
        "num_demos": 100,
        "total_iters": 100000,
        "eval_freq": 5000,
        "num_eval_episodes": 100,
        "num_eval_envs": 10,
    },
}


def run(cmd, *, cwd: Path, env: dict[str, str], log: Path | None = None) -> None:
    print("+", " ".join(str(x) for x in cmd))
    if log is None:
        subprocess.run(cmd, cwd=cwd, env=env, check=True)
        return
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8", buffering=1) as fh:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
            fh.write(line)
        code = proc.wait()
    if code:
        raise subprocess.CalledProcessError(code, cmd)


def output(cmd, *, cwd: Path) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def companion_json(h5: Path) -> Path:
    return h5.with_suffix(".json")


def episode_count(path: Path) -> int:
    doc = json.loads(path.read_text(encoding="utf-8"))
    episodes = doc.get("episodes")
    if not isinstance(episodes, list):
        raise RuntimeError(f"{path}: missing episodes list")
    return len(episodes)


def env_for(worktree: Path) -> dict[str, str]:
    env = dict(os.environ)
    previous = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(worktree) + (os.pathsep + previous if previous else "")
    return env


def ensure_worktree(repo: Path, dest: Path, sha: str) -> None:
    if dest.exists():
        actual = output(["git", "rev-parse", "HEAD"], cwd=dest)
        if actual != sha:
            raise RuntimeError(f"{dest}: expected {sha}, found {actual}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "worktree", "add", "--detach", str(dest), sha], cwd=repo, env=os.environ.copy())
    actual = output(["git", "rev-parse", "HEAD"], cwd=dest)
    if actual != sha:
        raise RuntimeError(f"worktree identity mismatch: expected {sha}, got {actual}")


def prepare_demo_copy(raw_h5: Path, dest_dir: Path) -> Path:
    raw_json = companion_json(raw_h5)
    if not raw_h5.is_file() or not raw_json.is_file():
        raise FileNotFoundError(
            f"raw demo requires both {raw_h5} and {raw_json}"
        )
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_h5 = dest_dir / "trajectory.h5"
    dest_json = dest_dir / "trajectory.json"
    shutil.copy2(raw_h5, dest_h5)
    shutil.copy2(raw_json, dest_json)
    return dest_h5


def find_converted_demo(demo_dir: Path) -> Path:
    candidates = sorted(
        demo_dir.glob("trajectory.state.pd_ee_delta_pose*.h5"),
        key=lambda p: p.stat().st_mtime_ns,
        reverse=True,
    )
    if not candidates:
        raise RuntimeError(f"no converted pd_ee_delta_pose dataset under {demo_dir}")
    chosen = candidates[0]
    if not companion_json(chosen).is_file():
        raise RuntimeError(f"converted dataset missing companion JSON: {chosen}")
    return chosen


def runtime_manifest() -> dict:
    out = {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
    }
    try:
        import torch

        out["torch"] = torch.__version__
        out["cuda_available"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            out["cuda_device"] = torch.cuda.get_device_name(0)
            out["cuda_version"] = torch.version.cuda
    except Exception as exc:
        out["torch_probe_error"] = repr(exc)
    return out


def replay_variant(repo: Path, root: Path, name: str, sha: str, raw_h5: Path) -> dict:
    worktree = root / "code" / name
    ensure_worktree(repo, worktree, sha)
    demo_dir = root / "data" / name / "PegInsertionSide-v1" / "motionplanning"
    if demo_dir.exists():
        shutil.rmtree(demo_dir)
    variant_raw = prepare_demo_copy(raw_h5, demo_dir)

    env = env_for(worktree)
    log = root / "logs" / name / "replay.log"
    run(
        [
            sys.executable,
            "-m",
            "mani_skill.trajectory.replay_trajectory",
            "--traj-path",
            str(variant_raw),
            "--use-first-env-state",
            "-c",
            "pd_ee_delta_pose",
            "-o",
            "state",
            "--save-traj",
            "--num-envs",
            "10",
            "-b",
            "physx_cpu",
        ],
        cwd=worktree,
        env=env,
        log=log,
    )

    converted = find_converted_demo(demo_dir)
    meta = {
        "variant": name,
        "sha": sha,
        "raw_h5_sha256": sha256(variant_raw),
        "converted_h5": str(converted),
        "converted_h5_sha256": sha256(converted),
        "converted_json_sha256": sha256(companion_json(converted)),
        "episodes": episode_count(companion_json(converted)),
        "replay_log": str(log),
    }
    (root / "results").mkdir(parents=True, exist_ok=True)
    (root / "results" / f"{name}.replay.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return meta


def load_replay_results(root: Path) -> dict[str, dict]:
    results = {}
    for name in VARIANTS:
        path = root / "results" / f"{name}.replay.json"
        if not path.is_file():
            raise RuntimeError(f"missing replay result for {name}: {path}")
        results[name] = json.loads(path.read_text(encoding="utf-8"))
    return results


def assert_training_gate(results: dict[str, dict], profile: str) -> None:
    counts = {name: int(item["episodes"]) for name, item in results.items()}
    unique = set(counts.values())
    if len(unique) != 1:
        raise RuntimeError(
            "FAIL-CLOSED: converted episode counts differ across variants; "
            f"do not train incomparable datasets: {counts}"
        )
    required = int(PROFILES[profile]["num_demos"])
    available = next(iter(unique))
    if available < required:
        raise RuntimeError(
            f"FAIL-CLOSED: profile {profile!r} requires {required} demos, "
            f"but only {available} matched converted episodes are available"
        )


def train_variant(
    repo: Path,
    root: Path,
    name: str,
    sha: str,
    replay: dict,
    *,
    profile: str,
    seed: int,
    track: bool,
    wandb_project_name: str,
    wandb_entity: str | None,
) -> dict:
    cfg = PROFILES[profile]
    worktree = root / "code" / name
    ensure_worktree(repo, worktree, sha)
    baseline = worktree / "examples" / "baselines" / "diffusion_policy"
    dataset = Path(replay["converted_h5"]).resolve()
    run_name = f"semrepair-factorial-{profile}-{name}-seed{seed}"
    log = root / "logs" / name / f"{profile}-seed{seed}.train.log"

    start = time.time()
    train_cmd = [
            sys.executable,
            "train.py",
            "--env-id",
            "PegInsertionSide-v1",
            "--demo-path",
            str(dataset),
            "--control-mode",
            "pd_ee_delta_pose",
            "--sim-backend",
            "physx_cpu",
            "--num-demos",
            str(cfg["num_demos"]),
            "--max_episode_steps",
            "300",
            "--total_iters",
            str(cfg["total_iters"]),
            "--eval_freq",
            str(cfg["eval_freq"]),
            "--num_eval_episodes",
            str(cfg["num_eval_episodes"]),
            "--num_eval_envs",
            str(cfg["num_eval_envs"]),
            "--seed",
            str(seed),
            "--exp-name",
            run_name,
            "--demo_type",
            "motionplanning",
        ]
    if track:
        train_cmd.extend(
            [
                "--track",
                "--wandb_project_name",
                wandb_project_name,
            ]
        )
        if wandb_entity:
            train_cmd.extend(["--wandb_entity", wandb_entity])

    run(
        train_cmd,
        cwd=baseline,
        env=env_for(worktree),
        log=log,
    )
    result = {
        "variant": name,
        "sha": sha,
        "profile": profile,
        "seed": seed,
        "dataset_sha256": replay["converted_h5_sha256"],
        "episodes": replay["episodes"],
        "train_log": str(log),
        "run_dir": str(baseline / "runs" / run_name),
        "wall_seconds": time.time() - start,
        "wandb_tracking": bool(track),
        "wandb_project_name": wandb_project_name if track else None,
        "wandb_entity": wandb_entity if track else None,
    }
    out = root / "results" / f"{name}.{profile}.seed{seed}.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--work-root", type=Path, required=True)
    p.add_argument("--raw-demo", type=Path, required=True)
    p.add_argument("--phase", choices=("replay", "train", "all"), default="all")
    p.add_argument("--profile", choices=tuple(PROFILES), default="smoke")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument(
        "--track",
        action="store_true",
        help="Enable the official train.py Weights & Biases integration.",
    )
    p.add_argument(
        "--wandb-project-name",
        default="SemRepair-ManiSkill-Factorial",
    )
    p.add_argument("--wandb-entity", default=None)
    args = p.parse_args()

    repo = args.repo.resolve()
    root = args.work_root.resolve()
    raw_h5 = args.raw_demo.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "runtime": runtime_manifest(),
        "repo": str(repo),
        "raw_demo": str(raw_h5),
        "raw_demo_sha256": sha256(raw_h5),
        "profile": args.profile,
        "seed": args.seed,
        "variants": VARIANTS,
        "wandb_tracking": bool(args.track),
        "wandb_project_name": args.wandb_project_name if args.track else None,
        "wandb_entity": args.wandb_entity if args.track else None,
    }
    (root / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.phase in ("replay", "all"):
        replay = {
            name: replay_variant(repo, root, name, sha, raw_h5)
            for name, sha in VARIANTS.items()
        }
    else:
        replay = load_replay_results(root)

    assert_training_gate(replay, args.profile)

    if args.phase in ("train", "all"):
        for name, sha in VARIANTS.items():
            train_variant(
                repo,
                root,
                name,
                sha,
                replay[name],
                profile=args.profile,
                seed=args.seed,
                track=args.track,
                wandb_project_name=args.wandb_project_name,
                wandb_entity=args.wandb_entity,
            )

    print(
        json.dumps(
            {
                "status": "complete",
                "phase": args.phase,
                "profile": args.profile,
                "seed": args.seed,
                "episode_counts": {
                    name: replay[name]["episodes"] for name in VARIANTS
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
