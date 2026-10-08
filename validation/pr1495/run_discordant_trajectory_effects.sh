#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-trajectory-effects}"
HARNESS_ROOT="$PWD"

for EPISODE in 1 63 96; do
  echo "=== tracing source episode $EPISODE ==="
  TARGET_EPISODE="$EPISODE"   ROOT="$ROOT/episode-$EPISODE"     bash validation/pr1495/run_episode8_protocol_trace.sh
done

python validation/pr1495/summarize_trajectory_effect_certificate.py   --root "$ROOT"   --output "$ROOT/trajectory_effect_certificate.json"
