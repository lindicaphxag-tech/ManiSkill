# Contributor research: frozen-policy stateful action ABI transport

**This folder is maintained by the fork author and is NOT a ManiSkill upstream release or maintainer endorsement.**

[**Four-task flagship research / complete methods / limitations**](./STATEFUL_ACTION_ABI_FLAGSHIP.md) · [Public external replication challenge](https://github.com/lindicaphxag-tech/kaggle/issues/67) · [All nine permanent original PullCube+StackCube task JSONs](./evidence/pull_stack_new_task_64/) · [Original genuine 64-task-state CPU PhysX Actions](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37815152548)

## Reproduce the original *audit* (no simulator/GPU/downloads required)

Clone the **public** fork; from repository root, with Python standard library:

\`\`\`bash
cd research/frozen_policy_transfer/evidence/pull_stack_new_task_64
sha256sum -c SHA256SUMS
cd ../../../..
python -m research.action_abi_pull_stack_aggregate \
  --input-dir research/frozen_policy_transfer/evidence/pull_stack_new_task_64 \
  --output /tmp/frozen-policy-two-task-replay.json
python -m unittest discover -s tests -p test_action_abi_pull_stack_auditor.py -v
\`\`\`

These commands verify that all **nine source JSON bytes** are unchanged, recompute complete paired 64-state/5-arm outcomes, and run eight intentional negative controls for tampered or missing evidence. [Read-only CI repeats this on Python 3.10/3.12/3.13](../../.github/workflows/stateful-action-abi-flagship.yml).

## Reproduce the actual simulator
The above audit **does not rerun physics**. The genuine task source exists at pinned test commit \`9ffa86c6d3a86d2cee44b6e13c560033a8b373cf\` with \`research/frozen_ppo_target_memory.py\`. Follow [its exact original environment/policy source workflow](https://github.com/lindicaphxag-tech/ManiSkill/blob/9ffa86c6d3a86d2cee44b6e13c560033a8b373cf/.github/workflows/action-abi-pull-stack-replication.yml) and use \`ABI_TASK=pull_cube ABI_CHUNK=0\` etc. Four eight-seed chunks for **each** of PullCube and StackCube were preregistered; all eight original jobs completed. Any fresh-seed trial needs its own up-front protocol.

**Scientific limits:** Four frozen policies on four ManiSkill manipulation tasks but **one Panda controller-family chart mismatch**. Actual previous target memory is required by this *particular* action-ABI inverse. Bounded projection is NOT_EXACT. This is simulation, not hardware, risk-certified safety, independent execution or a new VLA model.
