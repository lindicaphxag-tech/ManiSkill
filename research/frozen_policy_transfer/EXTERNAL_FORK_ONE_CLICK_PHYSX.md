# Reproduce frozen PPO unknown-ACK PhysX faults in your own GitHub Actions

This is a real frozen-policy ManiSkill PhysX simulator rerun, **not an offline re-aggregation**. The one-click entry lives in [the workflow](../../.github/workflows/external-ack-frozen-ppo-replication.yml).

## How to run

1. **Fork** https://github.com/lindicaphxag-tech/ManiSkill and enable Actions in YOUR fork.
2. Go to Actions > **External one-click genuine PhysX ACK-fault frozen PPO replication** > **Run workflow**.
3. Choose task **pull_cube** or **stack_cube**, then a fault: **applied_no_ack** (arm command was actually applied) or **neutral_arm_delta_no_ack** (arm receives zero native delta instead, gripper unchanged).
4. Choose a first task seed at or above **120001**. Manual mode runs exactly eight consecutive seeds (suggestion **130001**, but select and freeze your own NEW interval *before* viewing outcome).
5. Download the resulting artifact with complete original six-controller PhysX JSON, all failures, stdout, source commit, installed Python packages, model hash and SHA256SUMS.

To test BOTH physical fault truths on paired task states, launch two runs with the **same fresh task-seed range**. To test both frozen third-party PPOs, execute all four task/fault choices. Do not pool repeated seeds as independent pretrained policies.

## Local equivalent

From the ManiSkill repository root, with the project's normal PhysX CPU runtime and huggingface_hub installed:

```bash
python research/external_ack_replication.py --task stack_cube \
  --fault applied_no_ack --first-seed 130001 --count 8 \
  --output-dir replication_artifacts
```

Original method: [frozen PPO unknown-ACK recovery](../../frozen_ppo_unknown_ack_recovery.py). Original [32 trial-condition prospective pre-outcome experiment](UNKNOWN_ACK_PROSPECTIVE_32_REVIEWER_PACKET.md) and [byte-for-byte permanent raw archive](evidence/unknown_ack_prospective_32_94001_95008/) are separate. Investigator-selected follow-up seeds have an **explicit NEW schema** and are **NOT original preregistered evidence**.

## What the six controls actually disclose

- **Source PPO:** original native achieved-relative controller, no intentional ACK fault.
- **Privileged oracle:** continuously reads controller target memory (not equal-information control).
- **One-read recovery:** privileged controller target-state read exactly once immediately after unknown ACK and then a history observer.
- **Optimistic:** assume requested arm action applied; zero private target reads.
- **Pessimistic:** assume requested arm action was not applied; zero private target reads.
- **Fail-stop:** refuse to issue further control after unknown ACK.

The one-read method has an **additional information advantage** over optimistic/pessimistic. All official success values are simulator task flags, **not verified actuator-force, collision, contact or hardware safety**. Real network drop/reorder/latency is NOT implemented; a neutral delivered native arm delta in real PhysX approximates one branch of that protocol uncertainty.

If a fresh task finishes before the planned fault, **the fault did not occur**. Do not quietly exclude its seed or call it a recovery success. The validation reports failures rather than removing them.

## Original checkpoint and competing baseline credit

The frozen third-party PPO weights are openly released as [ActionShift baseline checkpoints](https://huggingface.co/kattri15/actionshift-baselines), associated with [Archerkattri/actionshift](https://github.com/Archerkattri/actionshift), which **already** implements a broader online hidden-action-interface benchmark (including active probes, belief adapters, action delay, PPO and Diffusion Policy). The PPO weights and the broad idea of adapting hidden action contracts are **not original to this repository**. This fork's narrower empirical question concerns **applied-vs-omitted command truth when action acknowledgement is untrustworthy**, target-history observability and the cost of a trusted readback. Meaningful new claims must be compared against ActionShift's belief/probe methods under the same fault cases and an equal information / online compute budget. This one-click reproduction does NOT by itself perform that independent head-to-head comparison.

## External-falsification request

An outside researcher can share THEIR run + unmodified JSON and the exact checked-out commit in the [open independent reproduction challenge](https://github.com/lindicaphxag-tech/kaggle/issues/67). Outside researchers' **negative** results are as scientifically valuable as successful ones. Forking alone or an author-owned Actions run does NOT constitute independent scientific replication.

Most valuable follow-up: mask target-memory telemetry altogether and recover state from a physical observation/proprioception stream under real action-latency uncertainty, comparing active probes and state estimators under an equal information/actuation/time budget and using a truly independent controller implementation.
