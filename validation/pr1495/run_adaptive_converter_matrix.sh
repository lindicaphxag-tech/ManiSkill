#!/usr/bin/env bash
set -euo pipefail

COUNT="${COUNT:-10}"
ROOT="${ROOT:-$PWD/.validation-pr1495-adaptive}"
MAIN_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
ADAPTIVE_SHA="80bd0fb678fd9534830dac18418c777b7ed1a2a3"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"
HARNESS_ROOT="$PWD"

mkdir -p "$ROOT"
python -m pip install --upgrade pip
python -m pip install -e .
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

replay_variant() {
  local name="$1"
  local src="$2"
  local demo_root="$ROOT/demos-$name"
  rm -rf "$demo_root"
  mkdir -p "$demo_root"
  cp "$RAW" "$demo_root/trajectory.h5"
  cp "$RAW_JSON" "$demo_root/trajectory.json"
  python -m pip install -e "$src"
  (
    cd "$src"
    SRC_EXPECTED="$src" NAME_EXPECTED="$name" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual=Path(mani_skill.__file__).resolve()
expected=Path(os.environ["SRC_EXPECTED"]).resolve()
print("variant=",os.environ["NAME_EXPECTED"],"import=",actual)
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}")
PY
    python -m mani_skill.trajectory.replay_trajectory \
      --traj-path "$demo_root/trajectory.h5" \
      --use-first-env-state -c pd_ee_delta_pose -o state --save-traj \
      --count "$COUNT" --num-envs 2 -b physx_cpu
  )
}

MAIN_SRC="$ROOT/src-main"
git clone --filter=blob:none https://github.com/mani-skill/ManiSkill.git "$MAIN_SRC"
git -C "$MAIN_SRC" checkout --detach "$MAIN_SHA"
replay_variant main "$MAIN_SRC"

ADAPTIVE_SRC="$ROOT/src-adaptive"
git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$ADAPTIVE_SRC"
git -C "$ADAPTIVE_SRC" fetch origin "$ADAPTIVE_SHA"
git -C "$ADAPTIVE_SRC" checkout --detach "$ADAPTIVE_SHA"
python -m pip install -e "$ADAPTIVE_SRC"
(
  cd "$ADAPTIVE_SRC"
  python -m pytest -q tests/test_action_conversion.py
)
replay_variant adaptive_current "$ADAPTIVE_SRC"

ADAPTIVE_FIXED_SRC="$ROOT/src-adaptive-controller-fixed"
git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$ADAPTIVE_FIXED_SRC"
git -C "$ADAPTIVE_FIXED_SRC" fetch origin "$ADAPTIVE_SHA"
git -C "$ADAPTIVE_FIXED_SRC" checkout --detach "$ADAPTIVE_SHA"
git -C "$ADAPTIVE_FIXED_SRC" config user.email "validation@semrepair.local"
git -C "$ADAPTIVE_FIXED_SRC" config user.name "SemRepair validation"
git -C "$ADAPTIVE_FIXED_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git
git -C "$ADAPTIVE_FIXED_SRC" fetch controller "$CONTROLLER_SHA"
git -C "$ADAPTIVE_FIXED_SRC" cherry-pick "$CONTROLLER_SHA"
replay_variant adaptive_controller_fixed "$ADAPTIVE_FIXED_SRC"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_adaptive_converter.py \
  --root "$ROOT" --expected "$COUNT" \
  --output "$ROOT/adaptive_converter_matrix.json"
