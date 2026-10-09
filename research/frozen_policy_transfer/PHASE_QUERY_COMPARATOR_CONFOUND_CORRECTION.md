# A necessary correction: equal controller observations do not imply equal executed control code

**9 October 2026 · research integrity notice · owner-operated simulator; not independently peer reviewed**

## What was previously measured

The prospective 64-reset-state, nine-controller-arm [phase-information run 37911547899](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37911547899) used unchanged released ActionShift PullCube and StackCube PPOs, two physical native target-hold substitutions at `t=2` and `t=3`, and distinct controller target-history hypotheses. A later [first-source-full audit run 37912403644](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37912403644) reported:

| Treatment | Actual official successes /64 | Privileged target reads |
|---|---:|---:|
| Task/phase-conditioned early private query | 56 | 58 |
| Old fixed t4 readback arm | 54 | 64 |
| Previously frozen task-ID route | 53 | 57 |
| Naive authority-slack early query | 55 | 63 |
| Reactive query only on geometry certificate refusal | 44 | 45 |

Paired phase versus prior task-only: 3 phase-only successes / 0 task-only-only (exploratory paired `p=.25`). Those observations **do not prove a new algorithm is better**.

## Hidden implementation confound

At `t=4`, the old `fault_always_single_privileged_query` comparator:

```python
maybe_two = len(belief.hypotheses) > 1
true_target = privileged_target(arm)
belief.require_external_resync(true_target)  # hypothesis set becomes singleton
# but local 'maybe_two' STILL remains True in this control step
if maybe_two:
    command = compile_common_action(belief.hypotheses, target)
else:
    command = invert_true_singleton_memory(target, true_target)
```

The task-conditioned `fault_phase_value_query` arm performs the **same authoritative read** on StackCube at step four but executes `maybe_two=False` after resynchronizing. Therefore the two treatments can take **different native physical actions with the same true target observation**, invalidating any assertion that the original result isolates query timing or scheduling.

The independent audit explicitly names **StackCube seed 830004 and 830020** as cases where the two controls had the same read count but different binary task outcomes. The problem is not a new POMDP theorem; it is a cached-branch invalidation bug with immediate causal consequences in a stateful controller. Note that the controller belief resets its `epoch` on every authoritative resync. Using an epoch-versioned action-dispatch handle protects against this class of mismatch.

## Transparent correction in code

Standalone CPU contract: [readback_belief_consistency.py](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/readback_belief_consistency.py); tests: [test_readback_belief_consistency.py](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/tests/test_readback_belief_consistency.py). These tests refuse commands derived from stale belief epochs, including after two missed command ACKs create four possible target histories.

The proper experiment must not silently patch the old arm in the already-observed run. Instead, **before any new native physics outcomes**, a separate protocol was committed: [d664ec2 / explicit preregistration](https://github.com/lindicaphxag-tech/ManiSkill/commit/d664ec2fe4bb3a5d86ff4de3b1e7797c199f3037). It retains the exact old fixed arm AND adds a **tenth physically stepped corrected fixed arm**. On 64 new PullCube seeds `970001–970032` and StackCube seeds `980001–980032`, every group of eight is executed with the same frozen PPO/control bounds and both native target-hold faults. The corrected comparator has exactly one surgical change: after authoritative target-state read, clear the current-step cached multi-history branch. Raw native action traces are saved for fixed, corrected fixed and phase arms.

**Hard, preregistered falsifier:** on StackCube, both phase query and corrected fixed read at the **same step four** and use the same single actual previous target; therefore all corresponding native dispatched actions should agree to numerical tolerance `1e-6` and task success/read counts should match on the same source reset states. If not, the scientific gate FAILS. PullCube comparisons are analyzed separately. The original 830004/830020 historical failures remain public and are not folded into the new prospective holdout.

[Ten-arm genuinely independent native PhysX source CI / author-controlled](https://github.com/lindicaphxag-tech/ManiSkill/pull/126) · [dedicated original 64-state action-trace auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/canonical-post-read-abi-new64-20261009/research/audit_canonical_post_read_fresh64.py).

## What cannot be concluded

This correctness bug means an apparent phase-query advantage could be **control-path semantics rather than information acquisition**. Existing data cannot establish benefit over an information-identical corrected fixed arm. The prior experiment and its original source remain as observed, including failures; a new-source prospective rerun is required.

ActionShift DualABI already contains task-regret-aware active probes and hard masks, so active sensing itself is established prior art. Its probe steps are a distinct cost from private controller memory reads. No equality of privilege, real network-loss recovery, collision/contact safety, cross-embodiment generalization, third-party reproducibility or upstream accepted paper is claimed here.
