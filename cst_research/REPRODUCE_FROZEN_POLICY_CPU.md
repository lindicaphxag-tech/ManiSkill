# CST frozen-policy robot controller migration: external replication kit

**Purpose:** make the engineering claim independently falsifiable without a
private robot, private data, GPU, or the author's personal environment.

**Important:** This project did not train the pretrained PPO. All results
use the public pretrained ActionShift PPO actor weights. Do not cite the
present controller adapter as the invention of delta→absolute conversion.

## Minimal environment

Ubuntu x86_64 with CPU, Python 3.11, publicly installable ManiSkill 3.0.1,
SAPIEN/PhysX CPU, Hugging Face model hub access.

```bash
sudo apt-get update
sudo apt-get install -y libvulkan1 mesa-vulkan-drivers libgl1 libosmesa6
git clone https://github.com/lindicaphxag-tech/ManiSkill.git
cd ManiSkill
python -m pip install --upgrade pip
python -m pip install -e . huggingface_hub
```

Checkpoint source:
https://huggingface.co/kattri15/actionshift-baselines
`ppo/pick_cube_final_ckpt.pt`.
Require SHA256
`3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`.
The evaluator aborts on a hash mismatch. The neural PPO is frozen for all
experiments; no training/fine tuning is performed.

## 1. Source competence on the original controller (4 development seeds)

```bash
git checkout bdea061a09a257e6c8fd33b66c057ef9ac41cc52
python research/frozen_ppo_pickcube_gate.py
```

Observed **4/4 successful**, canonical
[CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716172915).
This validates the checkpoint ABI and original policy competence only.

## 2. 32-seed pilot on delta vs absolute end-effector action charts

```bash
git checkout 9976449a9c18c56764bc68ca69aaca06d1b0e1e2
python research/frozen_ppo_ee_swap.py
```

[Protocol fixed before evaluation](FROZEN_PPO_32_SEED_HOLDOUT_PRE_REG_2026_10_08.md).
Observed single-batch outcomes: original frozen PPO **32/32**, compiled
absolute EE actions **31/32**, naive raw action copy **0/32**,
[CI with all raw episodes](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37716840505).
Four previously observed development seeds are not included.

**Replication warning:** seed 10014 failed compiled control when reached as
the 14th task in the 32-seed sequence, yet later passed in standalone
[repetition](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717458927).
Eight later successive standalone repetitions yielded identical initial
observation SHA and compiled success (source step 19, target step 25),
[reproducibility audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37745709797).
Therefore we cannot claim a stable per-seed failure with the current
protocol. Re-run the whole 32-seed batch, record cross-run complete
state hashes, and avoid overconfident success-rate claims.

## 3. Four-seed pilot on *stateful* target-relative actions

```bash
git checkout bfbae6ad27622a3f54a8fb525f21324fce022e8c
python research/frozen_ppo_target_memory.py
```

The trained 42-D observation ABI differs from the destination controller's
49-D state ABI, which includes a 7-D live target-pose state. The code
explicitly verifies and removes that controller-only memory from the
policy observation **while retaining it in the runtime action compiler**.

Four development seeds yielded source 4/4, exact/refuse 2/4, bounded
nonexact projection 4/4, naive raw 1/4,
[CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717601656).
Projected commands are **not** exact goal-preserving commands; log every
intervention, never report them as exact transport.

Prospective 32 different seeds `20001–20032` are preregistered in
[FROZEN_PPO_MEMORY_32SEED_PILOT_PRE_REG_2026_10_08.md](FROZEN_PPO_MEMORY_32SEED_PILOT_PRE_REG_2026_10_08.md)
with a separate [CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746168558).
The document above was filed **before** that 32-seed job started.

## 4. Independent real OSC state-memory causal experiment

Separate from ManiSkill action-chart transfer, public robosuite+MuJoCo
physics tested live `desired` previous-goal memory transport against an
`achieved`-only shortcut on 16-step scripts, three action seeds.
Correct full-scene qpos discrepancies remained below ~`4.61e-7`, whereas
the shortcut diverged by `0.477–1.024` in mixed-unit qpos dimensions;
[actual 20-test CI](https://github.com/lindicaphxag-tech/robomimic/actions/runs/37715504522).
The script is not a trained PPO evaluation or a universal theorem.

## Reporting rubric

Please disclose all attempted episodes, exact code SHA, hardware, OS,
Python dependencies, checkpoint SHA, environment/task, simulator backend,
observation ABI, action ABI, initial state fingerprint, policy deterministic
mean vs sampled action, and all errors or rejected transfers. Submit a
counterexample even if it contradicts the expected result.

A green GitHub Actions job alone is insufficient: inspect **episode-level
success records**, explicit refusal counts, and all invalid/exception cases.
Avoid claiming that same-seed physics is exactly reproducible without
comparing recorded state hashes across different process runs.

## Maintainer-focused upstream contribution (distinct)

ManiSkill #429 minimal NumPy/Torch replay fix:
https://github.com/lindicaphxag-tech/ManiSkill/tree/fix/429-numpy-tensor-replay-minimal

Exact two-file diff has passed a targeted test and CPU replay of 16
official RL demonstrations (7/16 demos saved), independently of this
research:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715715576

This fixes an *already reported* 2024 type bug; do not claim it is a
publication-level original discovery. Posting/updating upstream discussion
requires repository write permissions that the current ChatGPT integration
does not have. Official maintainer review/merge is not confirmed.

## Success criteria for a genuinely flagship next paper

- Independent cross-machine reproduction of fixed-checkpoint physics;
- More than one pretrained policy, robot/task/controller family;
- Controllers with **internal memory**, not just basic delta→absolute;
- Explicit feasibility/refusal/approximation certificates grounded in
  actual target-native bounds and measured goal errors;
- Matched, preregistered test scenes and no cherry-picked restarts;
- Open implementation that a maintainer or lab can adopt;
- Prior-art analysis including stateful refinement and ActionShift.
