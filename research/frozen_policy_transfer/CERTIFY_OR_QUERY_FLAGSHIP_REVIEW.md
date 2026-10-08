# Certify-or-Query: Evidence-Budgeted Frozen-Policy Controller Transport

**External reviewer decision map | 2026-10-09 | Author-operated research — NOT official ManiSkill or ActionShift work**

> Question: can an unchanged, third-party pretrained robot policy continue acting through a *stateful target controller* when one native command's execution receipt is unknown, without reading the privileged target at every timestep?

**One-sentence result.** In a prospectively preregistered, 64-**NEW**-seed genuine ManiSkill Panda CPU PhysX evaluation on PullCube and StackCube, a two-history *bounded commanded-target* authorization rule, with at most one privileged target readback when certification fails, completed **60/64 official tasks using 15 authoritative target readbacks**. A fixed one-readback-per-fault comparator completed **57/64 using 64 reads**. This is a **76.5625% reduction in the number of decision target-readback calls**, **NOT** proven better success probability, lower energy or collision safety.

## New information behind the result — NOT new generic action adaptation

The incoming frozen PPO emits achieved-EE-relative `pd_ee_delta_pose` actions. The destination `pd_ee_target_delta_pose` controller instead accumulates the **previous commanded target pose**, which may differ substantially from the robot's achieved EE pose. When all delivered native actions and reset provenance are known, a public history observer can reconstruct that target without reading a private field at decision time.

If the arm command might or might not have been executed, there are at least two credible target memories `M_A` and `M_B`. An exact common inverse can fail even when task objectives are compatible. This work therefore uses an ordinary Chebyshev/geodesic bounded common command **only after verifying target/action-chart assumptions and both errors below 0.05m/ 0.05rad**; otherwise it either explicitly refuses or spends **one accounted privileged controller-target readback** and reinitializes state. The one-readback method has **more information** than optimistic and zero-readback controls; do not describe this as equal-information algorithmic superiority.

The key question is **execution-evidence availability and the correct use of the observation budget**. Belief states, active queries, set membership, SO(3) midpoints and action adaptation are established areas. In particular, [ActionShift](https://github.com/Archerkattri/actionshift) already studies hidden action-interface beliefs, probes and delay-aware control; [SPACE](https://arxiv.org/abs/2606.24049) studies state-delta action adaptation across robots; [TAM](https://github.com/Dongwon-Son/TAM) uses history-conditioned torque compensation. Novelty of this specific combination, relative to these and earlier event-triggered estimation controllers, **has not yet been established by peer review**. It does NOT invent those underlying mechanisms.

## New prospective equal-information-cost query timing falsifier

**Stronger causal-mechanism challenge than the original 15-vs-64 target read comparison.** We precommitted an entirely NEW 64-reset-state cohort (PullCube 260001–260032; StackCube 270001–270032) and retained the exact original source PPO/controller/bounded-or-query code. As an eighth actual official PhysX controller arm, we introduced a **NON-ADAPTIVE, predeclared 1-of-every-4-seeds readback schedule**: read once at step 3 iff `seed % 4 == 0`, irrespective of geometry, task state, success or observed difficulty. That is precisely 16 target read calls total; the original adaptive controller ended up spending 17 calls.

| Condition | Real native task completions | Privileged target decision reads |
|---|---:|---:|
| **Evidence-triggered bounded-or-one-read**, unchanged | **58/64** | **17** |
| **Precommitted schedule**, same bounded controller otherwise | **47/64** | **16** |
| Fixed mandatory one target read per condition | 60/64 | 64 |
| Zero-readback bounded/refusal | 41/64 | 0 |
| Optimistic ACK guess | 40/64 | 0 |

**Per-seed task-result discordance:** 12 adaptive-only / 1 precommitted-only; 46 both / 5 neither. Exploratory **unadjusted** two-sided exact McNemar p=0.00341796875 on the 64 precommitted paired source-reset states. This is valuable evidence that the **WHEN of expensive evidence acquisition** matters in this one physical-simulator controller family, not merely that fewer readbacks can help. **Limitations:** calls differ by one, the control is a fixed periodic deterministic schedule rather than a truly random policy or competitive learned query agent, no power across hardware domains, and any multi-comparison inference requires adjustment. This does not establish a novel optimal stopping theorem or collision safety.

[**Before-outcome seed/query allocation frozen in commit ee209f6**](https://github.com/lindicaphxag-tech/ManiSkill/commit/ee209f6bc80e2bb280f9b00e6a9bafc330bdc799) · [**eight successfully run genuine PhysX CI jobs**](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833053629) · [**every original state and paired outcome with errors/limits**](CERTIFY_QUERY_PERIODIC_PLACEBO_64_ORIGINAL_RESULTS.md) · [**original full eight-file SHA audit and archive workflow**](../../.github/workflows/archive-query-periodic-placebo64.yml). **All contributor-operated, not endorsed by official ManiSkill/ActionShift.**

## Locked, state-disjoint physical-simulator outcomes

| Original fixed protocol | PullCube | StackCube | Pooled tasks | Privileged target decision reads |
|---|---:|---:|---:|---:|
| Discovery source (16 states), bounded then optional query | 8/8 | 7/8 | **15/16** | **4** |
| Discovery source (16 states), mandatory one readback | 8/8 | 7/8 | 15/16 | 16 |
| **NEW-seed frozen-method confirmation**, bounded then optional query | **32/32** | **28/32** | **60/64** | **15** |
| NEW-seed confirmation, mandatory one readback | 32/32 | 25/32 | 57/64 | 64 |
| NEW-seed confirmation, no-query robust/refuse | 30/32 | 17/32 | 47/64 | 0 |
| NEW-seed confirmation, optimistic unknown ACK | 31/32 | 11/32 | 42/64 | 0 |
| NEW-seed confirmation, source PPO, no fault (context only) | 32/32 | 28/32 | 60/64 | 0 |

**Important:** for the 64 NEW states (Pull 142001–142032; Stack 152001–152032), all task arms are paired by reset seed and original task; the original certifier Git blobs and PPO checkpoints were frozen **before** testing. Against mandatory readback, selective-only succeeds on **5** states and mandatory-only on **2**: this does **not** support a statistically significant general success superiority claim. Both modes read actual controller memory, but selective uses fewer reads.

Original source objects and immutable evidence:
- [Predeclared algorithm/seed lock](https://github.com/lindicaphxag-tech/ManiSkill/commit/9ebb39ef01c06869c60f923cdba5d1e4e5626b1d) · original unchanged algorithm head `db4fe4dd9d09aaff67c5dcf12213ad737162282d`.
- [Eight official genuine PhysX experimental jobs](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37828426195) · [original all-64 per-state successes, omissions forbidden](ROBUST_QUERY_NEW64_PROSPECTIVE_RESULTS.md).
- [Byte-identical 8 raw result JSONs, `SHA256SUMS`, independent stdlib record verifier](evidence/robust_query_new64_142001_152032/) · [successful trusted original source and tamper audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37829741895).
- [Original 16-state discovery source JSON and original simulator stdout](evidence/unknown_ack_bounded_query_16/) · [original 4-job discovery CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37826881229).

## Negative controls that MUST travel with the headline

**Falsifier 1 — naïve geometry is not enough.** Before testing a two-target geometric midpoint on a different cohort, frozen 32 unique reset seeds across two ACK truths (64 paired task×fault conditions) were registered; that zero-query midpoint succeeded on **43/64**, *worse* than zero-query optimistic **48/64**, versus one truthful target read **62/64**. Its belief contained the actual target, but minimizing target discrepancy did not minimize downstream manipulation loss. [Original eight source JSONs and SHA256SUMS](evidence/belief_minimax_prospective_64_96001_97016/).

**Falsifier 2 — task success does not validate ACK inference.** With one prescribed neutral probe and an **achieved-EE-pose-only** nearest-target state classifier, the agent confidently misidentified the executed-vs-held hidden ACK history on **15/16 actually executed, missing-ACK** conditions (and 0/16 held cases): **15 wrong confident labels / 32 registered task×truth conditions overall**. The public-observation heuristic achieved **19/32** task completions, compared to a same-probe optimistic baseline **21/32** and one privilege read **28/32**. These are all physically stepped true ManiSkill trajectories. This is a specific heuristic falsifier — **not** proof that no externally calibrated physics observer can ever recover execution state. [32 original raw trials, source audit and SHA256](evidence/public_response_ack_probe_32_negative/) · [genuine run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37829529190).

**Conditional correction, not secretly validated:** a separately implemented set-membership response certificate can only authorize a hidden-history label when externally attested plant-response envelopes exclude the other hypothesis, and must refuse if model envelope is untrusted. [Draft mechanism PR #83](https://github.com/lindicaphxag-tech/ManiSkill/pull/83) has CPU adversarial tests, **not a calibrated real-PhysX proof of its required envelope**. It is not promoted to experimental result here.

## Exact external decision path (no trust in narrative required)

1. **Verify** the byte-identical permanent source evidence and its SHA manifest. Run `python -m research.audit_new64_bounded_query --input-dir research/frozen_policy_transfer/evidence/robust_query_new64_142001_152032 --output /tmp/certify_query_audit.json` from repo root (Python standard library only).
2. **Re-execute** the exact current flagship method on NEW seeds using the [outside-fork seven-arm one-click workflow](../../.github/workflows/external-selective-query-physx.yml) (or use the [step-by-step independent-fork guide](INDEPENDENT_REPLICATION_QUICKSTART.md)). A contributor-run [native PhysX 8-new-seed smoke](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37831105250) verified the reproducibility interface itself (PullCube 8/8 with one selective vs eight mandatory controller-target reads); it is **NOT** external-party execution.
3. **Falsify** with a second independent controller implementation and a *real* action-delivery/ACK transport (drop, reorder, delay), authentic readback provenance, matched query/inference cost, EE/joint tracking, saturation, contact and force. Publish all incorrect authorizations and failures. [Public replication and falsification issue](https://github.com/lindicaphxag-tech/kaggle/issues/67).

## Precise claims and publication gap

- This research has **two** released, independently trained third-party pretrained PPOs on **one** Panda embodiment/controller family. The task benchmark is *genuine physics simulation*, but the fault is an **explicit controlled native arm target-hold substitution** at one predeclared timestep, **NOT** TCP/ROS packet loss or real hardware actuation failure.
- "Bounded" and "certified" here apply to **controller *commanded target-pose* error under complete two-history and correct controller-mapping assumptions**, **NOT** achieved trajectory error, collision, human safety, physical torques or secure sensor attestation.
- Query savings count **privileged target-state decision read calls** only; they are not energy, bandwidth, latency, financial or physical safety savings.
- All experiments so far are performed by the contributor. A separate user running the exact GitHub workflow in their own fork would establish independently operated execution, **not algorithmically independent reimplementation**.
- The contributor-fork research PRs being merged into the owner's fork confer **ZERO official upstream acceptance**. Official ManiSkill [#1495](https://github.com/mani-skill/ManiSkill/pull/1495), a *different narrower rotation-conversion fix*, remains OPEN; the independent [ActionShift author opt-in discussion](https://github.com/Archerkattri/actionshift/issues/1) has no verified external author reply.
- Reaching an externally reviewed flagship paper will require cross-controller **task-level** transfer (not only Fetch/XArm6 lower-layer setpoint calibration), independent execution, real uncertain transport, and matched-information learned/active-state-estimation controls. More self-merged research PR counts are not an evidence substitute.

**Takeaway:** the current strongest defensible research unit is an **unchanged-policy, resource-aware controller-state-observation gate**, with a genuine task-level new-state holdout and openly preserved cases where naive actuation-state inference fails.
