#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-pr1495-current-head}"
REPEATS="${REPEATS:-5}"
COUNT="${COUNT:-10}"
MAIN_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
PR_SHA="875ae4d8777678119b2f192ee186c6c15e6894d5"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
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
  local url="$2"
  local sha="$3"
  local src="$ROOT/src-$name"
  git clone --filter=blob:none "$url" "$src" >/dev/null
  git -C "$src" fetch origin "$sha" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
  echo "$src"
}

MAIN_SRC="$(clone_at main https://github.com/mani-skill/ManiSkill.git "$MAIN_SHA")"
PR_SRC="$(clone_at pr_current https://github.com/lindicaphxag-tech/ManiSkill.git "$PR_SHA")"
PR_CTRL_SRC="$(clone_at pr_current_plus_1472 https://github.com/lindicaphxag-tech/ManiSkill.git "$PR_SHA")"

git -C "$PR_CTRL_SRC" config user.email "validation@semrepair.local"
git -C "$PR_CTRL_SRC" config user.name "SemRepair validation"
git -C "$PR_CTRL_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git
git -C "$PR_CTRL_SRC" fetch controller "$CONTROLLER_SHA" >/dev/null
git -C "$PR_CTRL_SRC" cherry-pick "$CONTROLLER_SHA" >/dev/null

run_variant() {
  local name="$1"
  local src="$2"
  mkdir -p "$ROOT/$name"

  python -m pip install -e "$src" >/dev/null
  (
    cd "$src"
    SRC_EXPECTED="$src" NAME_EXPECTED="$name" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual=Path(mani_skill.__file__).resolve()
expected=Path(os.environ["SRC_EXPECTED"]).resolve()
print("variant=",os.environ["NAME_EXPECTED"],"import=",actual)
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected under {expected}")
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

run_variant main "$MAIN_SRC"
run_variant pr_current "$PR_SRC"
run_variant pr_current_plus_1472 "$PR_CTRL_SRC"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_current_head_gate.py   --root "$ROOT"   --repeats "$REPEATS"   --expected "$COUNT"   --output "$ROOT/current_head_gate.json"
