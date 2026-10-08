#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-episode8-repair-path}"
CANDIDATE_SHA="bd0e4feae2491a0d433107210ce8c16b8e8fb69a"
RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW="$RAW_ROOT/trajectory.h5"
HARNESS_ROOT="$PWD"

rm -rf "$ROOT"
mkdir -p "$ROOT"

git clone --filter=blob:none https://github.com/lindicaphxag-tech/ManiSkill.git "$ROOT/candidate" >/dev/null
git -C "$ROOT/candidate" fetch origin "$CANDIDATE_SHA" >/dev/null
git -C "$ROOT/candidate" checkout --detach "$CANDIDATE_SHA" >/dev/null

python -m pip install --upgrade pip
python -m pip install -e "$ROOT/candidate" >/dev/null
(
  cd /tmp
  python -m mani_skill.utils.download_demo "PegInsertionSide-v1"
)

python "$HARNESS_ROOT/validation/pr1495/scan_episode8_repair_path.py" \
  --raw-traj "$RAW" \
  --candidate-source-root "$ROOT/candidate" \
  --candidate-sha "$CANDIDATE_SHA" \
  --episode-id 8 \
  --step 0.05 \
  --output "$ROOT/episode8_repair_path.json"
