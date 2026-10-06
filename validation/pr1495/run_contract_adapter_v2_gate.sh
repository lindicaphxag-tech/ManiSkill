#!/usr/bin/env bash
set -euo pipefail

COUNT="${COUNT:-10}"
ROOT="${ROOT:-$PWD/.validation-contract-adapter-v2}"
BASE_SHA="107c9528b23b55bd276cf723c260a45ae7ce00ec"
CANDIDATE_SHA="69dd520f81831478021ccd542e4b113b6a74e043"
CONTROLLER_SHA="eed9be164797d41540421bda8adb3840377d7087"
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

clone_at() {
  local name="$1"
  local url="$2"
  local sha="$3"
  local src="$ROOT/src-$name"
  rm -rf "$src"
  git clone --filter=blob:none "$url" "$src" >/dev/null
  git -C "$src" fetch origin "$sha" >/dev/null
  git -C "$src" checkout --detach "$sha" >/dev/null
  echo "$src"
}

replay_variant() {
  local name="$1"
  local src="$2"
  local demo_root="$ROOT/demos-$name"
  rm -rf "$demo_root"
  mkdir -p "$demo_root"
  cp "$RAW" "$demo_root/trajectory.h5"
  cp "$RAW_JSON" "$demo_root/trajectory.json"

  python -m pip install -e "$src" >/dev/null
  (
    cd "$src"
    SRC_EXPECTED="$src" NAME_EXPECTED="$name" python - <<'PY'
from pathlib import Path
import os, mani_skill
actual=Path(mani_skill.__file__).resolve()
expected=Path(os.environ["SRC_EXPECTED"]).resolve()
print("variant=", os.environ["NAME_EXPECTED"], "import=", actual)
if expected not in actual.parents:
    raise SystemExit(f"wrong source imported: {actual}; expected {expected}")
PY
    python -m mani_skill.trajectory.replay_trajectory \
      --traj-path "$demo_root/trajectory.h5" \
      --use-first-env-state -c pd_ee_delta_pose -o state --save-traj \
      --count "$COUNT" --num-envs 1 -b physx_cpu
  )
}

BASE_SRC="$(clone_at current_main https://github.com/lindicaphxag-tech/ManiSkill.git "$BASE_SHA")"
replay_variant current_main "$BASE_SRC"

CANDIDATE_SRC="$(clone_at contract_adapter_v2 https://github.com/lindicaphxag-tech/ManiSkill.git "$CANDIDATE_SHA")"
python -m pip install -e "$CANDIDATE_SRC" >/dev/null
python -m pip install pytest >/dev/null
(
  cd "$CANDIDATE_SRC"
  python -m pytest -q tests/test_controller_contract_action_conversion.py
)
replay_variant contract_adapter_v2 "$CANDIDATE_SRC"

FUTURE_SRC="$(clone_at contract_adapter_v2_controller_fixed https://github.com/lindicaphxag-tech/ManiSkill.git "$CANDIDATE_SHA")"
git -C "$FUTURE_SRC" config user.email "validation@semrepair.local"
git -C "$FUTURE_SRC" config user.name "SemRepair validation"
git -C "$FUTURE_SRC" remote add controller https://github.com/VihaanAgarwal/ManiSkill.git || true
git -C "$FUTURE_SRC" fetch controller "$CONTROLLER_SHA" >/dev/null
git -C "$FUTURE_SRC" cherry-pick "$CONTROLLER_SHA" >/dev/null
replay_variant contract_adapter_v2_controller_fixed "$FUTURE_SRC"

cd "$HARNESS_ROOT"
python validation/pr1495/summarize_contract_adapter_v2.py \
  --root "$ROOT" --expected "$COUNT" \
  --output "$ROOT/contract_adapter_v2_gate.json"
