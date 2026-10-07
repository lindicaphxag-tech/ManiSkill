"""Run a matched ManiSkill Diffusion Policy assay for ManiSkill PRs #1495/#1472.

The Kaggle kernel downloads the official public PegInsertionSide demonstrations,
then independently replays the raw trajectories under the frozen base and the
#1495/#1472 changed-file combination before training each arm. TensorBoard
scalars are exported as JSON/CSV; no dataset, checkpoint, video, or credential
is included.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request
from pathlib import Path

WORK = Path("/kaggle/working")
REPO = WORK / "ManiSkill"
OUTPUT = WORK / "assay_output"
DEMO_ROOT = WORK / "demos"
# The physics backend is CPU; policy optimization alone uses Kaggle's GPU.
os.environ["MANISKILL_RENDER_BACKEND"] = "cpu"
BASE = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERSION = "875ae4d8777678119b2f192ee186c6c15e6894d5"
CONTROLLER = "eed9be164797d41540421bda8adb3840377d7087"
UPSTREAM = "https://github.com/mani-skill/ManiSkill.git"
DEMO_NAME = "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
CONFIG = {
    "env_id": "PegInsertionSide-v1",
    "demo_type": "motionplanning",
    "control_mode": "pd_ee_delta_pose",
    "sim_backend": "physx_cpu",
    "num_demos": 100,
    "max_episode_steps": 300,
    "total_iters": 100000,
    "batch_size": 1024,
    "seed": 1,
    "eval_freq": 10000,
    "num_eval_episodes": 20,
    "num_eval_envs": 10,
    "capture_video": False,
    "wandb_tracking": False,
    "measurement_deviation": "evaluation is reduced from upstream defaults (100 episodes/5000 iterations) to 20 episodes/10000 iterations to fit paired Kaggle GPU execution; optimizer/training/demo configuration follows baselines.sh",
}

started = time.time()
OUTPUT.mkdir(parents=True, exist_ok=True)
run_record = {
    "assay": "maniskill-diffusion-policy-peg-insertion-delta-pose",
    "status": "running",
    "upstream_repository": UPSTREAM,
    "base_commit": BASE,
    "conversion_pr": {"number": 1495, "head": CONVERSION},
    "controller_pr": {"number": 1472, "head": CONTROLLER},
    "arms": ["upstream_baseline", "combined_pr1495_pr1472"],
    "config": CONFIG,
    "platform": platform.platform(),
    "python": sys.version,
}

def run_stream(command: list[str], log_path: Path, cwd: Path | None = None) -> None:
    print("$ " + " ".join(command), flush=True)
    with log_path.open("a", encoding="utf-8") as log:
        proc = subprocess.Popen(
            command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, env=os.environ.copy()
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="", flush=True)
            log.write(line)
        code = proc.wait()
        if code:
            raise subprocess.CalledProcessError(code, command)

def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()

def apply_controller_pr_overlay(commit: str) -> None:
    """Apply the two changed files from #1472's root-shaped PR commit."""
    if commit != CONTROLLER:
        raise RuntimeError("Controller overlay commit differs from the pinned #1472 head")
    controller_path = REPO / "mani_skill" / "agents" / "controllers" / "pd_ee_pose.py"
    source = controller_path.read_text(encoding="utf-8")
    old = "rot_action = rot_action * self.config.rot_lower"
    new = "rot_action = rot_action * self.config.rot_upper"
    if source.count(old) != 1:
        raise RuntimeError("#1472 controller patch context is missing or ambiguous")
    controller_path.write_text(source.replace(old, new), encoding="utf-8")

    test_path = REPO / "tests" / "test_pd_ee_pose_controller.py"
    test_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        "https://api.github.com/repos/mani-skill/ManiSkill/pulls/1472/files?per_page=100",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "ManiSkill-assay"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        changed_files = json.load(response)
    test_patch = next(
        (item for item in changed_files if item.get("filename") == "tests/test_pd_ee_pose_controller.py"),
        None,
    )
    if not test_patch or test_patch.get("status") != "added" or test_patch.get("additions") != 76:
        raise RuntimeError("Could not resolve the pinned #1472 controller regression test patch")
    patch_lines = test_patch.get("patch", "").splitlines()
    if any(line and not line.startswith(("+", "@@")) for line in patch_lines):
        raise RuntimeError("#1472 test patch is not a pure file addition")
    test_source = "\n".join(line[1:] for line in patch_lines if line.startswith("+")) + "\n"
    test_bytes = test_source.encode("utf-8")
    git_blob_sha = hashlib.sha1(b"blob " + str(len(test_bytes)).encode() + b"\0" + test_bytes).hexdigest()
    if git_blob_sha != "ce7e6e66cf3e286168d3d82f763307e18b587659":
        raise RuntimeError("#1472 test patch does not match the pinned Git blob")
    test_path.write_bytes(test_bytes)

def apply_kaggle_worker_compatibility() -> str:
    """Avoid CUDA state inherited by ManiSkill's forkserver evaluation workers."""
    env_path = REPO / "examples" / "baselines" / "diffusion_policy" / "diffusion_policy" / "make_env.py"
    source = env_path.read_text(encoding="utf-8")
    old = 'context="forkserver"'
    new = 'context="spawn"'
    if source.count(old) != 1:
        raise RuntimeError("Expected exactly one diffusion-policy forkserver context")
    env_path.write_text(source.replace(old, new), encoding="utf-8")
    return sha256(env_path)

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def export_scalars(run_name: str, tb_dir: Path) -> list[dict]:
    from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
    acc = EventAccumulator(str(tb_dir), size_guidance={"scalars": 0})
    acc.Reload()
    rows = []
    for tag in sorted(acc.Tags().get("scalars", [])):
        for ev in acc.Scalars(tag):
            rows.append({"arm": run_name, "tag": tag, "step": int(ev.step), "value": float(ev.value), "wall_time": float(ev.wall_time)})
    return rows

try:
    if REPO.exists():
        raise RuntimeError(f"Refusing to overwrite existing checkout: {REPO}")
    run_stream(["git", "clone", UPSTREAM, str(REPO)], OUTPUT / "setup.log")
    git("fetch", "origin", f"refs/pull/1495/head:refs/remotes/origin/pr-1495")
    git("fetch", "origin", f"refs/pull/1472/head:refs/remotes/origin/pr-1472")
    for commit in (BASE, CONVERSION, CONTROLLER):
        subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", f"{commit}^{{commit}}"], check=True)
    subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", BASE, CONVERSION], check=True)

    subprocess.run(["git", "-C", str(REPO), "checkout", "--detach", BASE], check=True)
    run_record["hardware"] = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
        check=False, capture_output=True, text=True
    ).stdout.strip()
    run_stream([sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(REPO)], OUTPUT / "install.log")
    runtime_requirements = ["numpy>=1.22", "scipy", "dacite", "gymnasium>=0.29.1", "h5py", "pyyaml", "tqdm", "GitPython", "tabulate", "transforms3d", "trimesh", "imageio[ffmpeg]", "IPython", "pytorch_kinematics==0.7.6", "defusedxml", "nvidia-ml-py", "tyro>=0.8.5", "huggingface_hub", "sapien>=3.0.3", "pin"]
    run_stream([sys.executable, "-m", "pip", "install", *runtime_requirements], OUTPUT / "install.log")
    dp_dir = REPO / "examples" / "baselines" / "diffusion_policy"
    run_stream([sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(dp_dir)], OUTPUT / "install.log")
    run_stream([sys.executable, "-m", "pip", "install", "diffusers", "tensorboard"], OUTPUT / "install.log")
    import torch
    run_record["torch"] = torch.__version__
    run_record["cuda_available"] = bool(torch.cuda.is_available())
    run_record["cuda_version"] = torch.version.cuda
    from importlib.metadata import PackageNotFoundError, version
    package_names = ["mani-skill", "diffusion_policy", "torch", "sapien", "diffusers", "tensorboard", "tyro", "numpy"]
    package_versions = {}
    for name in package_names:
        try:
            package_versions[name] = version(name)
        except PackageNotFoundError:
            package_versions[name] = None
    run_record["package_versions"] = package_versions
    if not torch.cuda.is_available():
        raise RuntimeError("Kaggle GPU was requested but CUDA is unavailable")

    run_stream([sys.executable, "-m", "mani_skill.utils.download_demo", "PegInsertionSide-v1", "--output_dir", str(DEMO_ROOT)], OUTPUT / "dataset.log")
    raw_demo_path = DEMO_ROOT / "PegInsertionSide-v1" / "motionplanning" / "trajectory.h5"
    if not raw_demo_path.is_file():
        raise FileNotFoundError(f"Official raw motion-planning demo missing: {raw_demo_path}")
    raw_meta_path = raw_demo_path.with_suffix(".json")
    if not raw_meta_path.is_file():
        raise FileNotFoundError(f"Official raw motion-planning metadata missing: {raw_meta_path}")
    inventory = [str(p.relative_to(DEMO_ROOT)) for p in DEMO_ROOT.rglob("*") if p.is_file()]
    (OUTPUT / "dataset_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")

    arms = [
        ("upstream_baseline", BASE, None),
        ("combined_pr1495_pr1472", CONVERSION, CONTROLLER),
    ]
    all_scalars: list[dict] = []
    run_summaries = []
    demonstrations = {}
    for arm, start_commit, extra_commit in arms:
        subprocess.run(["git", "-C", str(REPO), "reset", "--hard", BASE], check=True)
        subprocess.run(["git", "-C", str(REPO), "clean", "-fd"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(REPO), "checkout", "--detach", start_commit], check=True)
        if extra_commit:
            apply_controller_pr_overlay(extra_commit)
            subprocess.run([
                "git", "-C", str(REPO), "add",
                "mani_skill/agents/controllers/pd_ee_pose.py",
                "tests/test_pd_ee_pose_controller.py",
            ], check=True)
            subprocess.run(["git", "-C", str(REPO), "diff", "--cached", "--check"], check=True)
        subprocess.run(["git", "-C", str(REPO), "diff", "--check"], check=True)
        tree = git("write-tree")
        # Regenerate state/action demonstrations under each source tree. PR #1495
        # and #1472 change conversion/controller semantics, so sharing one replayed dataset would
        # confound the treatment with a dataset encoded under the other arm.
        arm_demo_dir = DEMO_ROOT / "converted" / arm / "PegInsertionSide-v1" / "motionplanning"
        arm_demo_dir.mkdir(parents=True, exist_ok=True)
        arm_raw_path = arm_demo_dir / "trajectory.h5"
        shutil.copy2(raw_demo_path, arm_raw_path)
        shutil.copy2(raw_meta_path, arm_raw_path.with_suffix(".json"))
        run_stream([
            sys.executable, "-m", "mani_skill.trajectory.replay_trajectory",
            "--traj-path", str(arm_raw_path), "--use-first-env-state",
            "-c", CONFIG["control_mode"], "-o", "state", "--save-traj",
            "--num-envs", "10", "-b", CONFIG["sim_backend"],
        ], OUTPUT / "dataset.log", cwd=REPO)
        demo_path = arm_demo_dir / DEMO_NAME
        meta_path = demo_path.with_suffix(".json")
        if not demo_path.is_file() or not meta_path.is_file():
            raise FileNotFoundError(f"Arm-specific replay output missing: {demo_path}")
        meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
        demonstrations[arm] = {
            "source": "haosulab/ManiSkill_Demonstrations PegInsertionSide-v1 official download",
            "replay_source_commit": start_commit,
            "filename": DEMO_NAME,
            "sha256": sha256(demo_path),
            "metadata_sha256": sha256(meta_path),
            "episode_count": len(meta_data.get("episodes", [])),
            "raw_data_exported": False,
        }
        runtime_compatibility_sha256 = apply_kaggle_worker_compatibility()
        run_name = f"dp_peg_insertion_{arm}_seed_{CONFIG['seed']}"
        cmd = [
            sys.executable, "train.py",
            "--env-id", CONFIG["env_id"],
            "--demo-path", str(demo_path),
            "--control-mode", CONFIG["control_mode"],
            "--sim-backend", CONFIG["sim_backend"],
            "--num-demos", str(CONFIG["num_demos"]),
            "--max_episode_steps", str(CONFIG["max_episode_steps"]),
            "--total_iters", str(CONFIG["total_iters"]),
            "--batch_size", str(CONFIG["batch_size"]),
            "--seed", str(CONFIG["seed"]),
            "--eval_freq", str(CONFIG["eval_freq"]),
            "--num_eval_episodes", str(CONFIG["num_eval_episodes"]),
            "--num_eval_envs", str(CONFIG["num_eval_envs"]),
            "--exp-name", run_name,
            "--demo_type", CONFIG["demo_type"],
            "--no-capture-video",
        ]
        run_log = OUTPUT / f"{arm}.log"
        run_stream(cmd, run_log, cwd=dp_dir)
        run_dir = dp_dir / "runs" / run_name
        rows = export_scalars(arm, run_dir)
        all_scalars.extend(rows)
        tags = sorted({r["tag"] for r in rows})
        by_tag = {}
        for tag in tags:
            seq = [r for r in rows if r["tag"] == tag]
            by_tag[tag] = {"points": len(seq), "first": seq[0]["value"], "last": seq[-1]["value"], "last_step": seq[-1]["step"]}
        events = list(run_dir.glob("events.out.tfevents.*"))
        saved_events = []
        event_dir = OUTPUT / "events" / arm
        event_dir.mkdir(parents=True, exist_ok=True)
        for event in events:
            dest = event_dir / event.name
            shutil.copy2(event, dest)
            saved_events.append(str(dest.relative_to(OUTPUT)))
        run_summaries.append({"arm": arm, "source_commit": start_commit, "controller_overlay_commit": extra_commit, "source_tree": tree, "runtime_compatibility_sha256": runtime_compatibility_sha256, "demo_sha256": demonstrations[arm]["sha256"], "run_name": run_name, "scalar_count": len(rows), "metrics": by_tag, "event_files": saved_events})
        # Retain TensorBoard evidence and compact log only; drop checkpoints/videos.
        shutil.rmtree(run_dir, ignore_errors=True)
        print(json.dumps(run_summaries[-1], sort_keys=True), flush=True)
        (OUTPUT / "run_summaries.json").write_text(json.dumps(run_summaries, indent=2) + "\n", encoding="utf-8")
        with (OUTPUT / "metrics.jsonl").open("w", encoding="utf-8") as f:
            for row in all_scalars:
                f.write(json.dumps(row, sort_keys=True) + "\n")
        if all_scalars:
            with (OUTPUT / "metrics.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(all_scalars[0]))
                writer.writeheader()
                writer.writerows(all_scalars)

    run_record["run_summaries"] = run_summaries
    run_record["demonstrations"] = demonstrations
    run_record["status"] = "passed"
except Exception as exc:
    run_record["status"] = "failed"
    run_record["error"] = f"{type(exc).__name__}: {exc}"
    run_record["traceback"] = traceback.format_exc()
    raise
finally:
    run_record["elapsed_seconds"] = round(time.time() - started, 3)
    run_record["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (OUTPUT / "experiment_log.json").write_text(json.dumps(run_record, indent=2) + "\n", encoding="utf-8")
    (OUTPUT / "artifacts_manifest.json").write_text(json.dumps({
        "experiment_log": "experiment_log.json",
        "run_summaries": "run_summaries.json",
        "metrics_jsonl": "metrics.jsonl",
        "metrics_csv": "metrics.csv",
        "event_files_directory": "events/",
        "raw_demos_exported": False,
        "model_checkpoints_exported": False,
        "videos_exported": False,
        "status": run_record["status"],
    }, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(REPO, ignore_errors=True)
    shutil.rmtree(DEMO_ROOT, ignore_errors=True)
