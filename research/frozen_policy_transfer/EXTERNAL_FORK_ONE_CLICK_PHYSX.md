# Latest external replica: SELECTIVE READBACK real frozen-PPO PhysX (seven arms)

**This is the current primary fork-clickable original research replication.** It exercises seven *original unchanged* pretrained PPO/ManiSkill PhysX control arms, including **bounded correction / query only when the certificate fails**. It is **not** a simulation-free tally, research-independent evidence until another person's fork executes it, hardware safety, or real network packet loss.

[**Open the real seven-arm workflow**](https://github.com/lindicaphxag-tech/ManiSkill/actions/workflows/external-selective-query-physx.yml) · [**Merged implementation PR #84**](https://github.com/lindicaphxag-tech/ManiSkill/pull/84) · [**Completed author-operated real seven-arm test**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831105250) · [**Exact 64-state paired authority audit #85**](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/review/PAIRED_AUTHORITY_FRONTIER_64.md)

1. Fork `lindicaphxag-tech/ManiSkill` into your **own GitHub account**; enable Actions there.
2. In your fork's Actions, select **External one-click selective-query seven-arm genuine PhysX replication** → *Run workflow*. Choose task `pull_cube` or `stack_cube`. Choose eight **investigator-registered** consecutive seed IDs (for example first seed **250001**). Do **not** present original author-operated `pull_cube` 200001–200008 as a fresh seed-disjoint confirmatory sample; rerunning those is instead direct reproducibility.
3. The fork runner pins original method and certifier Git blob identity, downloads original third-party pretrained ActionShift PPO weights, runs real original CPU PhysX for every arm including failures, and publishes one SHA-stamped full original JSON plus method/source hash, package environment and `GITHUB_ACTOR` / `GITHUB_REPOSITORY`. The author-run full native demo **passed** but does not prove outside lab adoption.
4. Report all successes, failures, refusals and queries, and link the **actual run URL from your own fork**. If you find a counterexample or a model/dependency failure, include it rather than excluding the corresponding seed. The author has *not* verified independent outside reruns.

**Original best-supported finding:** [64 distinct *previously* held-out state seeds, two frozen policies](ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md) yielded 60/64 selective success using 15 trusted controller-target reads, versus mandatory 57/64 using 64 reads; exact paired 5-vs-2 McNemar *p*=0.453125 does **not** prove higher task success. Relative to zero-readback robust continuation, 60/64 vs 47/64 is a difference in **information use**, so not equal-information method superiority. Reader can independently check all eight original archived JSON SHA digests and stats in <1 min with stock Python using [the paired-audit tool](review/PAIRED_AUTHORITY_FRONTIER_64.md), but that is not a rerun of simulator physics.

---

## Previous separate six-arm applied-vs-held ACK-truth workflow (legacy)

The earlier material below describes **a different prior six-arm two-physical-truth experiment**; it is retained for reproducibility, but **does not test the current seven-arm selective-or-query candidate**, nor replace its original CI.

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
