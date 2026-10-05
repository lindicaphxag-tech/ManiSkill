#!/usr/bin/env bash
set -euo pipefail

VARIANT="${VARIANT:-}"
SEED="${SEED:-1}"
NUM_DEMOS="${NUM_DEMOS:-100}"
TOTAL_ITERS="${TOTAL_ITERS:-100000}"
WANDB_PROJECT="${WANDB_PROJECT:-maniskill-pr1495-peg-dp}"
WANDB_ENTITY="${WANDB_ENTITY:-}"
WORK_ROOT="${WORK_ROOT:-$PWD/.validation-pr1495}"

BASE_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
FIX_SHA="cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b"

case "$VARIANT" in
  baseline)
    REPO_URL="https://github.com/mani-skill/ManiSkill.git"
    TARGET_SHA="$BASE_SHA"
    ;;
  fixed)
    REPO_URL="https://github.com/lindicaphxag-tech/ManiSkill.git"
    TARGET_SHA="$FIX_SHA"
    ;;
  *)
    echo "VARIANT must be baseline or fixed" >&2
    exit 2
    ;;
esac

mkdir -p "$WORK_ROOT"
SRC="$WORK_ROOT/src-$VARIANT-$TARGET_SHA"
if [[ ! -d "$SRC/.git" ]]; then
  git clone --filter=blob:none "$REPO_URL" "$SRC"
fi
git -C "$SRC" fetch --all --tags
git -C "$SRC" checkout --detach "$TARGET_SHA"

python -m pip install --upgrade pip
python -m pip install -e "$SRC"
python -m pip install -e "$SRC/examples/baselines/diffusion_policy"

python -m mani_skill.utils.download_demo "PegInsertionSide-v1"

RAW="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning/trajectory.h5"
DEMO="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning/trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
if [[ ! -f "$DEMO" ]]; then
  python -m mani_skill.trajectory.replay_trajectory     --traj-path "$RAW"     --use-first-env-state     -c pd_ee_delta_pose     -o state     --save-traj     --num-envs 10     -b physx_cpu
fi

RUN_NAME="pr1495-${VARIANT}-PegInsertionSide-v1-state-${NUM_DEMOS}d-seed${SEED}"
OUT="$WORK_ROOT/evidence/$RUN_NAME"
mkdir -p "$OUT"

python - <<PY > "$OUT/manifest.json"
import json, os, platform, subprocess, sys
def cmd(*args):
    try:
        return subprocess.check_output(args, text=True).strip()
    except Exception:
        return None
print(json.dumps({
    "schema_version": 1,
    "variant": "$VARIANT",
    "target_sha": "$TARGET_SHA",
    "baseline_sha": "$BASE_SHA",
    "fix_sha": "$FIX_SHA",
    "seed": int("$SEED"),
    "num_demos": int("$NUM_DEMOS"),
    "total_iters": int("$TOTAL_ITERS"),
    "env_id": "PegInsertionSide-v1",
    "control_mode": "pd_ee_delta_pose",
    "sim_backend": "physx_cpu",
    "max_episode_steps": 300,
    "python": sys.version,
    "platform": platform.platform(),
    "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    "nvidia_smi": cmd("nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"),
}, indent=2))
PY

cd "$SRC/examples/baselines/diffusion_policy"

CMD=(
  python train.py
  --env-id PegInsertionSide-v1
  --demo-path "$DEMO"
  --control-mode pd_ee_delta_pose
  --sim-backend physx_cpu
  --num-demos "$NUM_DEMOS"
  --max_episode_steps 300
  --total_iters "$TOTAL_ITERS"
  --seed "$SEED"
  --exp-name "$RUN_NAME"
  --demo_type motionplanning
  --track
  --wandb-project-name "$WANDB_PROJECT"
)
if [[ -n "$WANDB_ENTITY" ]]; then
  CMD+=(--wandb-entity "$WANDB_ENTITY")
fi

"${CMD[@]}"

cp -a "runs/$RUN_NAME" "$OUT/run"
python "$OLDPWD/validation/pr1495/summarize_tensorboard.py"   "$OUT/run"   --output "$OUT/summary.json"

echo "Evidence written to $OUT"
