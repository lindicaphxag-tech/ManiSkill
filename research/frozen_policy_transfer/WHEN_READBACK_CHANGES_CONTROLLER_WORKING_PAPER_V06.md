# When Readback Changes the Controller: A Falsification-First Study of Stateful Action Transfer Under Unknown Execution

**Working paper v0.6 | 9 October 2026 | Zhibo Zhang, Hangzhou Dianzi University**

> **Research status:** Genuine author-run frozen-policy ManiSkill PhysX with publicly preserved original source, not a peer-reviewed or accepted robotics paper. The reported negative result explicitly supersedes any earlier claim that phase-based query timing improves raw task success over a correctly implemented fixed-read comparator.

## The one-sentence contribution

When a native accumulating controller's hidden target memory is revealed by a real authoritative read, **all control-branch decisions derived from the older multi-target belief must be invalidated**. Otherwise two methods that observe the same true target at the same time can dispatch different native commands and produce a spurious task-performance contrast.

## Why the effect matters

Two unknown execution acknowledgments leave up to four plausible previous commanded targets. A previous 64-state study found a task-phase querying controller appeared stronger than an always-read controller. The source-level audit discovered that the older always-read comparator did `belief.require_external_resync(actual)` at `t=4` but retained a stale pre-read `maybe_two=True` boolean for that same step. The proposed query algorithm correctly set `maybe_two=False`. The old two-arm comparison therefore tested **different action compilers after the same observation**, not just sensing timing.

## Fully preregistered new controlled falsifier

- Before implementing the new comparator or observing outcomes, [freeze commit `d664ec2`](https://github.com/lindicaphxag-tech/ManiSkill/commit/d664ec2fe4bb3a5d86ff4de3b1e7797c199f3037) locked two new reset-state cohorts: PullCube `970001–970032` and StackCube `980001–980032`, original fixed PPO checkpoints, two real PhysX native zero-arm-delta target holds at steps two and three, 0.05 m/0.05 rad setpoint budgets, a ten-arm matrix and the information-equivalence criterion.
- [PR #126](https://github.com/lindicaphxag-tech/ManiSkill/pull/126), **merged into the author-owned research repository only**, adds a corrected fixed comparator with exactly one local branch invalidation. The old buggy fixed comparator remains physically stepped for full transparent provenance.
- [Original eight green physical jobs and full-denominator source audit, run `37914020907`](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914020907), executed **640 genuinely separate native controller worlds** on **64 new paired source reset states**. Earlier failed CI attempts lacked frozen helper imports and remain public; no seed/task or numerical threshold was retuned after observing task performance.

| Treatment | PullCube | StackCube | Total official success | True target-state decision reads |
|---|---:|---:|---:|---:|
| Task-phase query | 32/32 | 24/32 | **56/64** | **56** |
| Corrected fixed early read | 32/32 | 24/32 | **56/64** | 64 |
| Legacy fixed read (cached post-read branch bug) | 32/32 | 21/32 | 53/64 | 64 |

**Key hard outcome:** all 32 StackCube source states produced **matching seven-dimensional actual native commands at every PhysX control step** between the task-phase and corrected fixed methods, within `1e-6` maximum per-element absolute error; both made the same true target read at `t=4`. Across all 64 reset states, these two methods had **zero discordant task outcomes**; this is descriptive exact finite-cohort agreement and **does not establish population noninferiority or equivalence**. The previous apparent three-success advantage was caused by the stale local software branch, not more intelligent information acquisition.

On PullCube, phase query skipped eight true controller-memory reads (24 instead of 32) while both treatments completed all 32 tasks. This reduction does not outperform the [precommitted simple task-ID route](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/REVIEWER_ONE_PAGE_K4_ACTION_AUTHORITY_20261009.md), which already achieved 58/64 outcomes using 56 getter calls on a different new cohort; **those different seeds must not be pooled as a causal comparison**.

## First-party/third-party evidence boundary

**Immutable original dataset:** [all eight source JSONs, eight complete PhysX logs, paired outcome audit and verified SHA-256 manifest](https://github.com/lindicaphxag-tech/ManiSkill/tree/main/research/frozen_policy_transfer/evidence/canonical_post_read_64_970001_980032). Both trusted-main original source archive jobs are [green](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914948951).

**Software regression:** the independently testable [versioned readback-memory authority](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/readback_belief_consistency.py) rejects stale epoch/sequence views after authoritative state reading or ACK changes. Its tests are [green on Windows, macOS and Linux × Python 3.11/3.13](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37914055085). This is standard versioned correctness engineering, not cryptographic sensor attestation.

**Adverse prior studies remain published:** the [older study's cached-branch confound and seeds 830004/830020](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/PHASE_QUERY_COMPARATOR_CONFOUND_CORRECTION.md), [the 64-trial strict private-read cap study with the PRE-FAULT SO(3) invalidity witness](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/STRICT_BUDGET16_NEW64_NEGATIVE_RESULT.md), and the [task-ID-only strong K=4 baseline](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/ORIGINAL_64_STRONG_QUERY_TIMING_BASELINE_AND_INVARIANT.md) are not deleted. In yet another new four-history motion-classifier study, public-only target-history identification accepted `0/32` conditions; this is a negative result against substituting low-confidence public motion for true controller-memory readback.

## Exact outside replication boundary

All raw original byte hashes can be verified without GPU, simulator or PPO weights using the complete original source, or the stand-alone reviewer script provided in the same conversation's self-contained 17-original-file evidence capsule. This check reproduces data integrity and arithmetic **only**. For a real independent experiment on new reset states, an outside research group must use an independent fork and frozen control code, exercise the actual controller with two native target holds, record all successes and failures, and publish a distinct new-source hash ledger.

ActionShift [Attri, 2026, DOI: 10.31224/7688](https://doi.org/10.31224/7688) already implements task-regret-aware active probing (DualABI) under hidden compositional action interfaces. Probe-action costs and privileged target-memory-getter counts are not interchangeable. This study does **not** prove general method superiority, a new minimax theorem, measured collision/contact safety, real packet-loss recovery, independent adoption, or any top-conference acceptance.

## The highest-impact next falsifier

Stop retuning phase thresholds on the already observed tasks. Perform a source-frozen, task/robot-disjoint comparison of (i) corrected fixed early read, (ii) preregistered task-ID-only policy, (iii) conditionally bounded common action, and (iv) adapted original ActionShift exact-belief/DualABI probe-and-query policies. All methods must share public observations, native action chart/limits, effective physical probe-step horizon and authority-read entitlements. Require cross-lab reexecution or an upstream project maintainer adopting a self-contained regression before labeling this an externally accepted robotics research artifact.
