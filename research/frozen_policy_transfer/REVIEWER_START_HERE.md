# Start here: executable reviewer package for latent execution ACK

**Unreviewed original simulation research**, 9 October 2026. This is not an accepted paper, learned VLA, original ManiSkill upstream merge, hardware safety certificate or outside-lab replication.

## Why this matters

Missing command acknowledgements create multiple possible previous **commanded native target histories** even with a known native action chart. The original source-frozen public-XYZ hypothesis adapter selects one entire plausible SE(3) controller target history when exactly one empirical public motion response is compatible; otherwise it pays for exactly one authoritative target read.

The stronger independently registered experiment uses **32 physically APPLIED / 32 physically HELD first t2 native commands**, the same held neutral t3 public probe, 64 new frozen third-party PPO manipulation resets and nine physically executed controller arms per state (**576 genuine ManiSkill PhysX worlds**).

| Method | Real task success | Privileged target reads |
| --- | ---: | ---: |
| Complete latent-history public XYZ identify-or-read | **58/64** | **31** |
| Strong precommitted task-ID fixed/selective query | **58/64** | **58** |
| True nine-world zero-read ALWAYS ASSUME HELD | **43/64** | **0** |
| Fixed t4 privileged read | 59/64 | 64 |

The public method had 33/64 uniquely identified history indexes (0 *observed* wrong confident against audit-only hidden target) and 31 counted fallback reads. Paired new-vs-strong task outcomes: 57 both won, 5 neither won, one each strategy uniquely won. In physical **APPLIED** StackCube first-ACK trials, public-or-read completed **15/16** vs the always-held shortcut only **1/16**. The read reduction is 27/58 = 46.6% relative to the task-aware strong comparator at the same aggregate task-success count, NOT a noninferiority or SOTA claim.

## Original source you can inspect before trusting any number

- [First original 10-job real PhysX execution + full independent audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37915263314).
- [17 original byte-identical JSONs, SHA256SUMS, full truth-stratified audit](./evidence/mixed_ack_truth_frozen_ppo_original64_860001_870032/).
- [Second successful ZIP-digest and full source archival verifier](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37916032672).
- [Before-new-outcome frozen protocol](../MIXED_ACK_TRUTH_PPO_NEW64_PREOUTCOME_V1.json), [physical method](../frozen_ppo_mixed_ack_truth_physx.py), [independent all64 auditor](../audit_mixed_ack_truth_new64.py) and [manuscript v1.5](./WHEN_DID_THE_COMMAND_EXECUTE_MANUSCRIPT_V1_5.md).
- [Earlier separate 32-task original negative](./evidence/public_fourhistory_frozen_ppo_original32_780001_790016/) (zero public labels and an information-cost loss) and [separate 64-task original ALL-HELD result](./evidence/discrete_hypothesis_ppo_original64_840001_850032/) (58/64; 39 vs 57 reads; susceptible to always-held shortcut).

## Actually run an independent new-seed test, with the original method unchanged

This reviewer program checks the exact approved mixed-ACK source Git blob 36e672446407435e656cbf8aba6fa2de7c1e9d0e. Select the first of eight consecutive truly unseen seeds (930001..999992) **before** looking at any outcome. The source reporter records operator, source SHA, actual physical t2 parity and all faults/failures. The released PPO checkpoints are frozen. In a Python 3.11 shell:

    git clone --branch research/mixed-ack-truth-frozenppo-new64-20261009 https://github.com/lindicaphxag-tech/ManiSkill.git
    cd ManiSkill
    python -m pip install -e . huggingface_hub
    PYTHONPATH="$PWD:$PWD/research" python research/outside_fork_mixed_ack_falsifier.py --task stack_cube --first-seed 930001 --output outside_mixed_ack_original
    (cd outside_mixed_ack_original && sha256sum *.json *.txt > SHA256SUMS)

[Optional external GitHub Actions source workflow](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/mixed-ack-truth-frozenppo-new64-20261009/.github/workflows/outside-fork-mixed-ack-physx.yml). **workflow_dispatch requires that the workflow be present on the fork's default branch.** Before that, use the direct command above or put only the reviewed workflow onto your fork's default branch. An author-owned CI run does not qualify as outside replication.

## Explicit scientific limitations

1. The true second fault outcome is HELD on every task. Only the first ACK truth is balanced. Four actual paired truth combinations remain untested.
2. The prior calibrated public response error model is empirical, not independently attested deterministic physics, and sees two public XYZ samples that the simplest private-read baselines do not consume.
3. There are two frozen PPO policies and one Panda native controller in one PhysX engine. Nothing here demonstrates actual lost network packets, SO(3) trajectory/force safety, camera-only VLA, independent robot transfer, or real laboratory validation.
4. Existing [ActionShift](https://github.com/Archerkattri/actionshift) and [ActionABI](https://github.com/Archerkattri/actionabi) already cover belief and active probes for unknown action interface semantics. The present result isolates *realized execution history* under a KNOWN native interface, not broad new active identification. A faithful matched-public-information probing comparator is still missing.
5. The same aggregate 58/64 task successes do not establish statistical noninferiority, and the fixed readback comparator achieved 59/64. Report this adverse observation too.

**Next promotion gate:** external investigator actually reruns unseen seeds in their own fork, reports every negative; followed by independent mixed first/second ACK physical truth, matched sensing/probe budgets, and a different robot/controller family.
