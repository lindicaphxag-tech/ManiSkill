# CST Evidence Ledger

Last updated: 2026-10-06.

This ledger separates implemented, publicly validated, externally reviewed, and adopted claims. A green run in the author's fork is reproducibility evidence, not external adoption.

## External problem anchor

- ManiSkill issue #429: https://github.com/mani-skill/ManiSkill/issues/429
- Maintainer statement: fully accurate action-space conversion is highly non-trivial and potentially publication-worthy.
- Technical diagnosis comment from this work: https://github.com/mani-skill/ManiSkill/issues/429#issuecomment-6015654790
- Maintainer response to that diagnosis: pending.

## Minimal upstream candidate

- PR-ready branch: `fix/joint-delta-to-joint-pos-pr`.
- Diff: exactly two files, two commits.
- Production change: `mani_skill/trajectory/utils/actions/conversion.py`.
- Regression: `tests/test_pd_joint_delta_to_pos_regression.py`.
- No CST research modules or temporary CI files are included in the PR-ready diff.

## Public base-fail / fix-pass evidence

- Validation run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37459621516
- Status: SUCCESS.
- Same regression on baseline: FAIL.
- Baseline failure: NumPy action reaches Torch-only `clip_and_scale_action` and raises `TypeError`.
- Same regression on proposed fix: PASS (`1 passed`).

Interpretation: this establishes a concrete source/runtime contract bug and verifies the focused correction against the identical regression. It does not yet establish task-level trajectory recovery.

## CST research-core evidence

- Public research branch: `research/closed-loop-semantic-transport-v1`.
- Full-suite run after reference-semantics extension: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37461105932
- Result: `32 passed in 0.60s`.

Current tested components:
- local closed-loop EXACT / APPROXIMATE / IMPOSSIBLE classification;
- minimum-norm stateful adapter synthesis;
- constructive unmatched physical-direction witness;
- finite-horizon local error bound;
- regional shared-adapter consistency;
- finite-pool counterexample-guided synthesis;
- different-dimensional controller-state handshake;
- ManiSkill joint-position executable contract compiler;
- 3,600 randomized absolute / delta-current / delta-target migrations;
- runtime implementation-to-contract extraction;
- reference ownership: absolute / current-state / chunk-anchor / previous-command / controller-target semantics;
- masked dimensions such as absolute gripper + relative arm.

## Real simulator evidence

- Validation branch: `validation/joint-delta-closed-loop-assay`.
- Assay: PickCube-v1, Panda, PhysX CPU, source `pd_joint_delta_pos`, target `pd_joint_pos`.
- First run failed before controller execution because hosted runner had no usable Vulkan device.
- Second run with `render_backend=none` still failed during RenderMaterial construction before controller execution.
- Current run installs Mesa software Vulkan and is PENDING.

Do not count the first two failures as method failures: no controller action was executed.

## External adoption status

- Maintainer review of #429 diagnosis: 0 as of this ledger update.
- Upstream PR for #429: not opened yet; contribution guide asks for maintainer thumbs-up first.
- Maintained external adoption of CST research method: 0.
- L8 achieved: NO.
- L9 achieved: NO.

## Claim upgrade gates

To move from L8-candidate to strong L8 evidence:
1. real simulator or real trajectory base-vs-fix behavior;
2. maintainer technical approval / PR review / merge;
3. second independent stack.

To argue L9-level external recognition:
- maintained external use or merge of the research method, independent reproduction, or strong peer-reviewed recognition in addition to the above.

## Independent-stack reference-semantics parity

- Validation run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37461922475
- Pinned LeRobot commit: `d40e8709cffb93644db66e30604ef50fdec003cb`.
- The assay executes the actual pinned-source `to_relative_actions` and `to_absolute_actions` function definitions and compares them with CST's CHUNK_ANCHOR semantics.
- Random chunks: 500.
- Batch per chunk: 4.
- Horizon: 9.
- Dimension: 7.
- Checked trajectories: 2,000.
- Checked action vectors: 18,000.
- Max CST-vs-LeRobot goal error: `1.4901161193847656e-07`.
- Max CST-vs-LeRobot absolute-action error: `1.4901161193847656e-07`.
- Temporally stacked-state current-frame parity error: `0.0`.
- Same numeric [1,2,3] under CHUNK_ANCHOR vs PREVIOUS_COMMAND has maximum goal divergence `3.0` in the frozen witness.

Interpretation: this is independent public-stack semantic parity, not LeRobot adoption of CST. It supports the claim that reference ownership is executable semantics and that CST can reproduce a real second stack's chunk-anchor contract.


## Causal deployability evidence

- Full-suite run after causality layer: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37463347917
- Result: `40 passed in 1.07s`.
- CST now distinguishes offline trace convertibility from online chunk deployability.
- Query-time whole-chunk transport is classified `PRECOMPUTABLE` only when all source-goal and target-reference dependencies are available when the policy chunk is emitted.
- Future CURRENT_STATE or CONTROLLER_TARGET dependencies produce `REQUIRES_STEP_HOOK` for horizon > 1.
- A step-time adapter with the required state access yields `EXECUTABLE_WITH_STEP_HOOK`; missing controller-owned state yields `REFUSE_MISSING_RUNTIME_STATE`.

Novelty boundary: asynchronous action-chunk misalignment and stale-state execution are already studied by prior work. The candidate CST contribution is compiling reference-ownership information availability into an adapter-placement/refusal obligation during controller migration, not discovering action-chunk latency itself.
