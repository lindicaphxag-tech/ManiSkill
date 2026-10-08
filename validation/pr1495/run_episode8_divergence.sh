#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-episode8-divergence}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
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
  local sha="$2"
  local src="$ROOT/src-$name"
  rm -rf "$src"
  git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$src" >/dev/null
  git -C "$src" fetch origin "$sha" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
  echo "$src"
}

trace_variant() {
  local name="$1"
  local src="$2"
  python -m pip install -e "$src" >/dev/null
  python "$HARNESS_ROOT/validation/pr1495/capture_episode8_trace.py" \
    --traj-path "$RAW" \
    --count 9 \
    --episode-id 8 \
    --variant "$name" \
    --expected-source-root "$src" \
    --output "$ROOT/$name.json"
}

MAIN_SRC="$(clone_at current_main "$BASE_SHA")"
trace_variant current_main "$MAIN_SRC"

CANDIDATE_SRC="$(clone_at contract_adapter_v2 "$CANDIDATE_SHA")"
trace_variant contract_adapter_v2 "$CANDIDATE_SRC"

FUTURE_SRC="$(clone_at contract_adapter_v2_controller_fixed "$CANDIDATE_SHA")"
git -C "$FUTURE_SRC" config user.email "validation@semrepair.local"
git -C "$FUTURE_SRC" config user.name "SemRepair validation"
git -C "$FUTURE_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git || true
git -C "$FUTURE_SRC" fetch controller "$CONTROLLER_SHA" >/dev/null
git -C "$FUTURE_SRC" cherry-pick "$CONTROLLER_SHA" >/dev/null
trace_variant contract_adapter_v2_controller_fixed "$FUTURE_SRC"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_episode8_divergence.py \
  --root "$ROOT" \
  --output "$ROOT/episode8_divergence.json"
