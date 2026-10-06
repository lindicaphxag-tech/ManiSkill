#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-episode8-trace}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
HARNESS_ROOT="$PWD"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"

rm -rf "$ROOT"
mkdir -p "$ROOT/episode8"

python -m pip install --upgrade pip
python -m pip install -e .
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

cp "$RAW_ROOT/trajectory.h5" "$ROOT/episode8/trajectory.h5"
python - "$RAW_ROOT/trajectory.json" "$ROOT/episode8/trajectory.json" <<'PY'
import json,sys
src,dst=sys.argv[1:]
data=json.load(open(src,encoding="utf-8"))
episodes=[ep for ep in data["episodes"] if int(ep["episode_id"])==8]
if len(episodes)!=1:
    raise SystemExit(f"expected one episode 8, got {len(episodes)}")
data["episodes"]=episodes
json.dump(data,open(dst,"w",encoding="utf-8"),indent=2)
PY

clone_at() {
  local name="$1"
  local url="$2"
  local sha="$3"
  local src="$ROOT/src-$name"
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
    python validation/pr1495/trace_episode8_conversion.py       --traj-path "$ROOT/episode8/trajectory.h5"       --variant "$name"       --source-sha "$sha"       --expected-source-root "$src"       --output "$ROOT/$name.json"
  )
}

BASE_SRC="$(clone_at current_main https://github.com/lindicaphxag-tech/ManiSkill.git "$BASE_SHA")"
trace_variant current_main "$BASE_SRC" "$BASE_SHA"

CANDIDATE_SRC="$(clone_at contract_adapter_v2 https://github.com/lindicaphxag-tech/ManiSkill.git "$CANDIDATE_SHA")"
trace_variant contract_adapter_v2 "$CANDIDATE_SRC" "$CANDIDATE_SHA"

FUTURE_SRC="$(clone_at contract_adapter_v2_controller_fixed https://github.com/lindicaphxag-tech/ManiSkill.git "$CANDIDATE_SHA")"
git -C "$FUTURE_SRC" config user.email "validation@semrepair.local"
git -C "$FUTURE_SRC" config user.name "SemRepair validation"
git -C "$FUTURE_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git || true
git -C "$FUTURE_SRC" fetch controller "$CONTROLLER_SHA" >/dev/null
git -C "$FUTURE_SRC" cherry-pick "$CONTROLLER_SHA" >/dev/null
trace_variant contract_adapter_v2_controller_fixed "$FUTURE_SRC" "$CANDIDATE_SHA+$CONTROLLER_SHA"

python validation/pr1495/summarize_episode8_trace.py   --main "$ROOT/current_main.json"   --candidate "$ROOT/contract_adapter_v2.json"   --candidate-fixed "$ROOT/contract_adapter_v2_controller_fixed.json"   --output "$ROOT/episode8_differential.json"
