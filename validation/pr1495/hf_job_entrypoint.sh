#!/usr/bin/env bash
set -euo pipefail

: "${VARIANT:?VARIANT must be baseline or fixed}"
SEED="${SEED:-1}"
HARNESS_SHA="${HARNESS_SHA:-7e3ee79fd50979c15bd9d234d4a120d04e05a7e3}"
HARNESS_REPO="${HARNESS_REPO:-https://github.com/lindicaphxag-tech/ManiSkill.git}"
HARNESS_DIR="${HARNESS_DIR:-/tmp/pr1495-harness}"
WORK_ROOT="${WORK_ROOT:-/tmp/pr1495-work-${VARIANT}-seed${SEED}}"
TRACK_MODE="${TRACK_MODE:-tensorboard}"

echo "JOB_ID=${JOB_ID:-unknown}"
echo "ACCELERATOR=${ACCELERATOR:-unknown}"
echo "CPU_CORES=${CPU_CORES:-unknown}"
echo "MEMORY=${MEMORY:-unknown}"
echo "VARIANT=$VARIANT SEED=$SEED TRACK_MODE=$TRACK_MODE"

if [[ "${ACCELERATOR:-none}" == "none" ]]; then
  echo "GPU accelerator required for the 100k Diffusion Policy training run" >&2
  exit 2
fi

rm -rf "$HARNESS_DIR"
git clone --filter=blob:none "$HARNESS_REPO" "$HARNESS_DIR"
git -C "$HARNESS_DIR" fetch origin "$HARNESS_SHA"
git -C "$HARNESS_DIR" checkout --detach "$HARNESS_SHA"

export VARIANT SEED WORK_ROOT TRACK_MODE
export MS_SKIP_ASSET_DOWNLOAD_PROMPT=1

exec bash "$HARNESS_DIR/validation/pr1495/run_peg_dp.sh"
