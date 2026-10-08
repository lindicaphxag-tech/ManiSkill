"""Run the full 2x2 ManiSkill Diffusion Policy causal attribution assay.

Four source-frozen arms independently replay the official PegInsertionSide
source demos before optimizer updates. This executable design differs from
the historical *two-arm combined-change* comparison, which cannot isolate
either PR. Every arm uses the ordered intersection of successful original
episode seeds across all FOUR source trees; no source-converted HDF5 is reused
across different intervention cells.

This script does not itself provide any completed training results or
statistical certainty. Four GPU trainings are expensive and must be
explicitly submitted and externally audited.

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

WORK = Path("/kaggle/working")
REPO = WORK / "ManiSkill"
OUTPUT = WORK / "assay_output_factorial"
DEMO_ROOT = WORK / "demos"
# The physics backend is CPU; policy optimization alone uses Kaggle's GPU.
os.environ["MANISKILL_RENDER_BACKEND"] = "cpu"
BASE = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERSION = "875ae4d8777678119b2f192ee186c6c15e6894d5"
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
    "measurement_deviation": "FROZEN four-arm factorial attribution experiment. Four independent source-tree replays and four seed-matched Diffusion Policy trainings. Eval uses 20 episodes/10000 iterations rather than 100 episodes/5000 for limited GPU; original total optimizer iterations/demos otherwise retained.",
    "experimental_design": "converter_x_controller_2x2_factorial",
    "causal_attribution_limit": "one optimizer seed; additive contrasts are descriptive, not significant",
}

started = time.time()
OUTPUT.mkdir(parents=True, exist_ok=True)
run_record = {
    "assay": "maniskill-diffusion-policy-peg-insertion-2x2-factorial-v1",
    "status": "running",
    "upstream_repository": UPSTREAM,
    "base_commit": BASE,
    "conversion_pr": {"number": 1495, "head": CONVERSION},
    "controller_pr": {"number": 1472, "head": CONTROLLER},
    "arms": [
        "upstream_baseline", "converter_pr1495_only",
        "controller_pr1472_only", "combined_pr1495_pr1472",
    ],
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
    """Use spawn/SAME_STEP workers and normalize NumPy evaluation metrics."""
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
    eval_path.write_text(eval_source, encoding="utf-8")
    compatibility_digests = f"{sha256(env_path)}:{sha256(eval_path)}"
    return hashlib.sha256(compatibility_digests.encode("ascii")).hexdigest()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def index_converted_episodes(demo_path: Path) -> dict[int, dict]:
    """Cross-check metadata success against the *saved native HDF5 terminal success*.

    ManiSkill replay_trajectory --allow-failure saves successful AND failed
    trajectories; its saved count is not a count of task successes. The
    upstream RecordEpisode wrapper writes the stepwise success dataset and
    copies the last entry into the JSON metadata. Both must agree, and
    every listed episode must actually exist in HDF5, BEFORE a treatment is
    counted as completed or any successful training subset is selected.
    """
    import h5py

    metadata = json.loads(demo_path.with_suffix(".json").read_text(encoding="utf-8"))
    episodes = metadata.get("episodes")
    if not isinstance(episodes, list):
        raise RuntimeError("converted replay metadata has no episode list")
    result = {}
    seen_seeds: set[int] = set()
    seen_trajectory_keys: set[str] = set()
    with h5py.File(demo_path, "r") as h5_file:
        for episode in episodes:
            if (
                not isinstance(episode, dict)
                or type(episode.get("episode_seed")) is not int
                or type(episode.get("episode_id")) is not int
                or type(episode.get("success")) is not bool
            ):
                raise RuntimeError("converted replay has missing source seed/id/success")
            seed = episode["episode_seed"]
            if seed in seen_seeds:
                raise RuntimeError(f"duplicate converted episode seed {seed}")
            seen_seeds.add(seed)
            source_key = f"traj_{episode['episode_id']}"
            if source_key in seen_trajectory_keys:
                raise RuntimeError(f"duplicate converted episode ID {source_key}")
            seen_trajectory_keys.add(source_key)
            if source_key not in h5_file:
                raise RuntimeError(
                    f"converted metadata refers to missing HDF5 {source_key}"
                )
            trajectory = h5_file[source_key]
            if "success" not in trajectory or "actions" not in trajectory:
                raise RuntimeError(
                    f"{source_key} missing native per-step success/actions"
                )
            success_steps = trajectory["success"]
            actions = trajectory["actions"]
            if (
                not isinstance(success_steps, h5py.Dataset)
                or success_steps.dtype.kind != "b"
                or not isinstance(actions, h5py.Dataset)
                or success_steps.ndim != 1
                or actions.ndim < 1
                or len(success_steps) == 0
                or len(actions) != len(success_steps)
                or type(episode.get("elapsed_steps")) is not int
                or episode["elapsed_steps"] != len(success_steps)
            ):
                raise RuntimeError(
                    f"{source_key} has corrupt/misaligned native outcome timeline"
                )
            terminal_success = bool(success_steps[-1])
            if terminal_success != episode["success"]:
                raise RuntimeError(
                    f"{source_key} JSON success conflicts with HDF5 terminal outcome"
                )
            if terminal_success:
                result[seed] = {
                    "source_key": source_key,
                    "metadata": episode,
                    "native_terminal_success": True,
                }
    # Zero successful conversions is a measured 0/N only if all metadata
    # rows and their native HDF5 trajectories passed the above checks.
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
    run_record["hardware"] = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
        check=False, capture_output=True, text=True
    ).stdout.strip()
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
    if not torch.cuda.is_available():
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

    # Exactly four independent converter/controller treatment cells.
    # The converter-only arm is the existing #1495 PR on the legacy
    # controller; controller-only is the frozen base with #1472 overlay.
    # Treatment assignment is SOURCE-FROZEN before the first replay.
    arms = [
        ("upstream_baseline", BASE, None),
        ("converter_pr1495_only", CONVERSION, None),
        ("controller_pr1472_only", BASE, CONTROLLER),
        ("combined_pr1495_pr1472", CONVERSION, CONTROLLER),
    ]
    if (
        len({name for name, _, _ in arms}) != 4
        or len({(base, overlay) for _, base, overlay in arms}) != 4
        or {(base, overlay) for _, base, overlay in arms}
        != {(BASE, None), (CONVERSION, None), (BASE, CONTROLLER), (CONVERSION, CONTROLLER)}
    ):
        raise RuntimeError("frozen 2x2 source intervention cells are not unique")
    # Immutable, pre-intervention population manifest. Written before
    # executing any converter/controller replay so aborted experiments cannot
    # silently redefine which source episodes were attempted.
    if any("episode_seed" not in ep for ep in selected_episodes):
        raise RuntimeError("Pinned source selection contains an unidentifiable seed")
    source_seed_order = [int(ep["episode_seed"]) for ep in selected_episodes]
    if len(set(source_seed_order)) != len(source_seed_order):
        raise RuntimeError("Precommitted source population has duplicate episode seeds")
    original_population = {
        "schema": "maniskill-source-population-precommit-v1",
        "source_dataset": {
            key: raw_dataset_record[key]
            for key in ("repository", "revision", "path", "sha256", "size_bytes")
        },
        "source_episodes": [
            {"episode_id": int(ep["episode_id"]), "episode_seed": int(ep["episode_seed"])}
            for ep in selected_episodes
        ],
        "source_episode_seeds_sha256": hashlib.sha256(
            json.dumps(source_seed_order, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "four_frozen_interventions": [
            {"arm": arm, "source_commit": head,
             "controller_overlay_commit": overlay}
            for arm, head, overlay in arms
        ],
        "note": "Pre-treatment source population; no converted replay outcomes yet",
    }
    (OUTPUT / "source_population_precommit.json").write_text(
        json.dumps(original_population, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    # Individual intervention outcome files are durable before any common-
    # survivor intersection. A replay crash is UNKNOWN, never counted as
    # success nor coerced to a measured failure.
    (OUTPUT / "per_arm_replay").mkdir(parents=True, exist_ok=True)
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
            "--count", str(CONFIG["replay_count"]),
            # Native ManiSkill flag: persist failed converted trajectories
            # too. Do NOT conflate the replay CLI's saved count with success.
            "--allow-failure",
        ], OUTPUT / f"replay_{arm}.log", cwd=REPO)
        demo_path = arm_demo_dir / DEMO_NAME
        meta_path = demo_path.with_suffix(".json")
        if not demo_path.is_file() or not meta_path.is_file():
            raise FileNotFoundError(f"Arm-specific replay output missing: {demo_path}")
        meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
        # This protocol requests all source episodes, INCLUDING failure
        # trajectories. A missing or duplicate row is UNKNOWN, not a
        # measured zero. Fail before advertising population-level effects.
        replay_rows = meta_data.get("episodes", [])
        replay_seeds = []
        for row in replay_rows:
            if (
                "episode_seed" not in row
                or type(row["episode_seed"]) is not int
                or type(row.get("success")) is not bool
            ):
                raise RuntimeError(
                    f"{arm}: incomplete replay metadata or missing binary success label"
                )
            replay_seeds.append(row["episode_seed"])
        if (
            len(replay_seeds) != len(source_seed_order)
            or len(set(replay_seeds)) != len(replay_seeds)
            or set(replay_seeds) != set(source_seed_order)
        ):
            raise RuntimeError(
                f"{arm}: allow-failure replay omitted or duplicated a precommitted source episode"
            )
        indexed_episodes = index_converted_episodes(demo_path)
        demonstrations[arm] = {
            "source": "haosulab/ManiSkill_Demonstrations PegInsertionSide-v1 official download",
            "replay_source_commit": start_commit,
            "filename": DEMO_NAME,
            "sha256": sha256(demo_path),
            "metadata_sha256": sha256(meta_path),
            "episode_count": len(meta_data.get("episodes", [])),
            "successful_episode_count": len(indexed_episodes),
            "failed_episode_count": len(source_seed_order) - len(indexed_episodes),
            "full_original_source_population_returned": True,
            "raw_data_exported": False,
        }
        prepared_arms[arm] = {
            "start_commit": start_commit,
            "extra_commit": extra_commit,
            "tree": tree,
            "demo_path": demo_path,
            "indexed_episodes": indexed_episodes,
        }
        # Persist all observed 0/1 replay results immediately after each
        # completed treatment, including 0 successes. On an interrupted
        # treatment no file is produced and the outcome remains UNKNOWN.
        extra = set(indexed_episodes) - set(source_seed_order)
        if extra:
            raise RuntimeError(
                f"Treatment {arm} returned seeds outside the precommitted source population: {sorted(extra)[:5]}"
            )
        completed_seeds = [seed for seed in source_seed_order if seed in indexed_episodes]
        (OUTPUT / "per_arm_replay" / f"{arm}.json").write_text(
            json.dumps({
                "schema": "maniskill-completed-arm-replay-v1",
                "arm": arm, "source_commit": start_commit,
                "controller_overlay_commit": extra_commit,
                "production_tree": tree,
                # These point to the REAL upstream replay output artifacts
                # that were checked at every terminal success/failure step.
                # The author-controlled digests help a third party reproduce
                # source-level differences from the frozen public demos;
                # they are not external attestation of how the run executed.
                "converted_hdf5_sha256": sha256(demo_path),
                "converted_metadata_sha256": sha256(meta_path),
                "native_outcome_verifier": "RecordEpisode HDF5 terminal success matches JSON",
                "source_population_sha256": original_population["source_episode_seeds_sha256"],
                "successful_episode_seeds": completed_seeds,
                "successful_count": len(completed_seeds),
                "failed_count": len(source_seed_order) - len(completed_seeds),
                "full_source_census": True,
                "replay_status": "completed",
                "log_file": f"replay_{arm}.log",
            }, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

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
    # PRE-SELECTION FINITE-SOURCE REPLAY OUTCOMES. Save the intention-to-replay
    # population and all 4 arms BEFORE intersecting successful trajectories.
    # The record survives missing common training demos or a later GPU crash.
    replay_itt_record = {
        "schema": "maniskill-source-episode-itt-v1",
        "interpretation": "descriptive source-seed paired replay only; not training",
        "source_dataset": {
            key: raw_dataset_record[key]
            for key in ("repository", "revision", "path", "sha256", "size_bytes")
        },
        "original_source_episodes": [
            {"episode_id": int(item["episode_id"]), "episode_seed": int(item["episode_seed"])}
            for item in selected_episodes
        ],
        "original_source_seed_sha256": hashlib.sha256(
            json.dumps(source_seed_order, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "arms": [
            {
                "arm": arm,
                "source_commit": checkout_sha,
                "controller_overlay_commit": overlay_sha,
                "successful_episode_seeds": arm_success_seeds[arm],
                "successful_seed_sha256": hashlib.sha256(
                    json.dumps(arm_success_seeds[arm], separators=(",", ":")).encode("utf-8")
                ).hexdigest(),
            }
            for arm, checkout_sha, overlay_sha in arms
        ],
    }
    (OUTPUT / "replay_intention_to_treat.json").write_text(
        json.dumps(replay_itt_record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    run_record["replay_itt_file"] = "replay_intention_to_treat.json"

    common_seeds = [
        seed for seed in source_seed_order
        if all(seed in prepared_arms[arm]["indexed_episodes"] for arm, _, _ in arms)
    ]
    if len(common_seeds) < CONFIG["minimum_paired_demos"]:
        raise RuntimeError(
            f"Only {len(common_seeds)} source-seed-matched successful demos survived all four replays; "
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

    # All four arms now train on the same successful source-seed set.
    # The four HDF5 files remain arm-specific: no action/state conversion
    # produced under a different source tree is ever reused.
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
    run_record["interpretation"] = (
        "Source-seed matched 2x2 design completed for one policy seed only. "
        "No causal or significance claim before independent metric audit."
    )
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
        "pairing_evidence": (
            "pairing_evidence.json"
            if (OUTPUT / "pairing_evidence.json").is_file()
            else None
        ),
        "replay_intention_to_treat": (
            "replay_intention_to_treat.json"
            if (OUTPUT / "replay_intention_to_treat.json").is_file()
            else None
        ),
        "source_population_precommit": (
            "source_population_precommit.json"
            if (OUTPUT / "source_population_precommit.json").is_file()
            else None
        ),
        "per_arm_replay_results": [
            str(path.relative_to(OUTPUT))
            for path in sorted((OUTPUT / "per_arm_replay").glob("*.json"))
        ] if (OUTPUT / "per_arm_replay").is_dir() else [],
        "raw_demos_exported": False,
        "model_checkpoints_exported": False,
        "videos_exported": False,
        "status": run_record["status"],
    }, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(REPO, ignore_errors=True)
    shutil.rmtree(DEMO_ROOT, ignore_errors=True)
    DEMO_ARCHIVE.unlink(missing_ok=True)
