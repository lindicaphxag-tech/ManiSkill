# Main-track readiness audit: When Did My Command Execute? (9 October 2026)

**Status:** Research design and source-grounded review criteria, **not** a conference decision, acceptance prediction or finished VLA fault-recovery result. Latest vetted manuscript is [v1.9](https://github.com/lindicaphxag-tech/ManiSkill/blob/main/research/frozen_policy_transfer/WHEN_DID_MY_COMMAND_EXECUTE_MANUSCRIPT_V1_9.md).

## Defensible central claim

A frozen controller policy transferred to a stateful target-relative action interface faces an *unknown executed-command history*, distinct from unknown action-channel semantics or policy task uncertainty. Two missing ACKs imply multiple complete latent SE(3) target histories. In a correctly matched native PhysX task, finite-hypothesis public achieved-motion evidence can sometimes replace a privileged controller target read. This is selective **information acquisition**, not an action safety theorem.

The strongest published author-operated native experiment is currently **64 different PullCube/StackCube task resets; 576 actual CPU PhysX simulator/controller worlds; 53/64 success in both matched information treatments with zero paired success discordance; 48 versus 64 actual privileged target reads; 16 empirically authorized complete histories with zero observed mistakes in *that* cohort**. Predecision physical commands and poses are matched; both methods use the same postdecision belief state machine/compiler. [Original 64 SHA256 permanent archive](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/shared-compiler-evidence-original64-20261009/research/frozen_policy_transfer/evidence/shared_compiler_twoack_original64_1480001_1490032).

**Negative evidence cannot be omitted.** Another disjoint real PhysX 64-case cohort recorded a *wrong confident* public history [StackCube 1730027, source audited](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37924192162). A separate 64-case prior also independently reported one wrong confident history. Therefore zero-risk, guaranteed identifiability, physical safety and formal noninferiority are not supported. The error demonstrates a gap between physical actuator-motion envelopes and an *empirically fitted*, not guaranteed, residual threshold.

## Novelty boundary against published main-track research

- **When to Act, Ask, or Learn: Uncertainty-Aware Policy Steering** (RSS 2026; Yuan, Wu, Bajcsy): [proceedings](https://www.roboticsproceedings.org/rss22/p142.html). Investigates uncertainty-aware test-time policy steering, selective queries and conformal calibration with simulation and physical robot data. We **must not** claim that selective queries, conformal risk calibration or act/ask gating were invented here. Different scientific unknown: internal commanded-target state after execution ACK loss, with physically matched native controller intervention.
- **Steerable Vision-Language-Action Policies** (RSS 2026; Chen et al.): [proceedings](https://www.roboticsproceedings.org/rss22/p074.html). A strong reasoner/VLA hierarchy plus real manipulation generalization. The present PPO-only causal result is not comparable in policy breadth or real-world performance.
- **Tune to Learn: How Controller Gains Shape Robot Policy Learning** (RSS 2026; Bronars et al.): [proceedings](https://www.roboticsproceedings.org/rss22/p139.html). Shows controller dynamics and gains are central, not merely wiring. This work cannot assume fixed dynamics, contact or actuator envelopes are harmless.
- **TAM: Torque Adaptation Module for Robust Motion Transfer** (CoRL 2026 Spotlight): [authors' project page](https://dongwon-son.github.io/tam-project-page/). Implements policy-independent adaptation to real dynamics mismatch, including hardware validation. Our method addresses controller target-memory ambiguity, **not** payload dynamics or torque correction; honest experiments should test whether the public envelope fails on those shifts.
- **ActionShift / DualABI** [source](https://github.com/Archerkattri/actionshift) explicitly studies hidden action-contract identification with paired frozen-policy baselines and active probing. Our work cannot use privileged read counts alone to assert superiority over an unexecuted equal-public-sensor, equal-actuation-cost active probe alternative.

## Concrete rejection risks and required tests

| Reviewer objection | Available evidence | Required acceptance-grade falsifier |
|---|---|---|
| Algorithm implementation or physics confounds information treatment | New 64 same-code physically matched prefix; source audit green | Repeat on at least another genuinely stateful native controller family, not a copied Panda-only chart; check actual action and target read semantics |
| A heuristic can confidently choose wrong | One independently audited wrong label; prior 16/16 correct doesn't guarantee safety | Fully new precommitted reliability-gate rollout, zero tolerance for hiding wrong labels, risk-vs-private-read Pareto curve at matched sensor/probe costs |
| Selective query / abstention is not novel | Correct: standard finite set-membership logic | Demonstrate *new* execution-state observability boundary, complete-history real robot controller integration and active information-value vs querying, not rebrand a confidence threshold |
| Two frozen PPOs cannot establish broad policy transport | Two PPO successes only; no published successful VLA fault-recovery | At least one real task-competent fixed BC/diffusion/VLA policy **actually experiencing a stateful-controller ACK perturbation**, not simply passing clean LIBERO |
| Public achieved samples and neutral probe are not free | Two XYZ reads plus common known-delivered t4 arm step | Report all sensing/actuation/computational latency and queries, plus a matched-public, probe-budgeted strongest active baseline |
| Synthetic hold injection isn't actual transport fault | Physical native zero/hold source has all four ACK truths | Test delayed/reordered ACK, partial action, contact-dependent response, asynchronous stale inference and genuine software delivery faults |
| Pairwise equality isn't automatically noninferiority | 53 both wins, 11 both losses, no discordance on n=64 | Precommit a clinically/robotically relevant noninferiority margin, test power and paired intervals, then evaluate independently held-out populations |
| Externally unrecognized | Public author-owned source/audit and repo self-PR | Outside investigator selects unseen resets and publishes original independent execution on own infrastructure; upstream maintainer review or paper decision tracked separately |

## Actual frozen SmolVLA evidence: no misleading task-ABI inference

Authentic native LIBERO/LeRobot four episodes each on spatial tasks 0 and 1 gave 1/4 and 4/4 official success [byte-archived original run](https://github.com/lindicaphxag-tech/ManiSkill/tree/evidence/smolvla-libero-4plus4-original-20261009/research/vla_beliefbridge/evidence/authentic_smolvla_libero_four_inits_per_task_20261009). These were **no-fault** task-competence pilots with small denominators. Native LIBERO OSC commands use an achieved-pose control target rather than ManiSkill's persistent previous commanded target, so injecting a drop into native OSC does **not** by itself validate our hidden target-memory problem.

A scientifically correct VLA extension must: pin the actual task-specific checkpoint and action normalizer, establish decoded rotation/frame units, establish a **genuine** persistent target-relative controller or physically stepped ABI conversion, invalidate queued asynchronous chunks after intervention, and record actual official task success with and without two *physically executed* unknown-ACK events. If any provenance/ABI prerequisite fails, refuse to report VLA fault recovery.

## Risk-selective mechanism now under true forward testing

The original 128 source-only retrospective audit [source](../audit_public_gap_crosscohort_development.py) supports the *exploratory question* whether the best-to-second public candidate residual separation predicts incorrect unique-history authorization. Previous exact original source labels: one cohort 16 authorized/0 wrong, another 16 authorized/1 wrong. The one wrong's residual gap was **3.603634 mm**, while the minimum accepted correct in the first cohort was **4.674019 mm**. A 4.5-mm additional gate would have retained 31 old authorizations with zero old false admissions, but this cutoff was chosen **after** both populations' outcomes were inspected; therefore this is not an out-of-sample confirmatory finding.

The genuinely unseen cohort of PullCube 2020001–2020032 plus StackCube 2030001–2030032 has its own [frozen preregistration](../OBSERVABILITY_MARGIN_GATE_NEW64_PREOUTCOME_V1.json), source [real 10-world method](../frozen_ppo_observability_margin_physx.py) and independent original-64 native runner [CI](../../.github/workflows/observability-margin-gate-new64.yml). Compare full-history A, margin-gated B and fixed-read C on identical original simulator seeds; B and A receive the **same** two publicly achieved XYZ samples, same physical t4 probe and matched fault-prefix controls, and the threshold cannot be retuned in response to this new cohort. Report every wrong admission, query and paired task outcome. An earlier workflow invocation typo caused a **pre-physics failure**, which must remain in the experiment ledger.

A zero-error *empirical* cohort is not a statistically certified failure bound. Even zero wrong history decisions in sixteen admitted histories leaves one-sided 95% binomial upper bound 1 - 0.05^(1/16) ≈ 17.1% under an illustrative iid sampling assumption, not a robot safety statement. No exchangeability/calibration basis has yet been established for a conformal guarantee.

## Proposed headline and framing

**When Did My Command Execute? Public Observability and Selective Private State Reads for Frozen Robot Policies with Missing Acknowledgements.**

One central idea, three connected contributions: (1) explicit complete SE(3) latent execution-history interface and impossibility when public response sets overlap; (2) mechanically matched, same-code information-versus-task study with a truly strong counted-reader comparator and independently auditable original task traces; (3) falsified heuristic reliability under domain shifts followed by *prospectively* evaluated abstention versus query frontier.

The standard overlap observation is background, **not** a new mathematical theorem. Do not label the result an RSS/CoRL/ICRA main-track excellent paper, a formal physical safety certificate or external endorsement until the above independent tests actually satisfy the corresponding thresholds.
