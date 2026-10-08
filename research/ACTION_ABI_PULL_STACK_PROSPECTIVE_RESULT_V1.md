# Prospectively frozen two-new-task PPO controller transfer: PullCube + StackCube

**Outcome:** Both new task families passed the exact pre-run source-competence gate and matched live-memory vs state-blind bounded-action gain gate. Every planned original task state and five-arm result is retained. No trained weights, bounded-action method or source-to-target pose conversion was retuned on these new seeds.

## Protocol / complete evidence

- Frozen *before* modifying runnable task selectors: https://github.com/lindicaphxag-tech/ManiSkill/commit/582e39206cedf3565217514b1fdc1872c1cffae7
- Immutable protocol Git blob SHA-1: 721509118c490f2e9a5a87a6570922b7106bfbea
- Original official native PhysX CPU pipeline: https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37815152548 (8/8 new task jobs plus full audit SUCCESS).
- Two independently pretrained external ActionShift PPO checkpoints, independently checked SHA-256, pinned released HF repository revision 6bdeb28810330ab5425ccd629bb561c58a56ff85.
- New unseen PullCube seeds 51001–51032; new unseen StackCube seeds 61001–61032. All eight original 8-seed JSONs, no omitted seed; exact official task success flag up to 50 physical simulation actions per arm.

## Five actual closed-loop controller arms, 32 per task

| Experiment | Original source PPO | Naive direct-copy | Exact-only, may refuse | Memory-aware bounded target controller | Memory-blind, same bounded conversion |
|---|---:|---:|---:|---:|---:|
| PullCube (new checkpoint) | **31/32** | 14/32 | 17/32 | **31/32** | 14/32 |
| StackCube (new checkpoint) | **28/32** | 0/32 | 11/32 | **30/32** | 0/32 |

**PRIMARY PAIRED, precommitted +6 net minimum**:
- PullCube: **17 stateful-only** successes / **0 state-blind-only**. Net **+17/32**. Original-source competence 31/32 ≥24; primary mechanism gate PASSED.
- StackCube: **30 stateful-only** successes / **0 state-blind-only**. Net **+30/32**. Source competence 28/32 ≥24; primary mechanism gate PASSED.
- Two task families were analyzed separately using their *different* published checkpoint SHA and full 32-seed denominators. A combined total should not be treated as 64 independent trained policies or distinct robots.

**Exactness and refusal accounting:**
- PullCube exact-only refusals **14** episodes; projected converter used **15 NON_EXACT** bounded-control steps.
- StackCube exact-only refusals **20** episodes; projected converter used **33 NON_EXACT** bounded-control steps.
- State-blind control is NOT direct-copy. It uses the **same intended source physical goal, native rotation/translation conversion, controller action bounds and clipped projection**; only the previous commanded target pose is replaced by the achieved end-effector pose.
- Source success 28 and adapted success 30 on StackCube do not prove adapted policy is generally better than its own source. The tasks/solutions were evaluated as separate closed loops on equal physical reset seeds.

## Exact byte-level original artifact hashes

| Original JSON file | SHA-256 |
|---|---|
| abi_pull_stack_prospective_aggregate.json | e7c4984d10fcf4c521b874e5ac6d18e451f93d3899a831226f8abd23f2e0e57b |
| abi_independent_pull_cube_chunk_0.json | 64a788b0ff9f6d81ff7579eba38c0b4c181b7093387cf8181395e3cb42686c8d |
| abi_independent_pull_cube_chunk_1.json | 824e8f9d1193628a41ae4a130430df61f0ce714b6c70390a77738714e99f9ecc |
| abi_independent_pull_cube_chunk_2.json | 71f5a9450d3e6ec34c581f55edb667bd1477a0d8d4e59dbd5942b8f6c3a1ed07 |
| abi_independent_pull_cube_chunk_3.json | 8f001217f690c6aef1fba51e009677628e03142cca636d984cdc1938beb52c85 |
| abi_independent_stack_cube_chunk_0.json | 2063cf4fb108219fa482efd1deed05a23a4ce9664b1d4bf146cfd45d30b3ae90 |
| abi_independent_stack_cube_chunk_1.json | d36132e5cda9f2a16c4ec515402abc91796141f2b13f29a036903ea4275424fb |
| abi_independent_stack_cube_chunk_2.json | 2bcf5c820dc6681573e8e5384bb9bc75c115497edeea702c8734f353cb85cf01 |
| abi_independent_stack_cube_chunk_3.json | 8b63cc6f3149a84f8ab3a74ee8a4d431af69fb5355efd8a6a2bd5b5434cc2963 |

All source raw results belong to public workflow artifact **full-64-state-two-new-task-frozen-ppo-audit**. The original aggregate is the immutable data source, not rounded narrative values. If a Git permanent archive is later claimed, each of these SHA-256 values must match unchanged files in public main.

## Broader supported conclusion and vetoes

The earlier, separate frozen PPO tests yielded PickCube memory-aware 31/32 vs matched state-blind 4/32 on new 22001–22032 states, and the already-exposed PushCube memory-aware 29/32 vs matched state-blind 20/32 on 41001–41032. Four task families now consistently exhibit a benefit in this particular **same Panda controller-family** target-memory semantic mismatch, using four independently trained third-party PPO backbones.

**Do not claim:** a novel first-ever robot action adapter; any independent academic review; cross-robot/controller-family generalization; formal physical safety; exact preservation after non-exact projection; real-hardware deployment; zero-shot VLA generative modeling; third-party external reuse of the algorithm. External downstream adoption of the original compiler remains zero.

Next decisive originality tests require another maintained controller family, a non-convergent actuator or moving-base case, task trajectory/control deviation metrics (not success only), a competitive learned adapter with matched data/compute budgets, and independent third-party execution.