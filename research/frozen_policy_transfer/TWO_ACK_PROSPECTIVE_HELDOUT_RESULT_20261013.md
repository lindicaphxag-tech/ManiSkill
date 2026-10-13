# Two unknown ACKs: prospective public-observation policy recovery on genuinely new PhysX resets

**Result report — 2026-10-13.** Frozen before new physical outcomes; all results from original GitHub Actions runs. Code, training data and preregistration are available in this branch. Independent source/artifact re-evaluation has passed. **This is a constrained target-restoration primitive, NOT a new VLA task-completion result or a proven unique algorithmic innovation.**

## Frozen hypothesis and original physical protocol

Hypothesis: A public EE-state feature expressed relative to a controller-source-replayed *nominal* goal will reduce reset nuisance variation, making the four missing-ACK history cases separable without reading hidden truth. Its learned nearest-centroid labels can then condition a source-valid corrective action.

The methods and new holdout seeds were frozen at [preregistration](../TWO_ACK_HELDOUT_SOURCE_NORMALIZED_PREREG_20261013.json), blob `b86bdf490d7bf3ee1335cfc774cdd11c41db7ae8`, before new outcomes. Training prototypes were frozen at [prior data prototype register](../TWO_ACK_HELDOUT_TRAIN_PROTOTYPES_20261013.json), blob `48000e2831537c178262835b17748b37672b10d4`, from the prior independent 160-world / 8-reset-cluster experiment. The new test used **different** reset seed sets: Panda `5603001–5603004`, xArm6 `5703001–5703004`. No test seed trained a centroid. Every test reset crossed four real hidden ACK histories and four precommitted policies.

- [Original exact-head native PhysX holdout run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38332965278), head `503e5cfe`: Panda and xArm6, both **SUCCESS**, 64 physical simulator conditions each, **128 total**, **eight new reset clusters**, 32 public-observation classification scenarios *per method*, grouped by reset.
- [Independent full original artifact audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38333385887), head from the separate audit workflow: **SUCCESS**. The auditor fetched both original robot artifacts, reconstructed every prediction from the immutable training prototypes and public features, verified 128 unique cells, identical paired pre-choice robot states, no hidden ACK/private target read on public paths, and independently recomputed every paired error and gate.
- In the task each robot uses ManiSkill `PickCube-v1` and native `pd_ee_target_delta_pose`, but the **primary endpoint is end-effector achieved XYZ distance to the prechosen public source target after one history-conditioned translation correction plus eight identical control steps**. It is not the environment's cube grasp/placement success, real packet loss or contact safety.

## Independently audited heldout outcomes

| Metric | Panda | xArm6 |
|---|---:|---:|
| ABSOLUTE_XYZ: ACK-classification correct | 6 / 16 | 6 / 16 |
| SOURCE_RELATIVE_XYZ: ACK-classification correct | **16 / 16** | **16 / 16** |
| Source feature: mean achieved target error | **0.1607 mm** | **0.3545 mm** |
| Raw XYZ: mean achieved target error | 18.3660 mm | 19.4214 mm |
| NO_ACTION: mean achieved target error | 22.2895 mm | 22.3161 mm |
| PRIVILEGED_ORACLE: mean achieved target error | 0.1607 mm | 0.3545 mm |
| Independent new reset clusters source feature beat BOTH public baselines | **4 / 4** | **4 / 4** |

The preregistered gate was source-relative error lower than **both** raw-XYZ and no-action in at least 3 of 4 original heldout reset clusters **for each robot**, without dropping any failures. Both robots met 4/4. **We do not interpret 4/4 independent clusters per body as a high-power generalization trial.**

### Per independent reset cluster, public-policy achieved target error (mm)

| Robot | Seed | Absolute XYZ | Source-relative XYZ | No-action |
|---|---:|---:|---:|---:|
| Panda | 5603001 | 20.5273 | 0.1533 | 22.2846 |
| Panda | 5603002 | 12.0163 | 0.1665 | 22.2916 |
| Panda | 5603003 | 13.7793 | 0.1663 | 22.2928 |
| Panda | 5603004 | 27.1412 | 0.1569 | 22.2889 |
| xArm6 | 5703001 | 12.0191 | 0.3555 | 22.3163 |
| xArm6 | 5703002 | 26.8930 | 0.3540 | 22.3163 |
| xArm6 | 5703003 | 22.3163 | 0.3550 | 22.3163 |
| xArm6 | 5703004 | 16.4574 | 0.3537 | 22.3156 |

Each table row is a mean over the four hidden-history counterfactual worlds of that same reset. No row in this table is 4 independent robot initializations.

## Why the result is real but does NOT yet establish a new L9 method

This **is** a bona fide heldout simulation result for a public-signal policy: classification was fixed before the new real physical outcomes; it did not read simulator ACK truth, and the recovery commands actually executed through the target-relative controller. The earlier posthoc leave-one-seed-out experiment alone would have been substantially weaker.

However, [our identifiability analysis](TWO_ACK_RESET_CENTERING_CONFOUND_20261013.md) proves a crucial simpler explanation: in the exact frozen controller, nominal planned translations add a *constant* per robot to its reset public EE XYZ. Therefore, source-goal centering and ordinary reset centering are simply translated features; within-robot Euclidean nearest-centroid decisions would be **identical** if the reset-centering baseline were calibrated properly. This mathematical control was disclosed **before new holdout results**.

Consequently, the correct scientific conclusion is:

> In a constrained target-relative translation ABI and two-missed-ACK simulator, a source-available contextual relative-coordinate feature enables an observable-history recovery policy to reproduce the privileged history oracle's achieved target-restoration error on eight genuinely new reset clusters across Panda/xArm6; unnormalized absolute XYZ does not. The available evidence does **not** establish that source replay outperforms ordinary reset anchoring or that this mechanism is a novel general policy.

The mechanisms of global negative distributed CLIP training, fold data leakage and ordinary decision-theoretic information capacity have existing literature; external method priority must be assessed separately.

## Mandatory next tests for a genuinely high-tier original method

- **Strong baseline:** explicit public reset-centered XYZ plus a trained raw-state estimator, fair cost/per-run controls, same fixed fresh test seeds.
- **Break additive equivalence:** prospective variation in target commands, controller state, action frame/rotation contracts, observation noise or physical contact that gives source-conditioned hypotheses *more information* than ordinary spatial centering. Any mode unsupported by `ActionHistoryObserver` must fail closed, not be silently treated as supported.
- **Task success and safety:** robust action costs, actual PickCube grasp success, IK/collision failures, abstentions, authority-cost, variable fault injection and sequential probes, independently paired test population; not just target position.
- **External adoption:** maintainer acceptance and independent laboratory reproduction; personal research branch CI does not count as an external Merge.

The earlier [complete source-aware 160-world physical cost matrix](TWO_ACK_PHYSX_RECOVERY_LOSS_AND_SIGNAL_CAPACITY_20261013.md) and the [previous negative 48-world fixed-probe pilot](ACK_ACTIVE_NATIVE_48_PHYSX_FROZEN_NEGATIVE_RESULT_20261013.md) remain disclosed; no negative result was overwritten or deleted.

**Status:** engineering evidence complete for these restricted preregistered studies; **not** yet a finished L9/L10 accepted flagship publication or an externally adopted research method.
