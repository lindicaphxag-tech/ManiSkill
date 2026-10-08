#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-pr1495-paired-fidelity}"
COUNT="${COUNT:-10}"
MAIN_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONVERTER_SHA="cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
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

capture() {
  local corpus="$1"
  local src="$2"
  python -m pip install -e "$src" >/dev/null
  python "$HARNESS_ROOT/validation/pr1495/capture_rotation_request_corpus.py"     --traj-path "$RAW"     --count "$COUNT"     --corpus "$corpus"     --expected-source-root "$src"     --output "$ROOT/$corpus.json"
}

evaluate() {
  local corpus="$1"
  local variant="$2"
  local src="$3"
  python -m pip install -e "$src" >/dev/null
  python "$HARNESS_ROOT/validation/pr1495/evaluate_frozen_rotation_requests.py"     --corpus "$ROOT/$corpus.json"     --variant "$variant"     --expected-source-root "$src"     --output "$ROOT/${corpus}__${variant}.json"
}

MAIN_SRC="$(clone_at main https://github.com/mani-skill/ManiSkill.git "$MAIN_SHA")"
CONV_SRC="$(clone_at converter_only https://github.com/lindicaphxag-tech/ManiSkill.git "$CONVERTER_SHA")"
CTRL_SRC="$(clone_at controller_only https://github.com/VihaanAgarwal/ManiSkill.git "$CONTROLLER_SHA")"
COMP_SRC="$(clone_at composed https://github.com/mani-skill/ManiSkill.git "$MAIN_SHA")"
compose_controller_fix "$COMP_SRC"
compose_converter_fix "$COMP_SRC"

# Freeze two independent request distributions before comparing implementations.
capture baseline_generated "$MAIN_SRC"
capture composed_generated "$COMP_SRC"

for corpus in baseline_generated composed_generated; do
  evaluate "$corpus" main "$MAIN_SRC"
  evaluate "$corpus" converter_only "$CONV_SRC"
  evaluate "$corpus" controller_only "$CTRL_SRC"
  evaluate "$corpus" composed "$COMP_SRC"
done

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_paired_semantic_fidelity.py   --root "$ROOT"   --output "$ROOT/paired_semantic_fidelity.json"
