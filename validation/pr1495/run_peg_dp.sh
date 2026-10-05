#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VARIANT="${VARIANT:-}"
SEED="${SEED:-1}"
NUM_DEMOS="${NUM_DEMOS:-100}"
TOTAL_ITERS="${TOTAL_ITERS:-100000}"
WANDB_PROJECT="${WANDB_PROJECT:-maniskill-pr1495-peg-dp}"
WANDB_ENTITY="${WANDB_ENTITY:-}"
TRACK_MODE="${TRACK_MODE:-auto}"
WORK_ROOT="${WORK_ROOT:-$PWD/.validation-pr1495}"

case "$TRACK_MODE" in
  auto)
    if [[ -n "${WANDB_API_KEY:-}" ]]; then
      TRACK_MODE="wandb"
    else
      TRACK_MODE="tensorboard"
    fi
    ;;
  wandb|tensorboard)
    ;;
  *)
    echo "TRACK_MODE must be auto, wandb, or tensorboard" >&2
    exit 2
    ;;
esac

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
RAW_JSON="${RAW%.h5}.json"
if [[ ! -f "$RAW" || ! -f "$RAW_JSON" ]]; then
  echo "downloaded raw PegInsertionSide trajectory or metadata is missing" >&2
  exit 1
fi

# Never let baseline/fixed share a derived trajectory. replay_trajectory writes
# converted files beside its input, so a shared ~/.maniskill path can silently
# make the second variant reuse the first variant's conversion. Copy the same
# raw source into a variant-private directory, then regenerate unconditionally.
DEMO_ROOT="$WORK_ROOT/demos/$VARIANT-$TARGET_SHA"
mkdir -p "$DEMO_ROOT"
RAW_VARIANT="$DEMO_ROOT/trajectory.h5"
RAW_VARIANT_JSON="$DEMO_ROOT/trajectory.json"
cp "$RAW" "$RAW_VARIANT"
cp "$RAW_JSON" "$RAW_VARIANT_JSON"

DEMO="$DEMO_ROOT/trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
DEMO_JSON="${DEMO%.h5}.json"
rm -f "$DEMO" "$DEMO_JSON"

python -m mani_skill.trajectory.replay_trajectory \
  --traj-path "$RAW_VARIANT" \
  --use-first-env-state \
  -c pd_ee_delta_pose \
  -o state \
  --save-traj \
  --num-envs 10 \
  -b physx_cpu

if [[ ! -f "$DEMO" || ! -f "$DEMO_JSON" ]]; then
  echo "variant-private replay did not produce expected converted trajectory" >&2
  exit 1
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
from hashlib import sha256

def file_sha256(path):
    h = sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

with open("$RAW_VARIANT_JSON", "r", encoding="utf-8") as handle:
    raw_meta = json.load(handle)
with open("$DEMO_JSON", "r", encoding="utf-8") as handle:
    converted_meta = json.load(handle)

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
    "tracking_mode": "$TRACK_MODE",
    "wandb_project": "$WANDB_PROJECT" if "$TRACK_MODE" == "wandb" else None,
    "raw_demo_sha256": file_sha256("$RAW_VARIANT"),
    "converted_demo_sha256": file_sha256("$DEMO"),
    "raw_episode_count": len(raw_meta.get("episodes", [])),
    "converted_episode_count": len(converted_meta.get("episodes", [])),
    "demo_derivation": "variant-private-unconditional-replay",
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
)
if [[ "$TRACK_MODE" == "wandb" ]]; then
  CMD+=(--track --wandb-project-name "$WANDB_PROJECT")
  if [[ -n "$WANDB_ENTITY" ]]; then
    CMD+=(--wandb-entity "$WANDB_ENTITY")
  fi
fi

"${CMD[@]}"

cp -a "runs/$RUN_NAME" "$OUT/run"
python "$SCRIPT_DIR/summarize_tensorboard.py"   "$OUT/run"   --output "$OUT/summary.json"

echo "Evidence written to $OUT"
echo "----- manifest.json -----"
cat "$OUT/manifest.json"
echo "----- summary.json -----"
cat "$OUT/summary.json"
