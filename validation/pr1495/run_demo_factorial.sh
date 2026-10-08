#!/usr/bin/env bash
# protocol-revision: headless-cpu-v2
set -euo pipefail

COUNT="${COUNT:-10}"
ROOT="${ROOT:-$PWD/.validation-pr1495-demo-factorial}"
BASE_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
CONTROLLER_SHA="5a408084daab6f2b644bcd3e653df11228071d98"
CONVERTER_SHA="8e6eb8cf28ebe7f0a1c32de7a2898ae814203109"
COMBINED_SHA="c282bb1b7d80b506104de31e52c8aba5cdbb62d0"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"
HARNESS_ROOT="$PWD"

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

convert_variant() {
  local variant="$1"
  local repo_url="$2"
  local sha="$3"
  local src="$ROOT/src-$variant"
  local demo_root="$ROOT/demos-$variant"

  rm -rf "$src" "$demo_root"
  git clone --filter=blob:none "$repo_url" "$src"
  git -C "$src" fetch origin "$sha"
  git -C "$src" checkout --detach "$sha"
  python -m pip install -e "$src"

  mkdir -p "$demo_root"
  cp "$RAW" "$demo_root/trajectory.h5"
  cp "$RAW_JSON" "$demo_root/trajectory.json"

  python - "$demo_root/trajectory.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
env_kwargs = data["env_info"]["env_kwargs"]
env_kwargs["render_backend"] = "none"
path.write_text(json.dumps(data, indent=2) + "\n")
PY

  (
    cd "$src"
    SRC_EXPECTED="$src" VARIANT_EXPECTED="$variant" SHA_EXPECTED="$sha" python - <<'PY'
from pathlib import Path
import os
import mani_skill
actual = Path(mani_skill.__file__).resolve()
expected = Path(os.environ["SRC_EXPECTED"]).resolve()
print("variant=", os.environ["VARIANT_EXPECTED"], "sha=", os.environ["SHA_EXPECTED"], "mani_skill_import=", actual)
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected under {expected}")
PY

    python -m mani_skill.trajectory.replay_trajectory \
      --traj-path "$demo_root/trajectory.h5" \
      --use-first-env-state \
      -c pd_ee_delta_pose \
      -o state \
      --save-traj \
      --allow-failure \
      --count "$COUNT" \
      --num-envs 1 \
      -b physx_cpu
  )

  local converted="$demo_root/trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
  local converted_json="${converted%.h5}.json"
  test -f "$converted"
  test -f "$converted_json"
}

convert_variant old_old "https://github.com/mani-skill/ManiSkill.git" "$BASE_SHA"
convert_variant controller_only "https://github.com/lindicaphxag-tech/ManiSkill.git" "$CONTROLLER_SHA"
convert_variant converter_only "https://github.com/lindicaphxag-tech/ManiSkill.git" "$CONVERTER_SHA"
convert_variant combined "https://github.com/lindicaphxag-tech/ManiSkill.git" "$COMBINED_SHA"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_demo_factorial.py \
  --root "$ROOT" \
  --raw-json "$RAW_JSON" \
  --count "$COUNT" \
  --identity-json "$ROOT/identities.json" \
  --output "$ROOT/demo_factorial.json"
