#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-replay-repeatability}"
REPEATS="${REPEATS:-5}"
COUNT="${COUNT:-10}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"
HARNESS_ROOT="$PWD"

rm -rf "$ROOT"
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
  git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$src" >/dev/null
  git -C "$src" fetch origin "$sha" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
}

clone_at current_main "$BASE_SHA"
clone_at contract_adapter_v2 "$CANDIDATE_SHA"

run_variant() {
  local name="$1"
  local src="$ROOT/src-$name"
  mkdir -p "$ROOT/$name"

  python -m pip install -e "$src" >/dev/null
  (
    cd "$src"
    SRC_EXPECTED="$src" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual=Path(mani_skill.__file__).resolve()
expected=Path(os.environ["SRC_EXPECTED"]).resolve()
print("import", actual)
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected {expected}")
PY
  )

  for i in $(seq 0 $((REPEATS - 1))); do
    local run_dir="$ROOT/$name/run_$i"
    rm -rf "$run_dir"
    mkdir -p "$run_dir"
    cp "$RAW" "$run_dir/trajectory.h5"
    cp "$RAW_JSON" "$run_dir/trajectory.json"

    (
      cd "$src"
      python -m mani_skill.trajectory.replay_trajectory         --traj-path "$run_dir/trajectory.h5"         --use-first-env-state         -c pd_ee_delta_pose         -o state         --save-traj         --count "$COUNT"         --num-envs 1         -b physx_cpu
    ) >"$ROOT/$name/repeat_$i.log" 2>&1
    cat "$ROOT/$name/repeat_$i.log"
  done
}

run_variant current_main
run_variant contract_adapter_v2

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_replay_repeatability.py   --root "$ROOT"   --repeats "$REPEATS"   --expected "$COUNT"   --output "$ROOT/replay_repeatability.json"
