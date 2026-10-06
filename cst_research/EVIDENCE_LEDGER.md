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
- Result at that stage: `40 passed in 1.07s`.
- CST now distinguishes offline trace convertibility from online chunk deployability.
- Query-time whole-chunk transport is classified `PRECOMPUTABLE` only when all source-goal and target-reference dependencies are available when the policy chunk is emitted.
- Future CURRENT_STATE or CONTROLLER_TARGET dependencies produce `REQUIRES_STEP_HOOK` for horizon > 1.
- A step-time adapter with the required state access yields `EXECUTABLE_WITH_STEP_HOOK`; missing controller-owned state yields `REFUSE_MISSING_RUNTIME_STATE`.

Novelty boundary: asynchronous action-chunk misalignment and stale-state execution are already studied by prior work. The candidate CST contribution is compiling reference-ownership information availability into an adapter-placement/refusal obligation during controller migration, not discovering action-chunk latency itself.

## Bounded cross-stack JIT migration evidence

- Validation run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37464317553
- Status: SUCCESS.
- Pinned LeRobot commit: `d40e8709cffb93644db66e30604ef50fdec003cb`.
- Source semantics: LeRobot-style CHUNK_ANCHOR relative actions.
- Target semantics: CURRENT_STATE-relative step-time actions.
- Relative offsets are bounded to uniform `[-0.2, 0.2]` on masked relative dimensions; non-relative dimensions remain absolute in `[-1,1]`.
- Frozen seed: `20261006`.
- 500 random chunks x batch 4 x horizon 9 = 2,000 trajectories / 18,000 action vectors.
- JIT max physical-goal error: `7.450580624679404e-09`.
- JIT mean per-trajectory max error: `1.5580290009071726e-09`.
- JIT p95 per-trajectory max error: `7.450580596923828e-09`.
- Naive tensor-copy mean per-trajectory max goal error: `0.5711112199053751`.
- Naive tensor-copy median per-trajectory max goal error: `0.554694190621376`.
- Naive tensor-copy p95 per-trajectory max goal error: `0.8517269160598515`.
- Naive tensor-copy global max goal error: `1.1520211696624756`.
- Temporally stacked-state current-frame parity error: `0.0`.

Interpretation: for bounded source-relative commands, the JIT adapter preserves the pinned second stack's physical goal trace to floating-point tolerance while direct numeric copying into a current-state-delta target systematically drifts. This is cross-stack executable-semantic validation, not maintained downstream adoption.

## LeRobot #3312 ACT external candidate

- External issue: `huggingface/lerobot#3312`, "Inference with ACT with relative action not working well".
- The issue is assigned to maintainer `pkooij`; the maintainer explicitly replied that relative actions were implemented for pi0/pi05 and invited an ACT PR.
- Current-main audit found the generic anchor-hold infrastructure already exists:
  - `RelativeActionsProcessorStep` holds a chunk anchor while the policy queue is non-empty;
  - `bind_relative_anchor(policy, preprocessor)` binds it to `count_queued_actions()`;
  - rollout/eval paths already call the binder.
- The remaining ACT-specific gap is narrow: `ACTConfig` has no relative-action fields and `make_act_pre_post_processors` still builds only the default normalize/unnormalize pipeline.
- Public upstream-candidate validation: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37467464140
- Validation method: CI clones official LeRobot at pinned commit `d40e8709cffb93644db66e30604ef50fdec003cb`, applies the candidate, installs that source, and runs the new regression together with official ACT processor tests.
- Result: `9 passed, 5 skipped in 0.88s`.
- Candidate scope: two production files (`configuration_act.py`, `processor_act.py`) plus one focused regression.
- Regression uses a real `ACTPolicy` queue and verifies:
  - default ACT processor layout is unchanged when the option is disabled;
  - relative conversion precedes normalization;
  - excluded gripper stays absolute;
  - the chunk-generation anchor is held while ACT's queue drains;
  - a fresh anchor is taken only after the queue becomes empty.

Interpretation: this is a maintainer-invited, current-main-valid upstream candidate. It is **not** an upstream PR or external adoption yet because no user LeRobot fork is currently available through the connected GitHub installation.

## Robomimic / Robosuite second-stack inverse semantics

- Full-suite run after the second-stack bridge: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37464762561
- Result at that stage: `53 passed in 2.18s`.
- External anchor: robomimic issue #270 explicitly requests absolute-action -> delta-action conversion; maintainer `amandlek` publicly stated they are happy to accept a PR for the functionality.
- Current robomimic delta->absolute converter drives the executable robosuite controller and reads `goal_pos/goal_ori`; the inverse prototype mirrors those semantics rather than using raw consecutive-action subtraction.
- Tested inverse obligations:
  - inverse affine controller action scaling;
  - SO(3) orientation inversion via group composition;
  - achieved-state vs previous-desired-goal reference modes;
  - explicit saturation / non-representability;
  - gripper / remainder preservation;
  - 2,000 randomized executable-goal round trips across achieved/desired modes.
- Upstream robomimic fork/PR: not yet created because the current GitHub integration cannot create a fork of that repository and cannot comment on the upstream issue (403).

Interpretation: this is a second independent public stack with executable-semantics validation, not robomimic adoption.

## Controller-rate contract

- Latest public full-suite run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37465617871
- Result: `59 passed in 1.30s`.
- CST now models integer controller-rate upsampling jointly with reference ownership under a declared zero-order-hold physical-goal contract.
- ABSOLUTE goals can be held directly.
- PREVIOUS_COMMAND deltas must be emitted once then zero-held; naively repeating a nonzero delta changes the physical goal.
- CURRENT_STATE / CONTROLLER_TARGET targets require target-rate runtime reference access and therefore a step hook.
- v0.1 intentionally refuses noninteger rate ratios rather than silently interpolating.

Novelty boundary: high-frequency action chunks, interpolation and asynchronous execution are established (e.g. RTR / RTC / A2C2). The candidate contribution is compiling controller-rate changes together with reference ownership into a precompute / step-hook / refusal obligation during frozen-policy controller migration.

## Real simulator evidence — current boundary

- Validation branch: `validation/joint-delta-closed-loop-assay`.
- Latest run with `render_backend="none"`: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37465118543
- The run now skips RenderSystem creation but still fails before controller execution because PickCube scene construction calls `sapien.render.RenderMaterial` and the hosted runner has no rendering device.
- This remains an infrastructure failure, not method evidence.
- Next assay should avoid task visual assets and test the actual controller/articulation path directly.

## Latest full research suite

- Public run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37465617871
- Result: `59 passed in 1.30s`.
- External maintainer adoption remains 0.
- L8 achieved: NO.
- L9 achieved: NO.

## Latest 75-test public suite and staged robomimic converter

- Full-suite run: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37471248763
- Result: `75 passed in 3.20s`.
- Workflow compiles the complete `cst_research` tree and runs every
  `test_*.py` file with NumPy, SciPy and pytest.
- The robomimic second-stack semantic core is therefore included in the same
  public regression suite as the ManiSkill / LeRobot CST components.
- Upstream-style candidate:
  `cst_research/upstream_candidates/robomimic/robosuite_add_delta_actions.py`.
- Candidate integration plan:
  `cst_research/upstream_candidates/robomimic/INTEGRATION_PLAN.md`.
- The candidate mirrors robomimic's existing delta->absolute converter and
  supports OSC scaling inversion, SO(3) left-composition inversion,
  robosuite <=1.4.1 and >=1.5 controller layouts, remainder preservation, and
  explicit saturation diagnostics.
- Direct attempt to post the implementation design to robomimic #270 through
  the connected GitHub integration returned HTTP 403
  `Resource not accessible by integration`.
- Upstream robomimic PR remains **not opened**; this is public preparation and
  reproducibility evidence, not adoption.

Current external adoption remains 0. L8 achieved: NO. L9 achieved: NO.
