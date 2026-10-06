#!/usr/bin/env bash
set -euo pipefail

REPEATS="${REPEATS:-5}"
COUNT="${COUNT:-10}"
ROOT="${ROOT:-$PWD/.validation-replay-determinism}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"

mkdir -p "$ROOT"
python -m pip install --upgrade pip
python -m pip install -e .
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

SRC="$ROOT/src-main"
rm -rf "$SRC"
git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$SRC" >/dev/null
git -C "$SRC" fetch origin "$BASE_SHA" >/dev/null
git -C "$SRC" checkout --detach "$BASE_SHA" >/dev/null
python -m pip install -e "$SRC" >/dev/null

prepare_demo() {
  local regime="$1"
  local rep="$2"
  local dir="$ROOT/${regime}-r${rep}"
  rm -rf "$dir"
  mkdir -p "$dir"
  cp "$RAW" "$dir/trajectory.h5"
  cp "$RAW_JSON" "$dir/trajectory.json"

  if [[ "$regime" == "enhanced" ]]; then
    python - "$dir/trajectory.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
env_kwargs = data["env_info"]["env_kwargs"]
env_kwargs["enhanced_determinism"] = True
sim = env_kwargs.setdefault("sim_config", {})
scene = sim.setdefault("scene_config", {})
scene["enable_enhanced_determinism"] = True
scene["cpu_workers"] = 0
path.write_text(json.dumps(data, indent=2) + "\n")
PY
  fi
  echo "$dir"
}

run_one() {
  local regime="$1"
  local rep="$2"
  local dir
  dir="$(prepare_demo "$regime" "$rep")"
  (
    cd "$SRC"
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    python -m mani_skill.trajectory.replay_trajectory \
      --traj-path "$dir/trajectory.h5" \
      --use-first-env-state \
      -c pd_ee_delta_pose -o state --save-traj \
      --count "$COUNT" --num-envs 1 -b physx_cpu
  )
}

for regime in default enhanced; do
  for rep in $(seq 0 $((REPEATS - 1))); do
    echo "=== regime=$regime replicate=$rep ==="
    run_one "$regime" "$rep"
  done
done

python validation/pr1495/summarize_replay_determinism_probe.py \
  --root "$ROOT" --repeats "$REPEATS" --expected "$COUNT" \
  --output "$ROOT/replay_determinism_probe.json"
