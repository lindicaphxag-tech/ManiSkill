# Public, independently checkable flagship evidence — 2026-10-13

**Status ledger, not an admissions endorsement or invented research ranking.** This public GitHub file exists because the comprehensive private account repository is not accessible to outside faculty/maintainers without permission. It links only to publicly verifiable source, upstream PRs, full workflow runs and counterexamples. L8/L9/L10 are optional personal planning labels, not official levels.

## Externally merged upstream code (verified separately from open PRs)

GitHub search for **merged external PRs authored by `lindicaphxag-tech`, excluding own repositories** returned **28** on 2026-10-13. Verify individual records rather than trusting the number:

- [Braindecode #1200, EEG-CLIP dual-encoder integration — merged](https://github.com/braindecode/braindecode/pull/1200).
- [Braindecode #1218, NeuroRVQ pretrained electrode identity — merged](https://github.com/braindecode/braindecode/pull/1218).
- [Braindecode #1223, NeuroRVQTokenizer residual implementation — merged](https://github.com/braindecode/braindecode/pull/1223).
- [Braindecode #1319, correct cold-start distributed EMA — merged](https://github.com/braindecode/braindecode/pull/1319).
- [MOABB #1207, splitters — merged](https://github.com/NeuroTechX/moabb/pull/1207); [#1208, statistical critical-difference visualization — merged](https://github.com/NeuroTechX/moabb/pull/1208).
- [Ray/RLlib #66198, DQN exploration device correctness — merged](https://github.com/ray-project/ray/pull/66198).

A merged implementation does **not** imply that it is the first published mathematical algorithm.

## Still awaiting external Merge (do not count them)

- [Braindecode #1320 global-negative distributed EEG-CLIP](https://github.com/braindecode/braindecode/pull/1320): authentic unequal-rank actual DDP centralized gradient equivalence, and a new **synchronized global shape/emptiness preflight** on both ranks. [3-OS CPU/Gloo preflight CI](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38337406542) 3/3 success, 5 focused tests per runner. Latest official head `d943a585c3a51c0cf8a48fe5d135d615ab07b949` has [style](https://github.com/braindecode/braindecode/actions/runs/38338357034), [docs](https://github.com/braindecode/braindecode/actions/runs/38338357027), and What's New green; [official full tests](https://github.com/braindecode/braindecode/actions/runs/38338357056) must be checked for final completion; maintainer Approval/Merge pending.
- [MOABB #1235](https://github.com/NeuroTechX/moabb/pull/1235): opt-in **raw epoch extraction-window overlap** protection. It is not a certificate of absence of long-tail filtering dependence; API adoption pending.
- [ManiSkill #1495](https://github.com/mani-skill/ManiSkill/pull/1495): source converter semantics, native-controller behavioral assessment includes negative cases; open.
- [JAX #41227](https://github.com/jax-ml/jax/pull/41227), [#41228](https://github.com/jax-ml/jax/pull/41228): numerically stable distribution edge cases; upstream review and re-review pending.
- [Ray #66641](https://github.com/ray-project/ray/pull/66641): EnvRunnerGroup regression; open.
- [Transformers #49483 issue](https://github.com/huggingface/transformers/issues/49483): identified by **another contributor** (@LE0-Lin) who has publicly claimed the fix. A separate [fork CPU reproduction/candidate branch](https://github.com/lindicaphxag-tech/transformers/tree/fix/chunked-prefill-cached-prefix-20261013) passed [7 tiny Llama unit tests](https://github.com/lindicaphxag-tech/transformers/actions/runs/38338368467), but creating a duplicate official PR failed 403 and should not bypass original author ownership.

## Research / algorithms: experiments you can actually inspect

### True public EEG source and filter-leakage mechanism

- [Prospectively specified original PhysioNet EEGBCI study](https://github.com/lindicaphxag-tech/moabb/blob/research/physionet-edf-fold-filter-20261013/research/PHYSIONET_EDF_FOLD_FILTER_PREREG_20261013.json): four independent participants, two original EDF runs each, two channels, four registered guard lengths => 64 paired observation conditions; fixed fourth-order Butterworth 1–30 Hz SOS zero-phase filtering over entire original recording.
- [Original real EDF study: SUCCESS](https://github.com/lindicaphxag-tech/moabb/actions/runs/38336887369), eight EDFs with file SHA256 fingerprint. Synthetic polarity-flip intervention in held-out source interval (not naturally occurring clinical artifact or label leakage). Median relative training-window L2 transfer gains: 0/80/320/640 sample gaps = **0.0660861 / 0.0138181 / 0.000423804 / 0.00000426660**. Every raw train/test window was disjoint; same heldout samples masked before filtering eliminated every induced difference.
- [Completely separate fresh-EDF re-download and independent linear `F(delta)` audit: SUCCESS](https://github.com/lindicaphxag-tech/moabb/actions/runs/38337809594), original 8 EDF hashes and **64/64** stored condition results verified. This proves code-level numerical consistency, not a separately recruited biomedical subject cohort.
- [Synthetic SOS spectral-vs-Frobenius guard 6-platform CI](https://github.com/lindicaphxag-tech/moabb/actions/runs/38335270570): in its fixed toy example, a numerical induced L2 spectral bound selected 640 raw guard samples versus 800 for conservative Frobenius. Standard linear algebra, not a new mathematical theorem; **no classifier performance gain yet**.

### True robot state / hidden-ACK behavior, including the essential NEGATIVE originality test

- [Native PhysX 160-world original task-target restoration comparison](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38331837905), 8 original independent robot reset clusters (Panda/xArm6), [full independent audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38332443094).
- [Frozen fresh-seed 128-world public observation policy](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38332965278) with [independent decision-level audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38333385887): source-goal-centering public XYZ history prediction **16/16 per robot** compared with raw XYZ **6/16 per robot**, sub-millimeter end-effector target restoration. **But** this controller's constant root-translation chart makes source-goal centering mathematically equivalent to conventional reset-centering. Not proven original algorithm advantage, no PickCube completion gain.
- [Original 64-train + 320 completely new-test real PhysX SO(3) comparison](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335458988) and [independent full-source audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38335861213). Both source-hypothesis and appropriately variant-matched reset-relative SO(3) classifier: **32/32 per robot, precisely identical target-restoration error**. Precommitted novelty win gate **FAILED 0/4 reset clusters per robot**, and official PickCube success zero. [Read the original complete negative report](research/frozen_policy_transfer/TWO_ACK_SO3_STRONG_BASELINE_NEGATIVE_20261013.md).
- Therefore, **do not** claim novel SO(3) geometry recovery superiority, robot hardware safety certification, general VLA task success or independent external lab replication.

## Why this constitutes a coherent portfolio but not yet three fully accepted research flagships

Recurring invariant: correct *state and semantic provenance* under execution: (i) EEG raw-test influence despite disjoint signal windows; (ii) DDP paired-row semantics before collectives; (iii) controller target history and ACK uncertainty. This is a useful research direction, not evidence that one new universal theorem spans all three.

**Completed:** real upstream code acceptance history, meaningful correctness proofs with CI, real public data/source evidence, real CPU PhysX controller tests, preregistered negative comparisons, and independent programmatic replication.

**Not completed:** accepted upstream #1320, new MOABB guard utility upstream adoption, EEG classifier decision/accuracy impact in multi-dataset holdout, robot task-level gains over fully command-aware Bayesian/system-ID baselines, external publication/reviewer agreement or academic claim of priority.

**Next gates in priority order:** (1) one new upstream merged flagship-level contribution; (2) preregistered true downstream EEG model or embodied full-task gain beyond strong baselines, including negative cases; (3) external maintainer or independent researcher uses/reviews the method. Do not convert unmerged PRs or self-run CI into external recognition.


## October 13 cross-domain expansion: independent tests and originality barriers

### Engineering evidence: a previously missed nonempty-global, empty-local DDP bug

1. The [official upstream Braindecode #1320](https://github.com/braindecode/braindecode/pull/1320) on head `d943a585` passed exact-head upstream full tests, acceptance, pre-commit/style, documentation and What's New. It is **OPEN without a maintainer Approval**; do not count a new Merge.
2. The fork's initial [synchronized-invalid-rank test](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38337406542) truly passed 3/3 OS, but the **subsequently authored 0-pair local rank / 5-pair remote rank test was not selected by the first `-k` filter**. The corrected [0+5 test run](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38340869281) exposed a **real failure** in `EEGCLIP.forward()`: `reshape(0,-1,D)` cannot infer the middle dimension of an empty EEG local minibatch. It is NOT legitimate to claim the earlier green test covered this.
3. The [narrow exploratory patch](https://github.com/lindicaphxag-tech/braindecode/tree/research/eegclip-global-ack-preflight-20261013) changes the projected EEG reshape to use the explicit `features.shape[-1]` temporal dimension. [Current three-OS real 0+5 DDP test](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38341326398): verify the final matrix before claiming full cross-platform success. The 0+5 result is NOT yet promoted into official PR #1320, preventing an untested late change.
4. The engineering novelty at stake is the **EEGCLIP-specific production correctness contract** and real distributed gradient equivalence. DDP, CLIP global negatives, rank preflight and zero-batch fundamentals are established prior art; this is not a new mathematical or neuroscience method.

### Scientific evaluation: 4 pilot participants and 20 fully unseen real subjects

- [Original PhysioNet signal-level audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38337809594) passed independent re-download/recompute for all 64 of the original **real EDF 4-subject** filter-dependence pairs.
- [Prospectively frozen event-labelled classifier design](https://github.com/lindicaphxag-tech/moabb/blob/research/physionet-eeg-decoder-dependence-20261013/research/PHYSIONET_EEG_DECODER_CONTRACT_PREREG_20261013.json) fixes C3/C4 log bandpower, T1/T2 motor-imagery event labels, a chronological last-third heldout fold in each run, and scikit-learn scaled logistic regression. The intervention **flips raw samples solely in test-event crops** before whole-record IIR filtering, keeping clean heldout evaluation features and the train labels untouched. Its endpoints measure downstream heldout probability drift, class-prediction flips and *diagnostic* accuracy change; these are not natural artifact rates, label leakage or clinical accuracy gains.
- [Eight original EDF classifier protocol runs](https://github.com/lindicaphxag-tech/moabb/actions/runs/38341234033), four original participants; results must be inspected before claiming success or an effect.
- [Independently pre-registered 20 **new** participants S005–S024](https://github.com/lindicaphxag-tech/moabb/blob/research/physionet-eeg-decoder-20-unseen-20261013/research/PHYSIONET_20_NEW_SUBJECTS_DECODER_PREREG_20261013.json) on the **immutable original program blob `67977ba9...`**, with two untouched EDF runs per person across four five-subject CI shards: [full study run](https://github.com/lindicaphxag-tech/moabb/actions/runs/38341544307). This is a prospective broader measurement attempt; raw outcomes, effect and retained complete denominator are not reported as success until the workers finish.
- No comparisons across 40 runs or hundreds of epochs should be interpreted as **40 independent patients**. Person-cluster summary is the only independent observed subject unit here.

### Adjacent science scope and external strong baselines

- [LeRobot async inference documentation](https://huggingface.co/docs/lerobot/async) expressly distinguishes planned action chunks, execution and async continuation. [ICLR 2026 REMAC](https://proceedings.iclr.cc/paper_files/paper/2026/hash/c35834443b7881e782e52b3519fe27c7-Abstract-Conference.html) already studies execution/perception chunk misalignment with masked action chunking and simulation/real-robot task outcomes. Thus a new state/recovery project must compare against this and other strong current action-chunk methods, not pretend async recovery was never studied.
- [LeRobot #4870](https://github.com/huggingface/lerobot/issues/4870) TDMPC server time-major queue issue already has [PR #4872](https://github.com/huggingface/lerobot/pull/4872); [#4327](https://github.com/huggingface/lerobot/issues/4327) shared-policy parallel evaluation already has [PRs #4341](https://github.com/huggingface/lerobot/pull/4341) and [#4450](https://github.com/huggingface/lerobot/pull/4450); [#3747](https://github.com/huggingface/lerobot/issues/3747) stale observation on DAgger resume already has [PR #4398](https://github.com/huggingface/lerobot/pull/4398). **Do not duplicate these.**
- [C2P ECCV 2026 official repository](https://github.com/Yundi218/Concept-to-Pixel) is missing several code files mentioned in its README, independently reported by users. Original geometry-consensus itself is not a new method when renamed as geometry trust. External geometry evidence and genuine OOD improvement against faithful original+current baselines remain unverified.
- A user-independent formal L8/L9/L10 community ranking has not been established; acceptance, novelty and reproducibility are evaluated by actual artifacts/peers, not these labels.


### Completed real EEG downstream classifier check (NEGATIVE, 2026-10-13)

[The frozen original EEGMI classifier study](https://github.com/lindicaphxag-tech/moabb/actions/runs/38341234033) is now SUCCESS. Four independent subjects, eight original EDF runs, actual T1/T2 motor imagery annotations, 40 clean heldout event trials, same chronological splits and original real source. Changing *only test-event raw source* prior to whole-record IIR filtering caused **0/40 predicted-class changes**, identical 55.0% mean per-record clean/perturbed heldout decoding accuracy, and a within-record mean predicted-class-1 probability change median of **6.910888528111058e-13**. [Full, explicitly negative original-result report](https://github.com/lindicaphxag-tech/moabb/blob/research/physionet-eeg-decoder-dependence-20261013/research/PHYSIONET_EEG_DECODER_NEGATIVE_PILOT_20261013.md). The synthetic polarity-flip is not label leakage, and a nonzero IIR source transfer alone does NOT imply material task-level leakage. The pre-frozen **20 new subjects/40 additional EDF** [extension](https://github.com/lindicaphxag-tech/moabb/actions/runs/38341544307) was separately launched; outcome/denominator pending — no positive gain claimed.

The full [official Braindecode #1320 CI](https://github.com/braindecode/braindecode/actions/runs/38338357056) has now completed SUCCESS on latest official head `d943a585...`, including full tests and acceptance; [style](https://github.com/braindecode/braindecode/actions/runs/38338357034) and [docs](https://github.com/braindecode/braindecode/actions/runs/38338357027) also succeeded. The source-corrected local-zero / remote-five DDP test, after a first honest red run that exposed invalid `reshape(0,-1,D)`, passed **Ubuntu and Windows** on [new fork run](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38341326398) at time checked; macOS must finish before promoting this new patch to official PR. No maintainer approval or Merge has yet occurred.
