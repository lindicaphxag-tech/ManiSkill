# Contributor research: frozen-policy stateful action ABI transport

**This folder is maintained by the fork author and is NOT a ManiSkill upstream release or maintainer endorsement.**

[**Four-task flagship research / complete methods / limitations**](./STATEFUL_ACTION_ABI_FLAGSHIP.md) · [Public external replication challenge](https://github.com/lindicaphxag-tech/kaggle/issues/67) · [All nine permanent original PullCube+StackCube task JSONs](./evidence/pull_stack_new_task_64/) · [Original genuine 64-task-state CPU PhysX Actions](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37815152548)

## New observer extension: no per-action private target getter

[**Original 16-seed preregistered results and all 16 episode records**](./ACTION_HISTORY_OBSERVER_PROSPECTIVE_16.md) · [Five-job successful true PhysX/contract CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37819111802) · [Source and observer](../action_abi_history_observer.py) · [Read-only target observer tests](../../tests/test_action_abi_history_observer.py).

An action-history observer tracks the last *commanded* target from the reset achieved end-effector pose and **acknowledged issued actions**, without reading the target controller's private state during policy decision making. On **16 never-before-tested** PullCube/StackCube task states, its genuine frozen PPO success outcomes matched live-target-memory conversion **13/16** (Pull 6/8, Stack 7/8), versus memory-blind bounded conversion **5/16**. Final target-estimate errors were at most 2.39e-8 m and 6.51e-7 rad; **12** steps were bounded **NOT_EXACT** projections. Unknown action execution triggers fail-closed refusal/resynchronization, not continued speculative control.

These results are one owner-executed PhysX run on the **same Panda controller ABI**, not independent validation, safety certification, or hardware deployment.

## Reproduce the original *audit* (no simulator/GPU/downloads required)

Clone the **public** fork; from repository root, with Python standard library:

```bash
cd research/frozen_policy_transfer/evidence/pull_stack_new_task_64
sha256sum -c SHA256SUMS
cd ../../../..
python -m research.action_abi_pull_stack_aggregate \
  --input-dir research/frozen_policy_transfer/evidence/pull_stack_new_task_64 \
  --output /tmp/frozen-policy-two-task-replay.json
python -m unittest discover -s tests -p test_action_abi_pull_stack_auditor.py -v
```

These commands verify that all **nine source JSON bytes** are unchanged, recompute complete paired 64-state/5-arm outcomes, and run eight intentional negative controls for tampered or missing evidence. [Read-only CI repeats this on Python 3.10/3.12/3.13](../../.github/workflows/stateful-action-abi-flagship.yml).

## Reproduce the actual simulator
The above audit **does not rerun physics**. The genuine task source exists at pinned test commit `9ffa86c6d3a86d2cee44b6e13c560033a8b373cf` with `research/frozen_ppo_target_memory.py`. Follow [its exact original environment/policy source workflow](https://github.com/lindicaphxag-tech/ManiSkill/blob/9ffa86c6d3a86d2cee44b6e13c560033a8b373cf/.github/workflows/action-abi-pull-stack-replication.yml) and use `ABI_TASK=pull_cube ABI_CHUNK=0` etc. Four eight-seed chunks for **each** of PullCube and StackCube were preregistered; all eight original jobs completed. Any fresh-seed trial needs its own up-front protocol.

**Scientific limits:** Four frozen policies on four ManiSkill manipulation tasks but **one Panda controller-family chart mismatch**. Previous target memory is required by this *particular* inverse map, but can now be reconstructed under documented deterministic controller-update and confirmed-action assumptions. Bounded projection is NOT_EXACT. This is simulation, not hardware, risk-certified safety, independent execution or a new VLA model.
