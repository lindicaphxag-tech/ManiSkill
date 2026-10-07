# PegInsertionSide Diffusion Policy A/B assay

This Kaggle T4 experiment compares the official ManiSkill Diffusion Policy PegInsertionSide preset on the frozen base `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` with #1495 and the exact changed-file patch from [ManiSkill #1472](https://github.com/mani-skill/ManiSkill/pull/1472).

## Protocol

- Official public `PegInsertionSide-v1` motion-planning demos; the raw data stays in Kaggle and is not exported.
- Each arm independently replays the raw demonstrations under its own checked-out source tree; converted-dataset HDF5 and JSON SHA-256 hashes are recorded per arm.
- The treatment is frozen at #1495 `875ae4d8777678119b2f192ee186c6c15e6894d5` plus the controller line change and regression test file from #1472 `eed9be164797d41540421bda8adb3840377d7087`.
- Same seed (1), 100 demos, state observations, `pd_ee_delta_pose`, `physx_cpu` evaluation, 300-step horizon, batch size 1024, and 100,000 training updates.
- The measured variant uses 20 evaluation episodes every 10,000 updates and disables video to reduce runtime. The upstream script's default 100 episodes every 5,000 updates and video capture are not used; the training/update configuration is unchanged.
- TensorBoard curves are exported as CSV/JSONL. W&B is disabled because no W&B credential is part of the experiment environment.
- Checkpoints and demonstrations are deleted or kept outside the exported artifact set; only logs, scalar curves, source identities, and hashes are emitted.

## Current state

The private Kaggle kernel `oblivicore/maniskill-dp-peg-1495-1472` was submitted with a Tesla T4 request. Versions 1–3 stopped before training during dependency or demo preparation. Version 4 invokes the documented replay command but used a single dataset replayed under the base for both arms; it is retained as a pipeline diagnostic only and its policy metrics are inadmissible. A corrected version 5 runner has been prepared to independently replay each arm's dataset before training the baseline and the #1495+#1472 changed-file combination. Since #1472's exposed commit has no parent, the runner applies its exact controller change and test file instead of cherry-picking a full-tree snapshot. It has not been submitted while v4 is still running.

The runner installs ManiSkill in editable no-dependency mode and installs only the runtime packages this non-planning assay needs. The official PegInsertionSide demos and generated replay dataset are deleted before output packaging.

### Validity audit and correction

Before interpreting v4, an audit found that its runner replayed the raw demos
only once under the frozen base, then reused that converted dataset for both
arms. That is not a valid paired comparison for a change to action conversion.
No result from v4 is evidence for either PR. An earlier local audit used an
unpublished stale branch (`034e40c`) and incorrectly concluded the public PR
heads were sign-incompatible. The actual public #1495 head was `cdd6db7` and the
current PR branch now includes a runtime scale adapter; see
[the corrected action-sign audit](ACTION_SIGN_AUDIT.md).

A single seed supports a paired mechanistic comparison, not a statistically powered performance claim. Success-rate increments have 0.05 resolution at each 20-episode evaluation point.
