#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$PWD/.factorial}"
mkdir -p "$ROOT/worktrees"

declare -A REFS=(
  [00]="62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
  [10]="a231074ef562a9638e24c3f9a4d35bb70d4960d1"
  [01]="cdd6db713ffe7edc3e0df3abfab51ea5320c1c0b"
  [11]="24dcccba3d0aeae56b6fba1f5168e22cc340ab71"
)

for cond in 00 10 01 11; do
  dir="$ROOT/worktrees/$cond"
  if [[ -e "$dir/.git" || -f "$dir/.git" ]]; then
    actual="$(git -C "$dir" rev-parse HEAD)"
    [[ "$actual" == "${REFS[$cond]}" ]] || {
      echo "worktree $cond has $actual, expected ${REFS[$cond]}" >&2
      exit 2
    }
    continue
  fi
  git worktree add --detach "$dir" "${REFS[$cond]}"
done

mkdir -p "$ROOT/shared_assets"
BASE="$ROOT/worktrees/00"
if [[ ! -f "$ROOT/shared_assets/demos/PegInsertionSide-v1/motionplanning/trajectory.h5" ]]; then
  (
    cd "$BASE"
    MS_ASSET_DIR="$ROOT/shared_assets"       python -m mani_skill.utils.download_demo PegInsertionSide-v1
  )
fi

echo "Factorial worktrees ready under $ROOT/worktrees"
