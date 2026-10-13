# Four-gate completed upstream software flagships (2026-10-13)

**Evidence ledger for a critical doctoral-admissions or scientific-software reviewer.** A four-gate software engineering contribution is not automatically an original mathematical theorem, a first-authored paper, or a degree/admissions rating.

## Distinguish the same-result causal chain

1. **Problem/failure:** document a real target-ecosystem problem and a concrete minimal witness.
2. **Mechanism:** show which code change addresses that failure, and distinguish reused prior mathematics from new implementation correctness.
3. **Reproducible evidence:** independent reimplementation or actual upstream tests, numerical controls and source identity.
4. **External approval:** an unrelated maintainer approves/merges that **same** contribution; don't cite reviews of other PRs as approval of a still-open one.

## Completed engineering flagship A — NeuroRVQ cold-start DDP correctness

**[Braindecode #1319](https://github.com/braindecode/braindecode/pull/1319) — MERGED.**

- **Failure:** distinct local EEG data and RNG cause first-forward cold-start cosine k-means to construct different EMA codebook index meanings on distinct DDP workers; downstream count/embedding-sum reductions cannot correct already-incompatible code index mapping. The two-rank CPU/Gloo minimal reproducer showed **max 1.3146654** discrepancy in codebook weights.
- **Mechanism:** reuse Braindecode's broadcast mechanism exactly after rank 0's codebook initialization and **before first token assignment**. Synchronize weights, cluster sizes, embedding averages and initialized flag, retaining pretrained and single-rank behavior. This is an original specific production bug fix, not a novel distributed-systems theorem.
- **Evidence:** real two-rank CPU/Gloo regression showed the same rank discrepancy shrink to **0.0**, and tests of cold initialization and subsequent distributed EMA. [Official six-OS/Python matrix](https://github.com/braindecode/braindecode/actions/runs/38142353551) included Ubuntu/Windows/macOS and succeeded.
- **External adoption:** official upstream PR is **merged**. **All four production engineering stages completed.** Scientific NeuroRVQ invention remains attributed to the original model authors.

## Completed engineering flagship B — NeuroRVQ model + pretrained electrode identity

**[Braindecode #1218](https://github.com/braindecode/braindecode/pull/1218) — independent maintainer APPROVED and MERGED.**

- **Need:** correct integration of the published multi-scale pretrained EEG foundation model, with electrode-identity-safe channel mapping and pinned pretrained checkpoint schema; pretrained spatial channel slots must not silently assume arbitrary first-N electrodes.
- **Mechanism:** channel-aware Braindecode module, pretrained loader requiring explicit channel names / channel metadata (fresh randomly initialized models may use a documented positional fallback), strict schema validation and clear third-party license boundaries. This is an integration/provenance mechanism, not original invention of NeuroRVQ.
- **Internal source parity:** all 263 shared pretrained tensors and a CPU copied-weights parity audit were documented; logits/input gradients agreed in that exact probe.
- **Independent maintainer approval evidence:** reviewer bruAristimunha reports a 5-seed × 10-fold independent NeuralBench/Voyager replication of paper Table 1(A) Eyes (PhysioNet) with balanced accuracy **0.837 ± 0.003** against published **0.869 ± 0.026**, and a reported **3.7% relative gap inside the reviewer's 5% criterion**. The reviewer also reports tokenizer parity **2.98e-8** and approved. This is genuine outside technical scrutiny **of the same integrated model**.
- **External adoption:** actual merged PR. **Four engineering stages completed.**

## Completed engineering flagship C — trustworthy EEG benchmark statistical comparison

**[MOABB #1208](https://github.com/NeuroTechX/moabb/pull/1208) — independent maintainer APPROVED and MERGED.**

- **Scientific-software need:** pipeline ranking and significance can become invalid when data have unmatched dataset×pipeline blocks, session/subject repeat imbalance, missing learning-curve permutation identities, mixed protocols or quietly averaged nonfinite scores.
- **Mechanism:** reusable public critical-difference plot, dataset-block Friedman/Nemenyi comparison, prescribed macro-aggregation, fail-closed data-integrity conditions and reference test. Friedman/Nemenyi statistics are established prior art; the contribution is **verified statistical-software correctness and safe integration**.
- **Evidence:** canonical Demšar formula k=4, N=14, alpha=.05 gives critical difference approximately 1.25, plus tests of missing/mismatched experimental cells.
- **Independent maintainer approval:** reviewer bruAristimunha explicitly checked the published numerical constant and data ordering, ran **16/16** headless focused tests, confirmed the completeness hardening and approved.
- **External adoption:** merged. **Four engineering stages completed.**

## Completed engineering flagship D — EEG-CLIP model port

**[Braindecode #1200](https://github.com/braindecode/braindecode/pull/1200) — independent maintainer APPROVED and MERGED.**

- **Need:** EEG/text dual-encoder published-source functionality integrated with Braindecode native model, skorch/forward, paired inference, serialization and stable loss semantics.
- **Mechanism:** separate tensor-valued default forward from paired encoder interface; preserve source projection, scale and bidirectional contrastive loss; adapt model/checkpoint contracts and tests. The published EEG-CLIP architecture is **not** a new algorithm attributed to this contributor.
- **Evidence:** pinned source logits/loss/gradient parity and multi-platform unit/integration checks. Maintainer confirms source projection and CLIP loss, CPU/low-precision contract checks, and TUAB LogReg pathological reproduction within **5%**.
- **External adoption:** independently approved and merged.

## Major new results NOT yet a full four-gate chain

**[Braindecode #1320](https://github.com/braindecode/braindecode/pull/1320) — OPEN, not approved or merged.** Strong engineering candidate: local DDP CLIP negatives differ from central global loss; new synchronized paired-shape collective, uneven 2+3 rank actual-gradient oracle, valid 0+5 rank case and its real ambiguous reshape red/green fix, [3/3 OS fork tests](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38341326398). Official docs/style/acceptance succeeded, but [latest full official test](https://github.com/braindecode/braindecode/actions/runs/38342524442) remains in progress. PR description was rewritten from a contradictory historical log to the current diff and exact reviewer decision. Actual maintainer review still missing. The attempted official reviewer request failed GitHub 403; **do not claim the request was sent**.

**[MOABB #1235](https://github.com/NeuroTechX/moabb/pull/1235) — OPEN.** The user-facing guarantee is direct raw epoch extraction-window non-overlap only, not whole-record zero-phase IIR independence.

**[JAX #41227](https://github.com/jax-ml/jax/pull/41227) and [#41228](https://github.com/jax-ml/jax/pull/41228) — OPEN, review status CHANGES_REQUESTED.** Several of the original inline suggestions on #41227 became outdated after changes, but a new reviewer approval is still needed. Current GitHub reports clean Git merging but mergeable-state blocked.

**[ManiSkill #1495](https://github.com/mani-skill/ManiSkill/pull/1495) — OPEN.** Native controller conversion evidence has positives and negative saturated cases, without broad end-task superiority or approval.

**Real EEG decision certification research: prospective mechanistic SUPERIORITY GATE FAILED.** [Eight truly unseen people / 16 true PhysioNet EDF / 3 fixed synthetic training-channel gain interventions](https://github.com/lindicaphxag-tech/moabb/actions/runs/38355519800) plus [independent full 8-person original-artifact audit](https://github.com/lindicaphxag-tech/moabb/actions/runs/38355642342): 14 repeated conditional classifier flips; only **+0.833 percentage points** Hessian certificate coverage against lambda-only, in **one of eight independent people**. Preregistered gate required >=5 pp and gains for at least 2 people. [Negative full report](https://github.com/lindicaphxag-tech/moabb/blob/research/eeg-gain-shift-cert-unseen-20261013/research/PHYSIONET_8_UNSEEN_TRAIN_GAIN_CERT_NEGATIVE_20261013.md). Known strong-convex optimization and curvature-bounding prior art; a correct certificate does not establish novel theorem priority or measured practical superiority.

**ManiSkill lost ACK SO3 recovery scientific superiority gate FAILED.** Source template equals adequately command-aware reset baseline on unseen variants, official PickCube task success zero; clear originality claim boundary, not a completed new algorithm result.

## Doctoral review conclusion

- **YES:** there are at least three already completely accepted and externally governed, rigorously demonstrated *scientific software engineering* projects (not just 28 unexamined PR counts).
- **NO:** a new researcher-priority original mathematical theorem, an accepted original-method paper, or an external research group adopting an unprecedented original algorithm has not been established by these same records.
- **NEXT:** finish the still-open Braindecode #1320 through official CI and maintainer API-boundary judgement; if reviewers reject its design, adapt to their guidance rather than declaring author-side success. For a separate academic-method flagship, design a genuinely distinct hypothesis and compare against the strongest literature before any new blind experimental cohort. Existing real EEG source stability and robot SO3 studies already falsified key exaggerated superiority hypotheses.

**No official community-wide L8/L9/L10 scale exists.** Evaluate project level from original problem, mechanism, exact evidence, and the actual outside project or research reviewer, keeping scientific priority separate from engineering acceptance.
