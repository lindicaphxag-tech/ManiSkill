# PegInsertionSide Diffusion Policy A/B assay

This Kaggle T4 experiment compares the official ManiSkill Diffusion Policy PegInsertionSide preset on the frozen base `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` with the same training setup using the exact open PR heads for [ManiSkill #1495](https://github.com/mani-skill/ManiSkill/pull/1495) and [#1472](https://github.com/mani-skill/ManiSkill/pull/1472).

## Protocol

- Official public `PegInsertionSide-v1` motion-planning demos; the raw data stays in Kaggle and is not exported.
- Same seed (1), 100 demos, state observations, `pd_ee_delta_pose`, `physx_cpu` evaluation, 300-step horizon, batch size 1024, and 100,000 training updates.
- The measured variant uses 20 evaluation episodes every 10,000 updates and disables video to reduce runtime. The upstream script's default 100 episodes every 5,000 updates and video capture are not used; the training/update configuration is unchanged.
- TensorBoard curves are exported as CSV/JSONL. W&B is disabled because no W&B credential is part of the experiment environment.
- Checkpoints and demonstrations are deleted or kept outside the exported artifact set; only logs, scalar curves, source identities, and hashes are emitted.

## Current state

The private Kaggle kernel `oblivicore/maniskill-dp-peg-1495-1472` was submitted with a Tesla T4 request. Version 1 stopped before training because the root package installer required Linux `mplib==0.1.1`, which has no compatible published distribution in the Kaggle Python 3.13 image. Version 2 installed successfully but stopped before training because the raw archive did not contain the guessed preprocessed filename. Version 3 correctly inventoried the archive but exposed that the official download contains only raw trajectories. Version 4 now invokes ManiSkill's documented `replay_trajectory` preprocessing command to generate the state/action HDF5 consumed by the Diffusion Policy baseline. Version 4 is running; no learned-policy result is claimed until both arms complete.

The runner installs ManiSkill in editable no-dependency mode and installs only the runtime packages this non-planning assay needs. The official PegInsertionSide demos and generated replay dataset are deleted before output packaging.

A single seed supports a paired mechanistic comparison, not a statistically powered performance claim. Success-rate increments have 0.05 resolution at each 20-episode evaluation point.
