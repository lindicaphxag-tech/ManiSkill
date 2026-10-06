#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-contract-adapter-trace}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
TARGET_EPISODE="${TARGET_EPISODE:-8}"
HARNESS_ROOT="$PWD"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"

mkdir -p "$ROOT"

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

trace_variant() {
  local name="$1"
  local src="$2"
  local sha="$3"
  python -m pip install -e "$src" >/dev/null
  (
    cd "$HARNESS_ROOT"
    python validation/pr1495/trace_contract_adapter_episode.py       --traj-path "$RAW"       --target-episode "$TARGET_EPISODE"       --variant "$name"       --source-sha "$sha"       --output "$ROOT/$name.json"
  )
}

BASE_SRC="$(clone_at current_main https://github.com/lindicaphxag-tech/ManiSkill.git "$BASE_SHA")"
python -m pip install -e "$BASE_SRC" >/dev/null
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)
test -f "$RAW"
trace_variant current_main "$BASE_SRC" "$BASE_SHA"

CANDIDATE_SRC="$(clone_at contract_adapter_v2 https://github.com/lindicaphxag-tech/ManiSkill.git "$CANDIDATE_SHA")"
trace_variant contract_adapter_v2 "$CANDIDATE_SRC" "$CANDIDATE_SHA"

FUTURE_SRC="$(clone_at contract_adapter_v2_controller_fixed https://github.com/lindicaphxag-tech/ManiSkill.git "$CANDIDATE_SHA")"
git -C "$FUTURE_SRC" config user.email "validation@semrepair.local"
git -C "$FUTURE_SRC" config user.name "SemRepair validation"
git -C "$FUTURE_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git || true
git -C "$FUTURE_SRC" fetch controller "$CONTROLLER_SHA" >/dev/null
git -C "$FUTURE_SRC" cherry-pick "$CONTROLLER_SHA" >/dev/null
FUTURE_SHA="$(git -C "$FUTURE_SRC" rev-parse HEAD)"
trace_variant contract_adapter_v2_controller_fixed "$FUTURE_SRC" "$FUTURE_SHA"

python validation/pr1495/summarize_episode_trace.py   --main "$ROOT/current_main.json"   --candidate "$ROOT/contract_adapter_v2.json"   --candidate-fixed "$ROOT/contract_adapter_v2_controller_fixed.json"   --output "$ROOT/episode_trace_summary.json"
