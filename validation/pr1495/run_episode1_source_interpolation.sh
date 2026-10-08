#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-episode1-source-interpolation}"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"
ALPHAS=(0 0.1 0.25 0.5 1)
HARNESS_ROOT="$PWD"

rm -rf "$ROOT"
mkdir -p "$ROOT"
python -m pip install --upgrade pip
python -m pip install -e .
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

for alpha in "${ALPHAS[@]}"; do
  key="$(python - <<PY
value=float("$alpha")
print(str(value).replace(".", "p"))
PY
)"
  src="$ROOT/src_alpha_$key"
  demo="$ROOT/demo_alpha_$key"
  git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$src" >/dev/null
  git -C "$src" fetch origin "$CANDIDATE_SHA" >/dev/null
  git -C "$src" checkout --detach "$CANDIDATE_SHA" >/dev/null
  python "$HARNESS_ROOT/validation/pr1495/build_source_interpolation_variant.py" --source "$src" --alpha "$alpha"
  python -m pip install -e "$src" >/dev/null
  mkdir -p "$demo"
  cp "$RAW" "$demo/trajectory.h5"
  cp "$RAW_JSON" "$demo/trajectory.json"
  (
    cd "$src"
    SRC_EXPECTED="$src" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual=Path(mani_skill.__file__).resolve()
expected=Path(os.environ["SRC_EXPECTED"]).resolve()
print("import",actual)
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected {expected}")
PY
    python -m mani_skill.trajectory.replay_trajectory \
      --traj-path "$demo/trajectory.h5" \
      --use-first-env-state \
      -c pd_ee_delta_pose -o state --save-traj \
      --count 10 --num-envs 1 -b physx_cpu
  ) >"$ROOT/alpha_$key.log" 2>&1
  cat "$ROOT/alpha_$key.log"
done

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_episode1_source_interpolation.py \
  --root "$ROOT" \
  --alphas 0 0.1 0.25 0.5 1 \
  --output "$ROOT/source_interpolation.json"
