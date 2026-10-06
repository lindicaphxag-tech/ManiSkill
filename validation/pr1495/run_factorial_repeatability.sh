#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-pr1495-factorial-repeatability}"
REPEATS="${REPEATS:-5}"
COUNT="${COUNT:-10}"
BASE_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONTROLLER_SHA="5a408084daab6f2b644bcd3e653df11228071d98"
CONVERTER_SHA="8e6eb8cf28ebe7f0a1c32de7a2898ae814203109"
COMBINED_SHA="c282bb1b7d80b506104de31e52c8aba5cdbb62d0"
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
test -f "$RAW"
test -f "$RAW_JSON"

cat > "$ROOT/identities.json" <<JSON
{
  "old_old": "$BASE_SHA",
  "controller_only": "$CONTROLLER_SHA",
  "converter_only": "$CONVERTER_SHA",
  "combined": "$COMBINED_SHA"
}
JSON

prepare_variant() {
  local name="$1"
  local repo_url="$2"
  local sha="$3"
  local src="$ROOT/src-$name"
  git clone --filter=blob:none "$repo_url" "$src" >/dev/null
  git -C "$src" fetch origin "$sha" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
}

prepare_variant old_old "https://github.com/mani-skill/ManiSkill.git" "$BASE_SHA"
prepare_variant controller_only "https://github.com/lindicaphxag-tech/ManiSkill.git" "$CONTROLLER_SHA"
prepare_variant converter_only "https://github.com/lindicaphxag-tech/ManiSkill.git" "$CONVERTER_SHA"
prepare_variant combined "https://github.com/lindicaphxag-tech/ManiSkill.git" "$COMBINED_SHA"

run_once() {
  local name="$1"
  local repeat="$2"
  local src="$ROOT/src-$name"
  local out="$ROOT/$name/repeat_$repeat"
  rm -rf "$out"
  mkdir -p "$out"
  cp "$RAW" "$out/trajectory.h5"
  cp "$RAW_JSON" "$out/trajectory.json"

  python - "$out/trajectory.json" <<'PY'
import json
import sys
from pathlib import Path
p = Path(sys.argv[1])
d = json.loads(p.read_text())
d["env_info"]["env_kwargs"]["render_backend"] = "none"
p.write_text(json.dumps(d, indent=2) + "\n")
PY

  python -m pip install -e "$src" >/dev/null
  (
    cd "$src"
    SRC_EXPECTED="$src" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual = Path(mani_skill.__file__).resolve()
expected = Path(os.environ["SRC_EXPECTED"]).resolve()
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected under {expected}")
print("source_identity_ok", actual)
PY
    python -m mani_skill.trajectory.replay_trajectory \
      --traj-path "$out/trajectory.h5" \
      --use-first-env-state \
      -c pd_ee_delta_pose \
      -o state \
      --save-traj \
      --allow-failure \
      --count "$COUNT" \
      --num-envs 1 \
      -b physx_cpu
  ) >"$ROOT/$name/repeat_$repeat.log" 2>&1
  cat "$ROOT/$name/repeat_$repeat.log"
}

for repeat in $(seq 0 $((REPEATS - 1))); do
  for name in old_old controller_only converter_only combined; do
    run_once "$name" "$repeat"
  done
done

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_factorial_repeatability.py \
  --root "$ROOT" \
  --raw-json "$RAW_JSON" \
  --repeats "$REPEATS" \
  --count "$COUNT" \
  --identity-json "$ROOT/identities.json" \
  --output "$ROOT/factorial_repeatability.json"

