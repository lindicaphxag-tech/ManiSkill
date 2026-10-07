"""Run the native ManiSkill regression on a Kaggle GPU and emit evidence."""

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


WORK = Path("/kaggle/working")
REPO = WORK / "ManiSkill"
GITHUB_REPO = "https://github.com/lindicaphxag-tech/ManiSkill.git"
BRANCH = "fix/delta-pose-euler-action"
COMMIT = "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0"
PR_URL = "https://github.com/mani-skill/ManiSkill/pull/1495"
HARNESS_NAME = "test_pr1495_native_assay.py"
HARNESS_BASE64 = "__NATIVE_TEST_HARNESS_B64__"
HARNESS_BYTES = base64.b64decode(HARNESS_BASE64)
started = time.time()
log = {
    "assay": "native-pickcube-multiaxis-delta-pose",
    "status": "running",
    "repository": GITHUB_REPO,
    "branch": BRANCH,
    "hardware": subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
        check=False,
        capture_output=True,
        text=True,
    ).stdout.strip(),
}


def run(command, **kwargs):
    print("$", " ".join(command), flush=True)
    subprocess.run(command, check=True, **kwargs)


try:
    if REPO.exists():
        raise RuntimeError(f"Refusing to overwrite existing checkout: {REPO}")
    run(["git", "clone", "--branch", BRANCH, GITHUB_REPO, str(REPO)])
    run(["git", "-C", str(REPO), "checkout", COMMIT])
    commit = subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != COMMIT:
        raise RuntimeError(f"Checked out {commit}, expected frozen commit {COMMIT}")
    log["commit"] = commit
    log["pull_request"] = PR_URL
    log["validation_harness_sha256"] = hashlib.sha256(HARNESS_BYTES).hexdigest()
    log["validation_harness"] = HARNESS_NAME
    # ManiSkill's Linux extra pins mplib==0.1.1, which has no Python 3.13
    # distribution. This PickCube controller path does not use motion planning.
    # Install the project without dependency resolution, then install every
    # declared runtime dependency except that unrelated motion-planning package.
    run([sys.executable, "-m", "pip", "install", "--no-deps", "-e", str(REPO)])
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "numpy>=1.22",
            "scipy",
            "dacite",
            "gymnasium>=0.29.1",
            "h5py",
            "pyyaml",
            "tqdm",
            "GitPython",
            "tabulate",
            "transforms3d",
            "trimesh",
            "imageio[ffmpeg]",
            "IPython",
            "pytorch_kinematics==0.7.6",
            "defusedxml",
            "nvidia-ml-py",
            "tyro>=0.8.5",
            "huggingface_hub",
            "sapien>=3.0.3",
            "pin",
            "pytest",
        ]
    )

    environment = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--all"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    environment_path = WORK / "resolved_environment.txt"
    environment_path.write_text(environment, encoding="utf-8")
    log["resolved_environment_sha256"] = hashlib.sha256(
        environment_path.read_bytes()
    ).hexdigest()

    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("Kaggle GPU was requested but torch.cuda.is_available() is false")
    os.environ["MANISKILL_RENDER_BACKEND"] = "gpu"
    os.environ["MANISKILL_ASSAY_RESULT"] = str(WORK / "assay_result.json")
    harness_path = REPO / "tests" / HARNESS_NAME
    harness_path.write_bytes(HARNESS_BYTES)
    os.chdir(REPO)
    run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-s",
            "tests/test_action_conversion.py",
            f"tests/{HARNESS_NAME}",
        ]
    )
    log["status"] = "passed"
    result_path = WORK / "assay_result.json"
    if result_path.exists():
        log["measurements"] = json.loads(result_path.read_text())
except Exception as error:
    log["status"] = "failed"
    log["error"] = f"{type(error).__name__}: {error}"
    raise
finally:
    log["elapsed_seconds"] = round(time.time() - started, 3)
    if REPO.exists():
        shutil.rmtree(REPO)
    log_path = WORK / "experiment_log.json"
    log_path.write_text(json.dumps(log, indent=2) + "\n")
    files = {}
    for name in (
        "assay_result.json",
        "experiment_log.json",
        "resolved_environment.txt",
    ):
        path = WORK / name
        if path.is_file():
            data = path.read_bytes()
            files[name] = {
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
    (WORK / "artifacts_manifest.json").write_text(
        json.dumps(
            {
                "files": files,
                "repository_commit": log.get("commit"),
                "status": log["status"],
            },
            indent=2,
        )
        + "\n"
    )
