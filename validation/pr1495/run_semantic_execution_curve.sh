#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-semantic-execution-curve}"
REPEATS="${REPEATS:-5}"
COUNT="${COUNT:-10}"
MAIN_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
ALPHAS=(0 0.1 0.25 0.5 1)
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
  local target="$1"
  local sha="$2"
  git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$target" >/dev/null
  git -C "$target" fetch origin "$sha" >/dev/null
  git -C "$target" checkout --detach "$sha" >/dev/null
}

MAIN_SRC="$ROOT/src-main"
clone_at "$MAIN_SRC" "$MAIN_SHA"
python -m pip install -e "$MAIN_SRC" >/dev/null
(
  cd "$MAIN_SRC"
  python "$HARNESS_ROOT/validation/pr1495/capture_rotation_request_corpus.py"     --traj-path "$RAW"     --count "$COUNT"     --corpus semantic_execution_curve_main_requests     --expected-source-root "$MAIN_SRC"     --output "$ROOT/request_corpus.json"
)

for alpha in "${ALPHAS[@]}"; do
  key="$(python - <<PY
value=float("$alpha")
print(str(value).replace(".", "p"))
PY
)"
  src="$ROOT/src-alpha-$key"
  clone_at "$src" "$CANDIDATE_SHA"
  python "$HARNESS_ROOT/validation/pr1495/build_source_interpolation_variant.py"     --source "$src" --alpha "$alpha"
  python -m pip install -e "$src" >/dev/null

  (
    cd "$src"
    SRC_EXPECTED="$src" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual=Path(mani_skill.__file__).resolve()
expected=Path(os.environ["SRC_EXPECTED"]).resolve()
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected {expected}")
print("source identity:", actual)
PY
  )

  python "$HARNESS_ROOT/validation/pr1495/evaluate_frozen_rotation_requests.py"     --corpus "$ROOT/request_corpus.json"     --variant "alpha_$key"     --expected-source-root "$src"     --output "$ROOT/semantic_alpha_$key.json"

  mkdir -p "$ROOT/execution_alpha_$key"
  for i in $(seq 0 $((REPEATS - 1))); do
    run_dir="$ROOT/execution_alpha_$key/run_$i"
    mkdir -p "$run_dir"
    cp "$RAW" "$run_dir/trajectory.h5"
    cp "$RAW_JSON" "$run_dir/trajectory.json"
    (
      cd "$src"
      python -m mani_skill.trajectory.replay_trajectory         --traj-path "$run_dir/trajectory.h5"         --use-first-env-state         -c pd_ee_delta_pose         -o state         --save-traj         --count "$COUNT"         --num-envs 1         -b physx_cpu
    ) >"$ROOT/execution_alpha_$key/repeat_$i.log" 2>&1
    cat "$ROOT/execution_alpha_$key/repeat_$i.log"
  done
done

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_semantic_execution_curve.py   --root "$ROOT"   --alphas 0 0.1 0.25 0.5 1   --repeats "$REPEATS"   --expected "$COUNT"   --output "$ROOT/semantic_execution_curve.json"
