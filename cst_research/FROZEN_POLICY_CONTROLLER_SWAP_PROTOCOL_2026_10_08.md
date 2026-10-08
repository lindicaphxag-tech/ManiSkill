# CST frozen learned-policy controller swap: prospective execution protocol

**Status at document creation: runs scheduled, outcome unknown.**
Protocol frozen before reading frozen-checkpoint CI results. An exploratory
engineering smoke is NOT an unbiased confirmatory top-conference trial.

## Public frozen policy provenance

- Third-party public MIT checkpoint:
  https://huggingface.co/kattri15/actionshift-baselines
- File: `ppo/pick_cube_final_ckpt.pt`
- SHA256:
  `3e6c95d63a2132843323e24cf7ba962b8cf2610f04b2a5a43f3efb6fef8497a8`
- Network: original ManiSkill PPO state-observation actor architecture,
  MLP 256x3 with deterministic mean; **no gradient updates, retraining or
  fine-tuning** during evaluation.
- Parent work credited: [ActionShift](https://github.com/Archerkattri/actionshift);
  do not pretend these pretrained weights are our own work.

## Gate 0: source frozen policy competence

- Public CI:
  https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-pickcube-cpu-20261008
- Task: PickCube-v1, `pd_ee_delta_pose`, `obs_mode=state`,
  PhysX CPU, four **preselected seeds [42,270,429,2026]**.
- 50 maximum steps/seed, full recorded per-seed `success_once`.
- If source policy cannot be loaded/evaluated on CPU, or succeeds on less
  than two of four episodes, label any paired migration study
  **insufficient competent-source evidence**. Do not claim improvement.
  CPU backend differs from original training conditions.

## Exploratory three-arm controller swap

- Public branch:
  https://github.com/lindicaphxag-tech/ManiSkill/tree/validation/frozen-ppo-ee-controller-swap-20261008
- Same public frozen checkpoint evaluated independently on **each own
  observation** (genuine closed-loop), no online learning.
- Arms:
  1. **Source** `pd_ee_delta_pose` in official ManiSkill Panda.
  2. **Executable adapter** `pd_ee_pose` (root-frame Cartesian
     absolute target), using source `PDEEPoseController` math for native
     delta decoding and target-pose composition.
  3. **Naive** `pd_ee_pose` with raw native delta sent directly as
     absolute target (intentionally mismatched action ABI).
- Only four prespecified initial seeds and a 50-step horizon. Each arm
  must receive the same seed; initial observations must be checked for
  equivalence, and incompatible scenes are an **INVALID EXPERIMENT** not
  a zero-success outcome.
- Outputs: per-episode success flag for every arm, initial observation
  mismatch, actual episode steps, checkpoint hash, runtime errors.
- No claims about task success until all three arms actually complete.
- If naive fails from action limits or IK, keep the failure; do not drop
  the episode from source/compiled denominator.

## Scope and major caveats

- Uses real official ManiSkill task physics but no hardware.
- The controller family here is *ManiSkill EE pose* whereas prior
  memory-handshake causal evidence was in *robosuite OSC*; success in
  one cannot be silently transferred to the other.
- At most four episodes is a **smoke experiment**, not a statistical
  claim about transfer success rates or safety. No p-values/CI or
  extrapolated L8/L9 merit are licensed by a 4-episode smoke.
- Must compare against ActionShift and other prior methods; do not
  relabel general frozen-policy action adaptation as novel.
- Any mismatch in observation shape, checkpoint tensor keys or task
  backend is an integration failure requiring disclosure.

## Advancement gate

If source is competent and all arms work, expand to at least
20–50 *new preregistered disjoint seeds*, longer horizon, paired
within-seed differences, and a deliberate *stateful controller-memory*
intervention (not only a changed numerical action chart).
Independent reproduction and maintainer acceptance remain separate
requirements.

External PR acceptance/merge on this research line remains **unconfirmed**.
