#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/.validation-episode8-context}"
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

python - "$RAW" "$ROOT/episode8.h5" <<'PY'
import json
import sys
from pathlib import Path
import h5py

raw = Path(sys.argv[1])
out = Path(sys.argv[2])
with h5py.File(raw, "r") as src, h5py.File(out, "w") as dst:
    for key, value in src.attrs.items():
        dst.attrs[key] = value
    src.copy("traj_8", dst)

meta = json.loads(raw.with_suffix(".json").read_text())
chosen = [ep for ep in meta["episodes"] if int(ep["episode_id"]) == 8]
assert len(chosen) == 1
meta["episodes"] = chosen
out.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n")
PY

python "$HARNESS_ROOT/validation/pr1495/capture_episode8_trace.py" \
  --traj-path "$RAW" \
  --count 9 \
  --episode-id 8 \
  --variant "contract_adapter_v2_prefix_0_8" \
  --expected-source-root "$ROOT/candidate" \
  --output "$ROOT/prefix.json"

python "$HARNESS_ROOT/validation/pr1495/capture_episode8_trace.py" \
  --traj-path "$ROOT/episode8.h5" \
  --count 1 \
  --episode-id 8 \
  --variant "contract_adapter_v2_isolated" \
  --expected-source-root "$ROOT/candidate" \
  --output "$ROOT/isolated.json"

python "$HARNESS_ROOT/validation/pr1495/summarize_episode8_context.py" \
  --prefix "$ROOT/prefix.json" \
  --isolated "$ROOT/isolated.json" \
  --output "$ROOT/episode8_context.json"
