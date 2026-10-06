#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-endpoint-regime-audit}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"
HARNESS_ROOT="$PWD"

rm -rf "$ROOT"
mkdir -p "$ROOT"

python -m pip install --upgrade pip
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
  git -C "$src" fetch origin "$BASE_SHA" "$CANDIDATE_SHA" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
  echo "$src"
}

run_variant() {
  local name="$1"
  local src="$2"
  local count="$3"
  local demo="$ROOT/demos-$name"
  rm -rf "$demo"
  mkdir -p "$demo"
  cp "$RAW" "$demo/trajectory.h5"
  cp "$RAW_JSON" "$demo/trajectory.json"
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
    raise SystemExit(f"wrong source imported: {actual}; expected {expected}")
PY
    python -m mani_skill.trajectory.replay_trajectory       --traj-path "$demo/trajectory.h5"       --use-first-env-state -c pd_ee_delta_pose -o state --save-traj       --count "$count" --num-envs 1 -b physx_cpu
  )
}

MAIN2="$(clone_at main_count2 "$BASE_SHA")"
run_variant main_count2 "$MAIN2" 2

MAIN10="$(clone_at main_count10 "$BASE_SHA")"
run_variant main_count10 "$MAIN10" 10

CAND2="$(clone_at candidate_count2 "$CANDIDATE_SHA")"
run_variant candidate_count2 "$CAND2" 2

FILE2="$(clone_at candidate_with_main_conversion_count2 "$CANDIDATE_SHA")"
git -C "$FILE2" show "$BASE_SHA:mani_skill/trajectory/utils/actions/conversion.py"   > "$FILE2/mani_skill/trajectory/utils/actions/conversion.py"
MAIN_CONV_SHA="$(git -C "$FILE2" show "$BASE_SHA:mani_skill/trajectory/utils/actions/conversion.py" | sha256sum | awk '{print $1}')"
REPLACED_SHA="$(sha256sum "$FILE2/mani_skill/trajectory/utils/actions/conversion.py" | awk '{print $1}')"
test "$MAIN_CONV_SHA" = "$REPLACED_SHA"
run_variant candidate_with_main_conversion_count2 "$FILE2" 2

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_endpoint_regime_audit.py   --root "$ROOT"   --output "$ROOT/endpoint_regime_audit.json"
