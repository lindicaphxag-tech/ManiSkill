#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_SHA="8c920c4270460851cedd2737657584586d3dc66f"
ROOT="${ROOT:-$(mktemp -d)}"
OUT="${OUT:-$PWD/lerobot_mapping_compensation.json}"

mkdir -p "$ROOT/src/lerobot/processor"
curl -fsSL \
  "https://raw.githubusercontent.com/huggingface/lerobot/${UPSTREAM_SHA}/src/lerobot/processor/relative_action_processor.py" \
  -o "$ROOT/src/lerobot/processor/relative_action_processor.py"

test -s "$ROOT/src/lerobot/processor/relative_action_processor.py"

python validation/crossstack/lerobot_mapping_compensation.py \
  --source-root "$ROOT" \
  --upstream-sha "$UPSTREAM_SHA" \
  --output "$OUT"

cat "$OUT"
