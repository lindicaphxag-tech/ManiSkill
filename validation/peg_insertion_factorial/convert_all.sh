#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$PWD/.factorial}"
COUNT="${CONVERT_COUNT:-150}"
RAW_DIR="$ROOT/shared_assets/demos/PegInsertionSide-v1/motionplanning"

for cond in 00 10 01 11; do
  wt="$ROOT/worktrees/$cond"
  asset="$ROOT/assets/$cond"
  dst="$asset/demos/PegInsertionSide-v1/motionplanning"
  mkdir -p "$dst" "$ROOT/logs"
  cp --reflink=auto "$RAW_DIR/trajectory.h5" "$dst/trajectory.h5"
  cp "$RAW_DIR/trajectory.json" "$dst/trajectory.json"

  (
    cd "$wt"
    set -o pipefail
    MS_ASSET_DIR="$asset"       python -m mani_skill.trajectory.replay_trajectory         --traj-path "$dst/trajectory.h5"         --use-first-env-state         --target-control-mode pd_ee_delta_pose         --obs-mode state         --save-traj         --num-envs 10         --sim-backend physx_cpu         --count "$COUNT"       2>&1 | tee "$ROOT/logs/convert_${cond}.log"
  )

  test -f "$dst/trajectory.state.pd_ee_delta_pose.physx_cpu.h5"
  test -f "$dst/trajectory.state.pd_ee_delta_pose.physx_cpu.json"
done
