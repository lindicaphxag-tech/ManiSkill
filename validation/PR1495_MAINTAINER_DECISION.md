# ManiSkill #1495 — maintainer decision packet

This is the current one-page handoff for upstream
[mani-skill/ManiSkill#1495](https://github.com/mani-skill/ManiSkill/pull/1495).

## Decision summary

**Current #1495 is reviewer-ready as a standalone two-file patch.**

The converter no longer hard-codes a particular rotation sign convention. It
probes the active `PDEEPoseController` production action mapper, extracts the
signed axis-separable rotation scale, and encodes the target XYZ-Euler delta in
that active action chart.

Unsupported mappings fail explicitly rather than silently guessing.

## 2026-10-08 research-integrity correction

**Please do not cite the apparent 100–199 heldout replay as replication.**
The nominally green [holdout run #37745942944](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37745942944)
actually re-used the first 100 HDF5 source groups despite recording
episode-index metadata 100–199. The independent original-artifact
[audit #37752017483](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37752017483)
failed on the source-seed count mismatch. The result is **invalid for
disjoint cohort inference**, not evidence of a second success.

[Root cause, withdrawal and corrected physical-HDF5 slicing status](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/native-delta-pose-assay/research/kaggle_diffusion_policy_peg/HOLDOUT_SOURCE_VALIDITY_ERRATUM_2026_10_08.md).

The **first** 100-demo cohort result below remains valid: independently
audited 90/91/1/91 successful conversions on source indices 0–99. We have
not changed the preregistered 100–199 target, and no corrected holdout
outcome is claimed until actual sliced inputs and original seed identities
pass the same audit.

## Frozen current identities

- upstream #1495 head:
  `69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`
- PR shape:
  **1 commit / 2 files**
- converter blob:
  `438c4c41c7fe067194d8e090b9114ad0b5251128`
- focused test blob:
  `71254e58d690c2d4d8690eea4c6b8f637f157dd4`
- exact #1472 compatibility head:
  `eed9be164797d41540421bda8adb3840377d7087`
- #1472 controller blob:
  `bc4e811f336ef67d0f6cccf30116be238bb4031d`
- #1472 controller-test blob:
  `ce7e6e66cf3e286168d3d82f763307e18b587659`

## Exact-current-head compatibility closure

Canonical public workflow:

**https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37687749068**

The workflow first proves that the production/test blobs are byte-identical to
the current squashed upstream PR head.

### A. Current / legacy mapper

Result:

```text
tests/test_action_conversion.py
13 passed
```

Coverage includes:

- compound XYZ rotations;
- seeded 128-case quaternion/Euler round trip;
- anisotropic signed scales;
- zero-scale rejection;
- non-axis-separable mapping rejection.

### B. Exact #1472 mapper

The second job overlays the exact #1472 controller and controller-test blobs,
verifies their hashes, and runs the same current converter against that mapper.

Result:

```text
tests/test_action_conversion.py
tests/test_pd_ee_pose_controller.py

18 passed
```

Therefore #1472 is a tested compatibility environment, not a prerequisite for
reviewing or merging current #1495.

## Native controller evidence

Kaggle v15 checked out the same exact current head
`69facfaafaa0ef233d36ef19e6cd9a0f03532ee0` on a Tesla T4 and ran the upstream
conversion tests plus a native PickCube controller assay:

```text
14 passed
```

The run records a hashed `pip freeze --all` environment snapshot.

Artifacts:
https://github.com/lindicaphxag-tech/ManiSkill/tree/research/native-delta-pose-assay/research/kaggle_native_assay/results/pr1495_head_v15

Narrow native measurement:

- unsaturated one-step controller-target error:
  **5.36e-9 rad** for current #1495;
- legacy axis-angle baseline:
  **1.06e-3 rad**.

The saturated 16-step case is mixed (**0.228 vs 0.212 rad**), so this packet
makes no broad performance or task-success claim.

## Historical compensating-fault evidence

Earlier converter/controller versions exposed a genuine interaction:

```text
old converter + old controller   ~= 5.0767 deg
old converter + #1472            ~= 64.7473 deg
old #1495 + old controller       ~= 66.1280 deg
old #1495 + #1472                ~= 4.83e-06 deg
```

That result is retained as historical diagnosis, not as the merge argument for
current #1495.

Current #1495 addresses the review concern by asking the active production
mapper which signed chart it actually implements rather than assuming one.

## Newly completed official trajectory-replay 2×2 intervention (2026-10-08)

**This is task-context evidence, distinct from the earlier SO(3) unit
test and from learned-policy task success.**

- [Native official 8-demo four-cell replay run #37715587885](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715587885): **SUCCESS**
- [Raw run log and SHA-bound `factorial_replay.json`](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37715587885/artifacts/11523253779)
- [Independent audit on the actual frozen per-source-seed matrix: CI #37719750458](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37719750458): **SUCCESS**, includes real GitHub artifact download, independent recomputation of counts and paired SHA-256, plus tamper-rejection tests on Python 3.10 / 3.11 / 3.13.

| Converter #1495 | Controller #1472 | Official replay success, same eight source demos |
|---|---|---:|
| off | off | 6/8 |
| on | off | 6/8 |
| off | on | 0/8 |
| on | on | 6/8 |

**Important interpretation:** the controller-only change is *incompatible
with successful replay for this small frozen cohort*, while the composed
change restores replay to the baseline count. But converter-only also
matches the baseline 6/8, so there is **no demonstrated converter-only
replay improvement or learned-policy benefit** on this cohort.

The independently audited, original-source-seed-denominator
converter×controller interaction is **3/4**. This is a descriptive
eight-demonstration replay interaction, not a randomized-population causal
effect, confidence-supported policy benefit, or maintainer endorsement.
The controller-only arm has zero surviving demonstrations; do **not**
assign invented post-selection model performance to that cell.

The enlarged **100-source-demo** four-cell replay has now completed:
[original CI #37719545972](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37719545972)
(SUCCESS). Crucially, a **separate original-artifact audit** independently
downloaded its frozen per-seed matrix:
[CI #37746202004](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746202004)
(SUCCESS; [audited JSON](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37746202004/artifacts/11536185564)).

| Converter #1495 | Controller #1472 | Official replay, original 100 source seeds |
|---|---|---:|
| off | off | **90/100** |
| on | off | **91/100** |
| off | on | **1/100** |
| on | on | **91/100** |

The independent audit verified original dataset identity, four code source
commit identities, all 100 per-source-seed binary records, pairwise source
intersections/digests, summary consistency and the exact four-arm
intersection **1/100**. The original-source-denominator factorial
interaction `CK-C-K+B` is **89/100**. It also reports a *descriptive
resampling sensitivity band* [0.83, 0.95]; because these are a fixed prefix
of official demos, do **not** call this a population confidence interval.
No claim of general learned-policy improvement or #1495-only replay gain is
supported: converter-only differs by only +1/100, while the severe
controller-only incompatibility is what is rescued by combining the fixes.

A **disjoint, explicitly precommitted** source cohort indexed 100–199 was
locked before inspection of the 0–99 result, with falsifiable rate-margin
predictions and a fail-closed 'insufficient source' rule:
[FROZEN_NEXT_COHORT_100_199.md](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/native-delta-pose-assay/research/kaggle_diffusion_policy_peg/FROZEN_NEXT_COHORT_100_199.md).
[Original holdout execution #37745942944](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37745942944)
was found **invalid as a heldout test** by the independently run source-seed
integrity audit #37752017483: the CLI consumed the first 100 physical HDF5
groups despite metadata declaring indices 100–199. This result is expressly
withdrawn. See the linked source-validity erratum near the top of this packet.

## Official CPU policy-training pipeline is now runnable end-to-end

[Successful paired Diffusion Policy smoke CI #37713921020](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37713921020)
trained both original and composed environments on six matching original
source seeds, each with **893 transitions** and the native ~4.40M-parameter
policy. Both executed two optimizer updates, six tiny evaluation checkpoints
across the two runs, then closed normally.

**Both showed 0% success** under two-episode, 20-step short-horizon
evaluations. This is an infrastructure/experiment-readiness result, **not
positive trained-policy evidence**.

## Single maintainer question

**Is deriving the converter's signed per-axis rotation action scale from the
active `PDEEPoseController._clip_and_scale_action` mapper the intended current
controller contract?**

If yes, the current upstream PR can be reviewed on its existing one-commit,
two-file diff.

## Evidence boundary

This packet establishes:

- exact-current-head regression coverage;
- compatibility with both the current/legacy mapper and exact #1472 mapper;
- one deterministic native-controller reproduction.

It does **not** establish:

- learned-policy task success;
- arbitrary-controller replay equivalence;
- compatibility with a future ManiSkill 4 controller rewrite;
- maintainer acceptance or upstream adoption.

All evidence here is self-authored public evidence until a maintainer or third
party independently validates or retains the patch.


## Maintainer's actual policy-evidence request — status and zero-survivorship-bias correction

The request in [ManiSkill issue #1138](https://github.com/mani-skill/ManiSkill/issues/1138)
is specifically for **PegInsertionSide Diffusion Policy training curves / W&B
results**, following a reported PickCube action-conversion issue.
The current PR is **not** claimed to have passed this policy-evidence gate.
The corrected private Kaggle v4 has no publicly archived audited training
metrics on this branch.

The earlier public v3 archive reported original demo replay counts of
**90/100** (baseline) and **91/100** (both PR changes) with common-survivor
set size 90, then failed before the first policy optimizer update due to
a NumPy evaluation compatibility error. This is *not* a one-point improvement
in learned-policy success and not an attributable #1495 gain; the v3
archive also lacks complete original-seed-per-arm data needed to independently
audit every discordance.

To enable a real and falsifiable maintainer experiment rather than selected
success curves, the author prepared:
[full four-cell source-pinned factorial runner and protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/native-delta-pose-assay/research/kaggle_diffusion_policy_peg/FACTORIAL_REVIEWER_PROTOCOL.md).
It treats baseline, converter-only, controller-only and combined source trees
separately and preserves **every originally requested replay outcome before**
the selected-success demonstration intersection. Public
[CI 37717263530](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37717263530)
passed 27 adversarial artifact checks × 3 Python versions using
**synthetic unit test fixtures** only. This is experimental-readiness evidence,
**not** completed GPU training or an external reviewer evaluation.

The single maintainer code-contract question above still stands independently
of this training evidence. This packet is updated on the owner's fork only; it
was not posted again to the upstream PR.


## Source-frozen negative evidence and stronger replay provenance (2026-10-08)

A source-exact-head **GitHub CPU** control experiment was attempted against
`69facfaafaa0ef233d36ef19e6cd9a0f03532ee0`.

- 13 converter unit tests passed against the exact upstream checkout.
- [First CPU Vulkan attempt](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37720313380)
  showed a misleading **green** job due to a Python-to-`tee` shell
  pipeline without `pipefail`; the Python simulator initialization
  actually failed. This workflow defect has been corrected.
- [Strict render-disabled attempt](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37720554116)
  is properly **red**: `render_backend="none"` bypassed the Vulkan
  `RenderSystem`, but the actual PickCube scene then attempted a
  `sapien.render.RenderMaterial`, yielding
  `RuntimeError: failed to find a rendering device`.
- Hence these GitHub CPU actions do **not** supply any genuine task rollout,
  PegInsertionSide Diffusion Policy success rate, or replacement for
  the previous Kaggle graphics-capable native-controller results.

Separately, the [source-frozen four-arm Peg DP protocol](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/native-delta-pose-assay/research/kaggle_diffusion_policy_peg/FACTORIAL_REVIEWER_PROTOCOL.md)
now precommits the **original episode population before intervention**,
uses upstream `replay_trajectory --allow-failure` to keep failed
converted trajectories, and persists each arm's original-denominator
replay success and failure labels independently. A complete source-census
guard rejects missing/unknown episodes; a zero-success arm remains
**0/N measured**, whereas an interrupted arm remains **UNKNOWN**.
This fixes result-dependent missingness in the experimental infrastructure,
but **no new policy training curve is available**.

The immediate upstream review question remains the concrete signed-action
mapper contract. Policy-level adoption or efficacy is not asserted from
these author-generated CPU tests or experimental scripts.


## New 2026-10-08 reproducibility boundary: native HDF5 bytes vs manifest-only evidence

A substantial evidence-integrity gap was identified and fixed in the
**separate experimental assay**, not in upstream PR #1495 source.
Previously, the four-cell artifact gate checked that the declared
HDF5/JSON SHA-256 strings looked structurally valid but did not reopen
the original native files. A hypothetical forged 64-hex-character digest
could therefore pass the manifest-level gate without any matching
trajectory bytes.

The new frozen
[ManiSkill Peg native-evidence capsule v0.2](https://github.com/lindicaphxag-tech/ManiSkill/tree/peg-native-evidence-v0.2/research/kaggle_diffusion_policy_peg)
(SHA `a5c0232bc9a0a9a979b2acab12cbe220022851d0`) adds an
**independently implemented four-arm native HDF5/JSON file auditor**.
It requires exact real files under their original source-arm directory,
re-hashes the actual bytes, validates every source episode against the
original population, checks the HDF5 terminal success (and complete
boolean success time-series) against the JSON label, and separately
reconciles the four-arm replay journal. A missing native trajectory,
wrong hash, dropped failed episode, unknown arm or JSON/HDF5 disagreement
is refused.

[Public CI 37751401827](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37751401827)
passed **63 tests on each of Python 3.10/3.12/3.13** (new HDF5 tests use
synthetic tiny HDF5). The repo's [methodology](https://github.com/lindicaphxag-tech/ManiSkill/blob/peg-native-evidence-v0.2/research/kaggle_diffusion_policy_peg/FACTORIAL_REVIEWER_PROTOCOL.md)
states precisely how independent reviewers can re-open the four actual
native replay files, *if real runs are provided*.

**No raw four-cell Peg policy-performance curves exist as public
artifacts and no source-exact native training/robot rollout success
is claimed.** HDF5 fixture tests are not performance results and
authored hashes do not establish third-party attestation. The
maintainer's most useful immediate question remains the acceptability
of probing the real signed PDEEPoseController scale vs restricting
#1495 to the quaternion-to-XYZ fix.
