# PegInsertionSide Diffusion Policy A/B assay

This Kaggle T4 experiment compares the official ManiSkill Diffusion Policy PegInsertionSide preset on the frozen base `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` with the exact open PR #1495 head on the same base.

## Protocol

- Official public `PegInsertionSide-v1` motion-planning demos; the raw data stays in Kaggle and is not exported.
- Each arm independently replays the raw demonstrations under its own checked-out source tree; converted-dataset HDF5 and JSON SHA-256 hashes are recorded per arm.
- Same seed (1), 100 demos, state observations, `pd_ee_delta_pose`, `physx_cpu` evaluation, 300-step horizon, batch size 1024, and 100,000 training updates.
- The measured variant uses 20 evaluation episodes every 10,000 updates and disables video to reduce runtime. The upstream script's default 100 episodes every 5,000 updates and video capture are not used; the training/update configuration is unchanged.
- TensorBoard curves are exported as CSV/JSONL. W&B is disabled because no W&B credential is part of the experiment environment.
- Checkpoints and demonstrations are deleted or kept outside the exported artifact set; only logs, scalar curves, source identities, and hashes are emitted.

## Current state

The private Kaggle kernel `oblivicore/maniskill-dp-peg-1495-1472` was submitted with a Tesla T4 request. Versions 1–3 stopped before training during dependency or demo preparation. Version 4 invokes the documented replay command but used a single dataset replayed under the base for both arms; it is retained as a pipeline diagnostic only and its policy metrics are inadmissible. A corrected version 5 runner has been prepared to independently replay each arm's dataset before training. It has not been submitted while v4 is still running.

The runner installs ManiSkill in editable no-dependency mode and installs only the runtime packages this non-planning assay needs. The official PegInsertionSide demos and generated replay dataset are deleted before output packaging.

### Validity audit in progress

Before interpreting v4, an audit found that its runner replayed the raw demos
only once under the frozen base, then reused that converted dataset for both
arms. That is not a valid paired comparison for a change to action conversion.
See [the action-sign audit](ACTION_SIGN_AUDIT.md) for the separate stacking
hazard with #1472. No result from v4 is evidence for either PR.

A single seed supports a paired mechanistic comparison, not a statistically powered performance claim. Success-rate increments have 0.05 resolution at each 20-episode evaluation point.
