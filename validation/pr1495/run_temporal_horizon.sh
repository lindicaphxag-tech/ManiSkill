#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/evidence/pr1495-temporal-horizon}"
COUNT="${COUNT:-10}"
CONVERSION="mani_skill/trajectory/utils/actions/conversion.py"
mkdir -p "$ROOT"
cp "$CONVERSION" "$ROOT/conversion.template.py"

cd /tmp
python -m mani_skill.utils.download_demo PegInsertionSide-v1
cd "$OLDPWD"

RAW_ROOT="$HOME/.maniskill/demos/PegInsertionSide-v1/motionplanning"
RAW_H5="$RAW_ROOT/trajectory.h5"
RAW_JSON="$RAW_ROOT/trajectory.json"

for BUDGET in 4 6 8 12; do
  echo "=== retry_budget=$BUDGET ==="
  BUDGET="$BUDGET" python - <<'PY'
from pathlib import Path
import os
template = Path("evidence/pr1495-temporal-horizon/conversion.template.py").read_text()
needle = "        for _ in range(4):"
count = template.count(needle)
if count != 1:
    raise SystemExit(f"expected exactly one retry loop, found {count}")
budget = int(os.environ["BUDGET"])
Path("mani_skill/trajectory/utils/actions/conversion.py").write_text(
    template.replace(needle, f"        for _ in range({budget}):")
)
PY

  OUT="$ROOT/budget-$BUDGET"
  mkdir -p "$OUT"
  cp "$RAW_H5" "$OUT/trajectory.h5"
  cp "$RAW_JSON" "$OUT/trajectory.json"

  set +e
  python -m mani_skill.trajectory.replay_trajectory     --traj-path "$OUT/trajectory.h5"     --use-first-env-state     -c pd_ee_delta_pose -o state --save-traj     --count "$COUNT" --num-envs 2 -b physx_cpu     2>&1 | tee "$OUT/replay.log"
  CODE="${PIPESTATUS[0]}"
  set -e
  echo "$CODE" > "$OUT/exit_code.txt"
  if [[ "$CODE" -ne 0 ]]; then
    echo "replay process failed for budget $BUDGET" >&2
    exit "$CODE"
  fi

done

cp "$ROOT/conversion.template.py" "$CONVERSION"
python validation/pr1495/summarize_temporal_horizon.py   --root "$ROOT"   --expected "$COUNT"   --output "$ROOT/summary.json"
