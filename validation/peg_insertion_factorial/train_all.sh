#!/usr/bin/env bash
set -euo pipefail

SEED="${1:-1}"
ROOT="${2:-$PWD/.factorial}"
WANDB_ARGS=()
if [[ -n "${WANDB_ENTITY:-}" ]]; then
  WANDB_ARGS=(--track --wandb_entity "$WANDB_ENTITY" --wandb_project_name "ManiSkill-PR1495-factorial")
fi

for cond in 00 10 01 11; do
  wt="$ROOT/worktrees/$cond"
  demo="$ROOT/assets/$cond/demos/PegInsertionSide-v1/motionplanning/trajectory.state.pd_ee_delta_pose.physx_cpu.common100.h5"
  run_name="pr1495_factorial_${cond}_seed${SEED}"

  (
    cd "$wt/examples/baselines/diffusion_policy"
    python train.py       --env-id PegInsertionSide-v1       --demo-path "$demo"       --control-mode pd_ee_delta_pose       --sim-backend physx_cpu       --num-demos 100       --max_episode_steps 300       --total_iters 100000       --eval_freq 5000       --num_eval_episodes 100       --num_eval_envs 10       --seed "$SEED"       --exp-name "$run_name"       --demo_type motionplanning       --no_capture_video       "${WANDB_ARGS[@]}"       2>&1 | tee "$ROOT/logs/train_${cond}_seed${SEED}.log"
  )
done
