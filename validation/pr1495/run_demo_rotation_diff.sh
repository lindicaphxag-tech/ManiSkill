#!/usr/bin/env bash
set -euo pipefail

COUNT="${COUNT:-10}"
ROOT="${ROOT:-$PWD/.validation-pr1495-demo-diff}"
BASE_SHA="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
FIX_SHA="cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"
HARNESS_ROOT="$PWD"

mkdir -p "$ROOT"

# Install dependencies from the validation checkout, but all production
# conversions below execute from variant-private exact source directories.
python -m pip install --upgrade pip
python -m pip install -e .

# Avoid importing the repository checkout from the current working directory.
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

if [[ ! -f "$RAW" || ! -f "$RAW_JSON" ]]; then
  echo "official raw trajectory missing after download" >&2
  exit 1
fi

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

  # Causal identity gate: execute inside the exact checkout and verify import.
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
      --count "$COUNT" \
      --num-envs 2 \
      -b physx_cpu
  )
}

convert_variant baseline "https://github.com/mani-skill/ManiSkill.git" "$BASE_SHA"
convert_variant fixed "https://github.com/lindicaphxag-tech/ManiSkill.git" "$FIX_SHA"

BASE="$ROOT/demos-baseline/trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
FIX="$ROOT/demos-fixed/trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
if [[ ! -f "$BASE" || ! -f "$FIX" ]]; then
  echo "paired converted trajectories missing" >&2
  find "$ROOT" -maxdepth 3 -type f | sort >&2
  exit 1
fi

cd "$HARNESS_ROOT"
python validation/pr1495/analyze_demo_rotation_diff.py \
  --baseline "$BASE" \
  --fixed "$FIX" \
  --output "$ROOT/demo_rotation_diff.json"
