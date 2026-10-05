#!/usr/bin/env bash
set -euo pipefail

COUNT="${COUNT:-10}"
ROOT="${ROOT:-$PWD/.validation-pr1495-compensating}"
MAIN_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERTER_SHA="f96569f19688e4cee9415c491929541f0ebd1207"
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

prepare_repo() {
  local name="$1"
  local base_sha="$2"
  local src="$ROOT/src-$name"
  rm -rf "$src"
  git clone --filter=blob:none https://github.com/mani-skill/ManiSkill.git "$src"
  git -C "$src" fetch origin "$base_sha"
  git -C "$src" checkout --detach "$base_sha"
  echo "$src"
}

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

# A: current-main baseline.
MAIN_SRC="$(prepare_repo main "$MAIN_SHA")"
replay_variant main "$MAIN_SRC"

# B: converter-only: exact upstream PR #1495 head.
CONV_SRC="$ROOT/src-converter_only"
rm -rf "$CONV_SRC"
git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$CONV_SRC"
git -C "$CONV_SRC" fetch origin "$CONVERTER_SHA"
git -C "$CONV_SRC" checkout --detach "$CONVERTER_SHA"
replay_variant converter_only "$CONV_SRC"

# C: controller-only: exact upstream PR #1472 head.
CTRL_SRC="$ROOT/src-controller_only"
rm -rf "$CTRL_SRC"
git clone --filter=blob:none https://github.com/VihaanAgarwal/ManiSkill.git "$CTRL_SRC"
git -C "$CTRL_SRC" fetch origin "$CONTROLLER_SHA"
git -C "$CTRL_SRC" checkout --detach "$CONTROLLER_SHA"
replay_variant controller_only "$CTRL_SRC"

# D: composed: main + controller #1472 change + converter #1495 change.
COMP_SRC="$ROOT/src-composed"
rm -rf "$COMP_SRC"
git clone --filter=blob:none https://github.com/mani-skill/ManiSkill.git "$COMP_SRC"
git -C "$COMP_SRC" checkout --detach "$MAIN_SHA"
git -C "$COMP_SRC" config user.email "validation@semrepair.local"
git -C "$COMP_SRC" config user.name "SemRepair validation"
git -C "$COMP_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git
git -C "$COMP_SRC" fetch controller "$CONTROLLER_SHA"
git -C "$COMP_SRC" cherry-pick "$CONTROLLER_SHA"
git -C "$COMP_SRC" remote add converter https://github.com/lindicaphxag-tech/ManiSkill.git
git -C "$COMP_SRC" fetch converter "$CONVERTER_SHA"
# Apply only the two production files from converter PR head relative to main.
git -C "$COMP_SRC" checkout "$CONVERTER_SHA" -- mani_skill/trajectory/utils/actions/conversion.py tests/test_action_conversion.py
git -C "$COMP_SRC" commit -m "Compose controller-sign and converter-representation fixes"
replay_variant composed "$COMP_SRC"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_replay_matrix.py \
  --root "$ROOT" --output "$ROOT/compensating_defects_matrix.json"
