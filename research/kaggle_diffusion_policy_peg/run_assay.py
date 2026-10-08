"""Run a matched ManiSkill Diffusion Policy assay for ManiSkill PRs #1495/#1472.

The Kaggle kernel downloads the official public PegInsertionSide demonstrations,
then independently replays the raw trajectories under the frozen base and the
#1495/#1472 changed-file combination before training each arm. TensorBoard
scalars are exported as JSON/CSV; no dataset, checkpoint, video, or credential
is included.
"""
from __future__ import annotations

import csv
import copy
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
import zipfile
from pathlib import Path

SMOKE_MODE = os.environ.get("SEMREPAIR_DP_SMOKE", "0") == "1"
FACTORIAL_REPLAY_MODE = os.environ.get("SEMREPAIR_DP_FACTORIAL_REPLAY", "0") == "1"
if FACTORIAL_REPLAY_MODE and not SMOKE_MODE:
    raise RuntimeError("Factorial replay is a CPU smoke-only research mode")
WORK = (
    Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "semrepair_dp_smoke"
    if SMOKE_MODE
    else Path("/kaggle/working")
)
REPO = WORK / "ManiSkill"
OUTPUT = WORK / "assay_output"
DEMO_ROOT = WORK / "demos"
# State-based evaluation uses PhysX CPU.  The smoke mode disables rendering.
# For state-only CPU smoke, ManiSkill documents 'none' as disabling
# rendering; 'cpu' instead requests a SAPIEN render device named 'cpu'
# which can be unsupported even when Mesa Lavapipe exposes Vulkan.
os.environ["MANISKILL_RENDER_BACKEND"] = "none" if SMOKE_MODE else "cpu"
BASE = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERSION = (
    "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0"
    if SMOKE_MODE
    else "875ae4d8777678119b2f192ee186c6c15e6894d5"
)
CONTROLLER = "eed9be164797d41540421bda8adb3840377d7087"
UPSTREAM = "https://github.com/mani-skill/ManiSkill.git"
DEMO_DATASET_REVISION = "d674485bbffdd533914e52d272fdda34c0515608"
DEMO_ARCHIVE_RELATIVE_PATH = "demos/PegInsertionSide-v1.zip"
DEMO_ARCHIVE_SHA256 = "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c"
DEMO_ARCHIVE_URL = (
    "https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/resolve/"
    f"{DEMO_DATASET_REVISION}/{DEMO_ARCHIVE_RELATIVE_PATH}?download=true"
)
DEMO_ARCHIVE = WORK / "PegInsertionSide-v1.zip"
DEMO_NAME = "trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
CONFIG = {
    "env_id": "PegInsertionSide-v1",
    "demo_type": "motionplanning",
    "control_mode": "pd_ee_delta_pose",
    "sim_backend": "physx_cpu",
    "requested_num_demos": 100,
    "minimum_paired_demos": 32,
    "replay_count": 100,
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
if SMOKE_MODE:
    CONFIG.update(
        requested_num_demos=8,
        minimum_paired_demos=4,
        replay_count=8,
        max_episode_steps=20,
        total_iters=2,
        batch_size=32,
        eval_freq=1,
        num_eval_episodes=2,
        # Force official Gymnasium SyncVectorEnv (1 worker) for the CPU smoke:
        # the 2-worker AsyncVectorEnv path completed optimizer updates but the
        # parent process terminated with SIGSEGV at evaluator teardown.
        # This is a compatibility probe, not a performance-result change.
        num_eval_envs=1,
        measurement_deviation=(
            "CPU-only pipeline smoke: eight source demos, source-seed pairing, "
            "two optimizer updates, two SAME_STEP eval workers, no rendering. "
            "This is compatibility evidence only, not policy-performance evidence."
        ),
    )

if FACTORIAL_REPLAY_MODE:
    # A frozen 32-source-episode replication, independently replayed in every
    # cell; skip DP training altogether and preserve failure/zero cells.
    CONFIG.update(
        requested_num_demos=32,
        replay_count=32,
        minimum_paired_demos=16,
        measurement_deviation=(
            "32-episode CPU-only four-cell replay replication (no policy "
            "training); exact shared source seeds and complete negative "
            "outcomes are retained rather than filtered out."
        ),
    )

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
    if SMOKE_MODE:
        # Exact Git object fetched once by SHA, not the mutable public Files API.
        # Only the isolated smoke branch uses this archived, hash-checked copy.
        cached_test = Path(__file__).resolve().parent / "pinned" / "test_pd_ee_pose_controller.py"
        test_bytes = cached_test.read_bytes()
    else:
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

def apply_smoke_replay_renderer_override() -> str:
    """Disable renderer at the actual official replay gym.make boundary.

    MANISKILL_RENDER_BACKEND alone is insufficient: the trajectory replay path
    copies raw dataset env kwargs and passes them directly to gym.make. This
    isolated smoke adjustment prevents an unsupported SAPIEN "cpu" renderer
    device from being selected even when Vulkan Lavapipe is present.
    """
    if not SMOKE_MODE:
        raise RuntimeError("replay renderer override may only run in smoke mode")
    replay_path = REPO / "mani_skill" / "trajectory" / "replay_trajectory.py"
    source = replay_path.read_text(encoding="utf-8")
    expected = '    env_kwargs["num_envs"] = args.num_envs\n'
    if source.count(expected) != 1:
        raise RuntimeError("Official replay render-boundary anchor changed")
    override = (
        expected
        + '    env_kwargs["render_backend"] = "none"\n'
        + '    ori_env_kwargs["render_backend"] = "none"\n'
        + '    env_kwargs["render_mode"] = None\n'
        + '    # Isolated CPU smoke adjustment; no upstream production change.\n'
    )
    replay_path.write_text(source.replace(expected, override), encoding="utf-8")
    return sha256(replay_path)


def apply_kaggle_worker_compatibility() -> str:
    """Use spawn/SAME_STEP workers and normalize NumPy evaluation metrics.

    Smoke mode additionally disables the unused RGB render surface so the
    state-only PhysX-CPU path can execute on a renderer-less GitHub runner.
    """
    env_path = REPO / "examples" / "baselines" / "diffusion_policy" / "diffusion_policy" / "make_env.py"
    source = env_path.read_text(encoding="utf-8")
    old = 'context="forkserver"'
    new = 'context="spawn", autoreset_mode=gym.vector.AutoresetMode.SAME_STEP'
    if source.count(old) != 1:
        raise RuntimeError("Expected exactly one diffusion-policy forkserver context")
    env_path.write_text(source.replace(old, new), encoding="utf-8")

    eval_path = REPO / "examples" / "baselines" / "diffusion_policy" / "diffusion_policy" / "evaluate.py"
    eval_source = eval_path.read_text(encoding="utf-8")
    tensor_metric = "eval_metrics[k].append(v.float().cpu().numpy())"
    scalar_metric = "eval_metrics[k].append(v)\n"
    if eval_source.count(tensor_metric) != 1 or eval_source.count(scalar_metric) != 1:
        raise RuntimeError("Unexpected diffusion-policy evaluation metric conversion sites")
    eval_source = eval_source.replace(
        tensor_metric,
        "eval_metrics[k].append(torch.as_tensor(v).float().cpu().numpy())",
    )
    eval_source = eval_source.replace(
        scalar_metric,
        "eval_metrics[k].append(torch.as_tensor(v).float().cpu().numpy())\n",
    )
    if SMOKE_MODE:
        # Gymnasium SyncVectorEnv with one CPU worker may return metrics in
        # info["episode"] rather than the AsyncVectorEnv "final_info" slot.
        # Fail closed if that direct episode is missing or has no success metric.
        # The existing final_info path remains unchanged for non-smoke runs.
        sync_marker = '                if isinstance(info["final_info"], dict):'
        if eval_source.count(sync_marker) != 1:
            raise RuntimeError("Unexpected evaluation terminal-info branch")
        sync_handler = (
            '                if "final_info" not in info:\n'
            '                    if eval_envs.num_envs != 1 or "episode" not in info:\n'
            '                        raise RuntimeError("Missing terminal episode metrics")\n'
            '                    final_episode = info["episode"]\n'
            '                    if "success_at_end" not in final_episode:\n'
            '                        raise RuntimeError("Terminal episode lacks success_at_end")\n'
            '                    for k, v in final_episode.items():\n'
            '                        eval_metrics[k].append(torch.as_tensor(v).float().cpu().numpy())\n'
            '                elif isinstance(info["final_info"], dict):'
        )
        eval_source = eval_source.replace(sync_marker, sync_handler)
    eval_path.write_text(eval_source, encoding="utf-8")

    compatibility_paths = [env_path, eval_path]
    if SMOKE_MODE:
        train_path = REPO / "examples" / "baselines" / "diffusion_policy" / "train.py"
        train_source = train_path.read_text(encoding="utf-8")
        old_env_line = (
            '    env_kwargs = dict(control_mode=args.control_mode, reward_mode="sparse", '
            'obs_mode="state", render_mode="rgb_array", '
            'human_render_camera_configs=dict(shader_pack="default"))'
        )
        new_env_line = (
            '    env_kwargs = dict(control_mode=args.control_mode, reward_mode="sparse", '
            'obs_mode="state", render_mode=None, render_backend="none")'
        )
        if train_source.count(old_env_line) != 1:
            raise RuntimeError("Unexpected state-policy render configuration")
        train_source = train_source.replace(old_env_line, new_env_line)
        close_marker = "    envs.close()\n    writer.close()"
        if train_source.count(close_marker) != 1:
            raise RuntimeError("Unexpected DP environment/writer cleanup boundary")
        close_probe = (
            '    print("SMOKE_LIFECYCLE: before envs.close", flush=True)\n'
            '    envs.close()\n'
            '    print("SMOKE_LIFECYCLE: after envs.close", flush=True)\n'
            '    writer.close()\n'
            '    print("SMOKE_LIFECYCLE: after writer.close", flush=True)'
        )
        train_path.write_text(
            train_source.replace(close_marker, close_probe), encoding="utf-8"
        )
        compatibility_paths.append(train_path)

    compatibility_digests = ":".join(sha256(path) for path in compatibility_paths)
    return hashlib.sha256(compatibility_digests.encode("ascii")).hexdigest()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def index_converted_episodes(demo_path: Path) -> dict[int, dict]:
    """Index successful converted trajectories by their propagated source seed."""
    import h5py

    metadata = json.loads(demo_path.with_suffix(".json").read_text(encoding="utf-8"))
    result = {}
    with h5py.File(demo_path, "r") as h5_file:
        for episode in metadata.get("episodes", []):
            if episode.get("success") is not True:
                continue
            if "episode_seed" not in episode:
                raise RuntimeError(f"Converted episode is missing episode_seed: {episode}")
            seed = int(episode["episode_seed"])
            if seed in result:
                raise RuntimeError(f"Converted replay has duplicate episode seed {seed}")
            source_key = f"traj_{int(episode['episode_id'])}"
            if source_key not in h5_file:
                raise RuntimeError(f"Converted metadata points to missing HDF5 key {source_key}")
            result[seed] = {"source_key": source_key, "metadata": episode}
    if not result and not FACTORIAL_REPLAY_MODE:
        raise RuntimeError(f"No successful converted demonstrations found in {demo_path}")
    return result

def write_paired_dataset(demo_path: Path, indexed_episodes: dict[int, dict], seeds: list[int]) -> Path:
    """Copy the same source-seed subset into a compact, order-stable HDF5 dataset."""
    import h5py

    metadata = json.loads(demo_path.with_suffix(".json").read_text(encoding="utf-8"))
    metadata_by_seed = {
        int(item["episode_seed"]): item
        for item in metadata.get("episodes", [])
        if item.get("success") is True and "episode_seed" in item
    }
    paired_path = demo_path.with_name(demo_path.stem + ".paired.h5")
    paired_metadata = copy.deepcopy(metadata)
    paired_metadata["episodes"] = []
    with h5py.File(demo_path, "r") as source, h5py.File(paired_path, "w") as target:
        for new_id, seed in enumerate(seeds):
            item = indexed_episodes[seed]
            source.copy(item["source_key"], target, name=f"traj_{new_id}")
            episode = copy.deepcopy(metadata_by_seed[seed])
            episode["episode_id"] = new_id
            paired_metadata["episodes"].append(episode)
    paired_path.with_suffix(".json").write_text(
        json.dumps(paired_metadata, indent=2) + "\n", encoding="utf-8"
    )
    return paired_path

def download_pinned_demo_dataset() -> dict:
    """Download and verify the exact public demo archive used by the assay."""
    DEMO_ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DEMO_ARCHIVE_URL, timeout=120) as response:
        with DEMO_ARCHIVE.open("wb") as out:
            shutil.copyfileobj(response, out)
    actual_sha256 = sha256(DEMO_ARCHIVE)
    if actual_sha256 != DEMO_ARCHIVE_SHA256:
        raise RuntimeError(
            f"Demo archive SHA-256 mismatch: expected {DEMO_ARCHIVE_SHA256}, "
            f"got {actual_sha256}"
        )

    DEMO_ROOT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DEMO_ARCHIVE) as archive:
        root = DEMO_ROOT.resolve()
        for member in archive.infolist():
            target = (root / member.filename).resolve()
            if not target.is_relative_to(root):
                raise RuntimeError(f"Unsafe path in pinned demo archive: {member.filename}")
        archive.extractall(root)
    return {
        "repository": "haosulab/ManiSkill_Demonstrations",
        "revision": DEMO_DATASET_REVISION,
        "path": DEMO_ARCHIVE_RELATIVE_PATH,
        "sha256": actual_sha256,
        "size_bytes": DEMO_ARCHIVE.stat().st_size,
    }

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
    if shutil.which("nvidia-smi"):
        run_record["hardware"] = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            check=False, capture_output=True, text=True
        ).stdout.strip()
    else:
        run_record["hardware"] = "CPU-only GitHub smoke runner"
    # ManiSkill pins mplib==0.1.1 on Linux, which is unavailable for Python
    # 3.13. This policy assay consumes motion-planning demos but never imports
    # or invokes mplib; install runtime dependencies explicitly below.
    run_stream([sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(REPO)], OUTPUT / "install.log")
    runtime_requirements = ["numpy>=1.22", "scipy", "dacite", "gymnasium==1.2.0", "h5py", "pyyaml", "tqdm", "GitPython", "tabulate", "transforms3d", "trimesh", "imageio[ffmpeg]", "IPython", "pytorch_kinematics==0.7.6", "defusedxml", "nvidia-ml-py", "tyro>=0.8.5", "huggingface_hub", "sapien>=3.0.3", "pin"]
    run_stream([sys.executable, "-m", "pip", "install", *runtime_requirements], OUTPUT / "install.log")
    dp_dir = REPO / "examples" / "baselines" / "diffusion_policy"
    run_stream([sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(dp_dir)], OUTPUT / "install.log")
    run_stream([sys.executable, "-m", "pip", "install", "diffusers", "tensorboard"], OUTPUT / "install.log")
    import torch
    run_record["torch"] = torch.__version__
    run_record["cuda_available"] = bool(torch.cuda.is_available())
    run_record["cuda_version"] = torch.version.cuda
    from importlib.metadata import PackageNotFoundError, version
    package_names = ["mani-skill", "diffusion_policy", "torch", "sapien", "diffusers", "tensorboard", "tyro", "numpy", "gymnasium"]
    package_versions = {}
    for name in package_names:
        try:
            package_versions[name] = version(name)
        except PackageNotFoundError:
            package_versions[name] = None
    run_record["package_versions"] = package_versions
    if not SMOKE_MODE and not torch.cuda.is_available():
        raise RuntimeError("Kaggle GPU was requested but CUDA is unavailable")

    raw_dataset_record = download_pinned_demo_dataset()
    run_record["raw_dataset"] = raw_dataset_record
    (OUTPUT / "raw_dataset.json").write_text(
        json.dumps(raw_dataset_record, indent=2) + "\n", encoding="utf-8"
    )
    raw_demo_path = DEMO_ROOT / "PegInsertionSide-v1" / "motionplanning" / "trajectory.h5"
    if not raw_demo_path.is_file():
        raise FileNotFoundError(f"Official raw motion-planning demo missing: {raw_demo_path}")
    raw_meta_path = raw_demo_path.with_suffix(".json")
    if not raw_meta_path.is_file():
        raise FileNotFoundError(f"Official raw motion-planning metadata missing: {raw_meta_path}")
    raw_meta = json.loads(raw_meta_path.read_text(encoding="utf-8"))
    selected_episodes = raw_meta.get("episodes", [])[:CONFIG["replay_count"]]
    if len(selected_episodes) != CONFIG["replay_count"]:
        raise RuntimeError(
            f"Expected at least {CONFIG['replay_count']} raw demonstrations, "
            f"found {len(raw_meta.get('episodes', []))}"
        )
    unsuccessful_ids = [
        episode.get("episode_id") for episode in selected_episodes
        if not episode.get("success", False)
    ]
    if unsuccessful_ids:
        raise RuntimeError(
            f"The pinned replay prefix contains unsuccessful episodes: {unsuccessful_ids[:10]}"
        )
    raw_dataset_record["replay_selection"] = {
        "episode_ids": [episode["episode_id"] for episode in selected_episodes],
        "count": len(selected_episodes),
        "all_successful": True,
    }
    (OUTPUT / "raw_dataset.json").write_text(
        json.dumps(raw_dataset_record, indent=2) + "\n", encoding="utf-8"
    )
    inventory = [str(p.relative_to(DEMO_ROOT)) for p in DEMO_ROOT.rglob("*") if p.is_file()]
    (OUTPUT / "dataset_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")

    arms = (
        [
            ("upstream_baseline", BASE, None),
            ("converter_only_pr1495", CONVERSION, None),
            ("controller_only_pr1472", BASE, CONTROLLER),
            ("combined_pr1495_pr1472", CONVERSION, CONTROLLER),
        ]
        if FACTORIAL_REPLAY_MODE else [
            ("upstream_baseline", BASE, None),
            ("combined_pr1495_pr1472", CONVERSION, CONTROLLER),
        ]
    )
    run_record["arms"] = [arm for arm, _, _ in arms]
    run_record["factorial_replay_only"] = FACTORIAL_REPLAY_MODE
    all_scalars: list[dict] = []
    run_summaries = []
    demonstrations = {}
    prepared_arms = {}
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
        if SMOKE_MODE:
            override_digest = apply_smoke_replay_renderer_override()
            run_record.setdefault("smoke_replay_overrides", {})[arm] = {
                "official_replay_source_sha256": override_digest,
                "render_backend": "none",
                "render_mode": None,
                "scope": "isolated smoke runtime only",
            }

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
            "--num-envs", ("4" if SMOKE_MODE else "10"), "-b", CONFIG["sim_backend"],
            "--count", str(CONFIG["replay_count"]),
        ], OUTPUT / "dataset.log", cwd=REPO)
        demo_path = arm_demo_dir / DEMO_NAME
        meta_path = demo_path.with_suffix(".json")
        if demo_path.is_file() and meta_path.is_file():
            meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
            indexed_episodes = index_converted_episodes(demo_path)
            dataset_sha = sha256(demo_path)
            metadata_sha = sha256(meta_path)
        elif FACTORIAL_REPLAY_MODE and not demo_path.exists() and not meta_path.exists():
            # The official replay tool can save no dataset when a single-defect
            # controller produces zero successful trajectories. Preserve this
            # as a genuine non-trainable outcome, not as missing-at-random.
            meta_data = {"episodes": []}
            indexed_episodes = {}
            dataset_sha = None
            metadata_sha = None
        else:
            raise FileNotFoundError(f"Partially missing arm replay output: {demo_path}")
        demonstrations[arm] = {
            "source": "haosulab/ManiSkill_Demonstrations PegInsertionSide-v1 official download",
            "replay_source_commit": start_commit,
            "filename": DEMO_NAME,
            "sha256": dataset_sha,
            "metadata_sha256": metadata_sha,
            "episode_count": len(meta_data.get("episodes", [])),
            "successful_episode_count": len(indexed_episodes),
            "raw_data_exported": False,
        }
        prepared_arms[arm] = {
            "start_commit": start_commit,
            "extra_commit": extra_commit,
            "tree": tree,
            "demo_path": demo_path,
            "indexed_episodes": indexed_episodes,
        }

    if any("episode_seed" not in episode for episode in selected_episodes):
        raise RuntimeError("The pinned source metadata does not expose stable episode_seed values")
    source_seed_order = [int(episode["episode_seed"]) for episode in selected_episodes]
    if len(source_seed_order) != len(set(source_seed_order)):
        raise RuntimeError("The selected source demonstrations contain duplicate episode seeds")
    arm_success_seeds = {
        arm: [
            seed
            for seed in source_seed_order
            if seed in prepared_arms[arm]["indexed_episodes"]
        ]
        for arm, _, _ in arms
    }
    common_seeds = [
        seed for seed in source_seed_order
        if all(seed in prepared_arms[arm]["indexed_episodes"] for arm, _, _ in arms)
    ]
    if FACTORIAL_REPLAY_MODE:
        # The 2x2 cell success pattern itself is the measured evidence.
        # No recovered demo from another cell is reused for a failed cell.
        # A zero four-way overlap is a valid non-trainable factorial outcome.
        cell_matrix = [
            {
                "source_seed": seed,
                **{
                    arm: bool(seed in prepared_arms[arm]["indexed_episodes"])
                    for arm, _, _ in arms
                }
            }
            for seed in source_seed_order
        ]
        pairwise = {
            f"{left}|{right}": {
                "intersection_count": sum(
                    seed in prepared_arms[left]["indexed_episodes"]
                    and seed in prepared_arms[right]["indexed_episodes"]
                    for seed in source_seed_order
                ),
                "source_seed_sha256": hashlib.sha256(
                    json.dumps(
                        [seed for seed in source_seed_order
                         if seed in prepared_arms[left]["indexed_episodes"]
                         and seed in prepared_arms[right]["indexed_episodes"]],
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest(),
            }
            for i, (left, _, _) in enumerate(arms)
            for right, _, _ in arms[i + 1:]
        }
        factorial = {
            "schema_version": 1,
            "status": "factorial_replay_completed_not_policy_training",
            "source_dataset_revision": DEMO_DATASET_REVISION,
            "source_dataset_sha256": DEMO_ARCHIVE_SHA256,
            "baseline_code_sha": BASE,
            "converter_code_sha": CONVERSION,
            "controller_code_sha": CONTROLLER,
            "sample_size": len(source_seed_order),
            "source_seed_matrix": cell_matrix,
            "per_arm_success_count": {
                arm: len(prepared_arms[arm]["indexed_episodes"])
                for arm, _, _ in arms
            },
            "pairwise": pairwise,
            "four_way_intersection_count": len(common_seeds),
            "four_way_intersection_source_seed_sha256": hashlib.sha256(
                json.dumps(common_seeds, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "trainable_four_way_factorial": (
                len(common_seeds) >= CONFIG["minimum_paired_demos"]
            ),
            "authorities": "converter and controller are independent 2x2 factors",
            "claim_boundary": (
                "This reports official demonstration replay success only, "
                "not learned-policy success, physical task reward superiority, "
                "or an independent maintainer adoption."
            ),
        }
        (OUTPUT / "factorial_replay.json").write_text(
            json.dumps(factorial, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        run_record["factorial_replay"] = factorial
        run_record["demonstrations"] = demonstrations
        run_record["status"] = "passed"
        print(json.dumps({
            "factorial_success": factorial["per_arm_success_count"],
            "four_way_intersection_count": len(common_seeds),
            "note": factorial["claim_boundary"]
        }, sort_keys=True), flush=True)
        raise SystemExit(0)
    if len(common_seeds) < CONFIG["minimum_paired_demos"]:
        raise RuntimeError(
            f"Only {len(common_seeds)} source-seed-matched successful demos survived both replays; "
            f"minimum is {CONFIG['minimum_paired_demos']}"
        )
    common_seed_sha256 = hashlib.sha256(
        json.dumps(common_seeds, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    seed_evidence = {
        "schema_version": 1,
        "source_dataset": {
            key: raw_dataset_record[key]
            for key in ("repository", "revision", "path", "sha256", "size_bytes")
        },
        "requested_episode_seeds": source_seed_order,
        "requested_episode_seeds_sha256": hashlib.sha256(
            json.dumps(source_seed_order, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "arms": {
            arm: {
                "successful_episode_seeds": seeds,
                "successful_count": len(seeds),
                "successful_episode_seeds_sha256": hashlib.sha256(
                    json.dumps(seeds, separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
            }
            for arm, seeds in arm_success_seeds.items()
        },
        "paired_episode_seeds": common_seeds,
        "paired_count": len(common_seeds),
        "paired_episode_seeds_sha256": common_seed_sha256,
        "raw_demos_exported": False,
        "converted_trajectories_exported": False,
    }
    (OUTPUT / "pairing_evidence.json").write_text(
        json.dumps(seed_evidence, indent=2) + "\n", encoding="utf-8"
    )
    CONFIG["effective_paired_num_demos"] = len(common_seeds)
    CONFIG["paired_source_seed_sha256"] = common_seed_sha256
    for arm, _, _ in arms:
        paired_path = write_paired_dataset(
            prepared_arms[arm]["demo_path"],
            prepared_arms[arm]["indexed_episodes"],
            common_seeds,
        )
        prepared_arms[arm]["paired_demo_path"] = paired_path
        demonstrations[arm]["paired_filename"] = paired_path.name
        demonstrations[arm]["paired_sha256"] = sha256(paired_path)
        demonstrations[arm]["paired_metadata_sha256"] = sha256(paired_path.with_suffix(".json"))
        demonstrations[arm]["paired_episode_count"] = len(common_seeds)
        demonstrations[arm]["paired_source_seed_sha256"] = common_seed_sha256

    run_record["demonstrations"] = demonstrations
    run_record["pairing"] = {
        "requested_source_episodes": len(selected_episodes),
        "requested_episode_seeds_sha256": seed_evidence[
            "requested_episode_seeds_sha256"
        ],
        "successful_converted_episodes": {
            arm: demonstrations[arm]["successful_episode_count"] for arm, _, _ in arms
        },
        "successful_episode_seeds_sha256": {
            arm: evidence["successful_episode_seeds_sha256"]
            for arm, evidence in seed_evidence["arms"].items()
        },
        "paired_episode_count": len(common_seeds),
        "paired_source_seed_sha256": common_seed_sha256,
        "pairing_evidence_file": "pairing_evidence.json",
    }

    # Both arms now train on the same successful source-seed set. The two
    # HDF5 files remain arm-specific because their action/state conversions differ.
    for arm, _, _ in arms:
        start_commit = prepared_arms[arm]["start_commit"]
        extra_commit = prepared_arms[arm]["extra_commit"]
        demo_path = prepared_arms[arm]["paired_demo_path"]
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
        subprocess.run(["git", "-C", str(REPO), "diff", "--check"], check=True)
        tree = git("write-tree")
        runtime_compatibility_sha256 = apply_kaggle_worker_compatibility()
        run_name = f"dp_peg_insertion_{arm}_seed_{CONFIG['seed']}"
        cmd = [
            sys.executable, "train.py",
            "--env-id", CONFIG["env_id"],
            "--demo-path", str(demo_path),
            "--control-mode", CONFIG["control_mode"],
            "--sim-backend", CONFIG["sim_backend"],
            "--num-demos", str(len(common_seeds)),
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
        run_summaries.append({"arm": arm, "source_commit": start_commit, "controller_overlay_commit": extra_commit, "source_tree": tree, "runtime_compatibility_sha256": runtime_compatibility_sha256, "demo_sha256": demonstrations[arm]["paired_sha256"], "paired_num_demos": len(common_seeds), "paired_source_seed_sha256": common_seed_sha256, "run_name": run_name, "scalar_count": len(rows), "metrics": by_tag, "event_files": saved_events})
        run_record["run_summaries"] = run_summaries
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
        "run_summaries": (
            "run_summaries.json" if (OUTPUT / "run_summaries.json").exists() else None
        ),
        "factorial_replay": (
            "factorial_replay.json" if (OUTPUT / "factorial_replay.json").exists() else None
        ),
        "metrics_jsonl": "metrics.jsonl",
        "metrics_csv": "metrics.csv",
        "event_files_directory": "events/",
        "pairing_evidence": (
            "pairing_evidence.json"
            if (OUTPUT / "pairing_evidence.json").is_file()
            else None
        ),
        "raw_demos_exported": False,
        "model_checkpoints_exported": False,
        "videos_exported": False,
        "status": run_record["status"],
    }, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(REPO, ignore_errors=True)
    shutil.rmtree(DEMO_ROOT, ignore_errors=True)
    DEMO_ARCHIVE.unlink(missing_ok=True)
