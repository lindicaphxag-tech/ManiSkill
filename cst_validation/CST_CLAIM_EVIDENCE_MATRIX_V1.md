# CST claim-evidence matrix v1

This is a fail-closed research contract. Negative and missing evidence remain visible rather than being rewritten after experiments.

| ID | Claim | Status | Evidence |
|---|---|---|---|
| C1 | Native action tensors are insufficient to define controller-independent semantics when controller reference state differs. | **supported by construction/tests** | JointGoalChart distinguishes absolute, current-relative, and target-relative semantics; ambiguity witnesses are tested. |
| C2 | E1 exact transport exists when source semantics are identifiable and the semantic goal lies in the target chart image. | **supported for joint charts** | compiler plus exact/ambiguous/nonrepresentable tests; independent round-trip residual gate. |
| C3 | The current ManiSkill pd_joint_delta_pos -> pd_joint_pos path contains a native/physical chart mismatch. | **supported by focused regression** | upstream-ready branch decodes normalized source delta to physical delta, forms physical q_goal, then re-encodes in target chart; focused Actions run 37392694506 is green. |
| C4 | On four official ManiSkill motion-planning datasets, delta-target one-step semantic reachability is complete under +/-0.1 rad bounds. | **supported on frozen public data** | 4 tasks, 4,000 trajectories, 519,006 actions; 100.000000% one-step exact. |
| C5 | On the same data, delta-current has a strictly smaller one-step semantic image because the reference is measured q_current. | **supported on frozen public data** | 517,807/519,006 exact (99.768981%); 1,199 actions need H_min=2. |
| C6 | Delta-current sequence semantics require per-step q_current, whereas delta-target can be recursively decoded from initial q_target plus actions. | **supported on frozen public data** | run 37393395020: 4000/4000 delta-current action-only sequences refused; with q_current trace 3751/4000 are fully exact because remaining failures are target-image violations. Delta-target: 4000/4000 exact from one initial q_target, max goal/reference residual 0. |
| C7 | Exact CST results can be independently re-verified and are invalidated by chart/context/payload drift. | **supported in method core** | proof-carrying record plus verifier; stale context, chart drift and tampering tests pass in the green semantic-core gate. |
| C8 | CST preserves realized simulator trajectories (E3) for the ManiSkill #429 conversion. | **unproven** | hosted runner cannot instantiate SAPIEN renderer; Lavapipe fails before conversion execution. No E3 claim. |
| C9 | CST restores task success for issue #429 (E4). | **unproven** | requires real ManiSkill simulation on a Vulkan-capable runner. |
| C10 | CST has maintained external adoption. | **false currently** | ManiSkill issue #429 is external and maintainer-recognized, but no CST patch is merged. |
| C11 | CST generalizes to a second ecosystem. | **pending** | robomimic #270 explicitly welcomes absolute->delta functionality; no upstream implementation/adoption claimed yet. |

## Current paper-safe headline

Controller-native actions are charts over physical command semantics, not interchangeable tensors. CST compiles source actions through an explicit physical goal, proves source identifiability and target representability, emits constructive refusal witnesses, and records the controller state needed for lossless offline conversion.

## Do not currently claim

CST does not yet solve arbitrary controller conversion, prove 100% realized trajectory equivalence, prove 100% task-success recovery, prove safe deployment, or have maintained external adoption.

## Promotion gates

C8 requires a Vulkan-capable simulator run with matched initial state and per-step target/realized trace reporting. C9 requires task-level replay on issue-relevant trajectories. C10 requires code or contract retained by an external maintained repository. C11 requires an independently maintained second stack, not a second fork owned by the author.
