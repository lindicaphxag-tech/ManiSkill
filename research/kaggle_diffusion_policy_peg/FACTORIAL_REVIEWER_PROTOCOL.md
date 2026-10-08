# PegInsertionSide — source-frozen 2×2 Diffusion Policy attribution protocol

**Status 2026-10-08:** Code + unit tests only. No four-arm Kaggle job has been submitted by this repo, and **no four-arm policy performance has been measured**. The original two-arm corrected Kaggle v4 result is still not published in this repository.

## Why four cells are necessary

The earlier experiment `run_assay.py` compared upstream baseline vs **both** proposed code changes applied together. Even if the paired policy score changes, the data cannot establish that #1495's converter or #1472's controller change caused it individually. Therefore a nominally positive two-arm score is insufficient maintainer evidence for either patch.

The independent runner `run_assay_factorial.py` freezes four source interventions:

| Cell | Converter file | Controller |
|---|---|---|
| upstream_baseline | upstream base | upstream base (`rot_lower`) |
| converter_pr1495_only | PR #1495 | upstream base (`rot_lower`) |
| controller_pr1472_only | upstream base | PR #1472 (`rot_upper`) |
| combined_pr1495_pr1472 | PR #1495 | PR #1472 (`rot_upper`) |

Source commitments are defined and checked by `assay_design.py` and independently checked against the actual runner's Python AST in CI:

- ManiSkill base: `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- PR #1495 pinned converter source commit: `875ae4d8777678119b2f192ee186c6c15e6894d5`; its `mani_skill/trajectory/utils/actions/conversion.py` Git blob is **exactly** `438c4c41c7fe067194d8e090b9114ad0b5251128`, which matches the public current #1495 head `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`. The earlier commit identity is not the current PR identity; this claim is **file-content equivalence only**.
- PR #1472 overlay: `eed9be164797d41540421bda8adb3840377d7087`.

Every cell independently checks out its frozen source and replays the original, SHA-256-pinned public motion-planning demos through that exact converter/controller pair. Only then are compatible trajectories copied into **four different** HDF5 files and matched by the ordered original `episode_seed` identities. A source tree is never trained on a dataset encoded by another tree.

## Scientific limitations and required disclosures

1. **Post-treatment selection bias:** the replay stage intersects *successful* converted episodes from all four arms. Whether a demonstration replays successfully may itself depend on the conversion or controller fix. Therefore the trained common intersection is a post-treatment, selected population: the difference-in-differences cannot be presented as an unbiased causal effect on the full source-demonstration distribution. Publish arm-specific replay-success numerators and the original requested denominator; show results from all seeds, and ideally construct a new protocol that preserves a predeclared original seed population without treatment-conditioned selection. Until then call the contrasts **selected-subset exploratory**.
2. **One training seed:** the supplied runner has fixed seed `1`. A 2×2 source intervention isolates algebraic effects for this setting but cannot give significance, variance across policy initializations, or broad generalization. Any confirmation needs multiple independent policy seeds, evaluated episode seeds, and a justified experimental unit.
3. **Mixed effects:** replay dataset changes and controller execution changes are deliberately both parts of the treatment, but four cells alone cannot distinguish pure test-time controller effects from training-set distribution effects. Crossed *train-source × eval-controller* tests would be required for that distinct estimand.
4. **Reduced evaluation:** relative to upstream official baseline, evaluation uses 20 episodes every 10,000 iterations rather than 100 episodes every 5,000. A single 20-episode success rate moves in increments of 0.05. Never report it as high-precision evidence.
5. **Kaggle v4:** current corrected private v4 may still be unfinished. The original archived public v3 failed **before the first optimizer update**. Never fold its trajectories into completed training evidence.
6. **External validation:** SHA-256 consistency checks, public self-authored CI, and even GPU output from the owner's Kaggle account cannot prove independent researcher replication.

## GPU execution entry point (requires the owner's own Kaggle authorization)

The four-cell runner is self-contained (no remote dependency on other project Python files). To submit it, stage **only**:

- `run_assay_factorial.py` as the code file;
- `kernel-metadata-factorial.json` renamed to `kernel-metadata.json`.

Use the Kaggle CLI with the **user's own authenticated account**, e.g. `kaggle kernels push -p ./factorial_staging`. This chat has **not** submitted any GPU job; cloning public GitHub source and running CPU CI does not start Kaggle training.

The program writes `/kaggle/working/assay_output_factorial` (not the historical two-arm output folder), keeping manifests, per-arm replay identities, TensorBoard scalars, success metrics, paired seed list and source-tree IDs. Training four 100,000-iteration arms is expensive; do not launch without quota awareness.

After the entire four-cell output is available:

```bash
python research/kaggle_diffusion_policy_peg/policy_evidence_gate.py \
  /path/to/assay_output_factorial --output /path/to/factorial_reviewer.json
```

The fail-closed gate compares all four fixed source cells, the exact **shared original source-seed set**, all required training and evaluation steps, denominators, finite curve values and source hashes. It refuses a partial run and only then produces **descriptive** converter/controller contrasts and their interaction. It does not compute or assert a statistical p-value or physical-policy success in the absence of actual results.

## Pre-registered reviewer acceptance gates

Before claiming a benefit for #1495 or #1472, require real TensorBoard scalar traces, exact source/dataset identities, full four-cell numerators/denominators and uncertainty across multiple policy seeds. Interpret converter-only effect as `C - B`, controller-only effect as `K - B` and interaction as `CK - C - K + B`; do **not** infer any effect solely from the `CK - B` contrast.

Before promoting this protocol to a paper confirmatory experiment, resolve the post-treatment selection bias, add independent held-out training and evaluation seeds, and freeze success thresholds *before* seeing new outcome curves.

The CPU fixture in `tests/test_policy_evidence_gate.py` contains deliberately **synthetic metrics used only to test rejection logic**; it cannot substitute for actual Diffusion Policy curves or maintenance acceptance.


## Pre-selection intention-to-replay: implemented

The four-arm Kaggle runner now emits
`assay_output_factorial/replay_intention_to_treat.json` **before**
computing the common-success source-seed intersection, creating the four
paired training HDF5 files, or beginning the first policy optimizer update.
Each row binds an original `episode_id`, source `episode_seed`, exact
source dataset archive, four source-code intervention identities and four
independently observed replay success sets. The record is retained even if
the common-success intersection is below the required threshold or subsequent
GPU training fails.

To inspect the raw replay effect on **all originally requested episodes**
(with no post-treatment survivor selection):

```bash
python research/kaggle_diffusion_policy_peg/replay_itt.py \
  /path/to/assay_output_factorial/replay_intention_to_treat.json \
  --output /path/to/replay_full_population.json
```

The fail-closed evaluator checks exact ordered source episode seeds, SHA
digests, intervention identities, and every arm's binary success population.
It reports original-population replay rates, arm-vs-arm gain-only/harm-only
paired episodes, four-arm binary pattern counts and the finite-population
converter/controller interaction with the **original, precommitted
denominator**.

Crucial distinction: those are *trajectory replay* outcomes, not learned
Diffusion Policy evaluation outcomes. The four-arm policy trainings remain
on the common post-treatment-selected demonstration set. The full-population
replay contrast cannot be silently relabeled as a policy effect or as an
unbiased causal estimate of trained-policy advantage. No p-value or
independent external reproduction is claimed.

[Public adversarial CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717263530):
27 pure-Python tests across 3.10 / 3.12 / 3.13 passed. The tests use
synthetic binary fixtures; **no four-arm Kaggle execution is claimed**.
The pre-existing v3 archive lacks complete per-source-seed intersection
evidence and cannot be retrospectively upgraded into this result.
