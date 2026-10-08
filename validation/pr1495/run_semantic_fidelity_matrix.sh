#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-pr1495-semantic-fidelity}"
COUNT="${COUNT:-10}"
MAIN_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERTER_SHA="cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
ADAPTIVE_SHA="80bd0fb678fd9534830dac18418c777b7ed1a2a3"
HARNESS_ROOT="$PWD"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"

mkdir -p "$ROOT"
python -m pip install --upgrade pip
python -m pip install -e .
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

clone_at() {
  local name="$1"
  local url="$2"
  local sha="$3"
  local src="$ROOT/src-$name"
  rm -rf "$src"
  git clone --filter=blob:none "$url" "$src" >/dev/null
  git -C "$src" fetch origin "$sha" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
  echo "$src"
}

compose_controller_fix() {
  local src="$1"
  git -C "$src" config user.email "validation@semrepair.local"
  git -C "$src" config user.name "SemRepair validation"
  git -C "$src" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git || true
  git -C "$src" fetch controller "$CONTROLLER_SHA" >/dev/null
  git -C "$src" cherry-pick "$CONTROLLER_SHA" >/dev/null
}

compose_converter_fix() {
  local src="$1"
  git -C "$src" remote add converter https://github.com/lindicaphxag-tech/ManiSkill.git || true
  git -C "$src" fetch converter "$CONVERTER_SHA" >/dev/null
  git -C "$src" checkout "$CONVERTER_SHA" --     mani_skill/trajectory/utils/actions/conversion.py     tests/test_action_conversion.py
  git -C "$src" commit -m "Compose converter representation fix" >/dev/null
}

measure_variant() {
  local name="$1"
  local src="$2"
  python -m pip install -e "$src" >/dev/null
  python "$HARNESS_ROOT/validation/pr1495/measure_rotation_semantic_fidelity.py"     --traj-path "$RAW"     --count "$COUNT"     --variant "$name"     --expected-source-root "$src"     --output "$ROOT/$name.json"
}

MAIN_SRC="$(clone_at main https://github.com/mani-skill/ManiSkill.git "$MAIN_SHA")"
measure_variant main "$MAIN_SRC"

CONV_SRC="$(clone_at converter_only https://github.com/lindicaphxag-tech/ManiSkill.git "$CONVERTER_SHA")"
measure_variant converter_only "$CONV_SRC"

CTRL_SRC="$(clone_at controller_only https://github.com/VihaanAgarwal/ManiSkill.git "$CONTROLLER_SHA")"
measure_variant controller_only "$CTRL_SRC"

COMP_SRC="$(clone_at composed https://github.com/mani-skill/ManiSkill.git "$MAIN_SHA")"
compose_controller_fix "$COMP_SRC"
compose_converter_fix "$COMP_SRC"
measure_variant composed "$COMP_SRC"

ADAPT_SRC="$(clone_at adaptive_current https://github.com/lindicaphxag-tech/ManiSkill.git "$ADAPTIVE_SHA")"
measure_variant adaptive_current "$ADAPT_SRC"

ADAPT_FIX_SRC="$(clone_at adaptive_controller_fixed https://github.com/lindicaphxag-tech/ManiSkill.git "$ADAPTIVE_SHA")"
compose_controller_fix "$ADAPT_FIX_SRC"
measure_variant adaptive_controller_fixed "$ADAPT_FIX_SRC"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_semantic_fidelity.py   --root "$ROOT"   --output "$ROOT/semantic_fidelity_matrix.json"
