# Main-Conference Adversarial Review and Evidence Gate (2026-10-09)

**Candidate manuscript:** *When Can Public Motion Authorize a Robot Command? Latent Execution State under Controller-Response Shift*.

**Status:** original author-operated Panda/ManiSkill PhysX research, **NOT** a CoRL/RSS/ICRA main-conference-ready or accepted manuscript. No verified independent physical replication or real-robot task trial. The requirements below are **hard prerequisites, not optional cosmetics**.

## One-sentence distinct task definition

Known action **interface grammar** with missing *realized execution truth* → up to four complete internally remembered native controller target histories after two unknown ACKs. A public motion observer can sometimes identify the unique full history to reduce a costly privileged internal controller-target read, but **its empirical motion response model can be wrong**, confounding unique agreement with actual correctness. Study the controller's **evidence authority** under dynamics shift, not the already-studied generic active-robot-adaptation problem.

## Close existing top-conference novelty threats, with appropriate credit

- **ActionShift / ActionABI** (https://github.com/Archerkattri/actionshift): compositional hidden action ABI, structured beliefs, active probes, frozen PPO/DP, known grammar and privilege hierarchy. Our independent variable is **command actual execution/held truth** under an otherwise verified ABI, not arbitrary permutation/sign/scale/frame/latency identification. Do not claim to invent full-hypothesis belief or informative probing. Fair ActionShift-style baseline MUST be implemented on same latent-ACK problem, tasks, inputs and action opportunity costs. Simply reporting an unrelated ActionShift benchmark score is not fair.
- **FAIL-Detect, RSS 2025** (https://www.roboticsproceedings.org/rss21/p073.html): sequential OOD failure monitoring and conformal detection. Our monitored error is **controller target-history response miscoverage**, distinct from conventional observed task failure. Emphasize why this mismatch may remain hidden even after official task success.
- **Uncertainty-aware Policy Steering, RSS 2026** (https://www.roboticsproceedings.org/rss22/p142.html): acts/asks/learns using uncertainty and conformal methods with robot hardware. Generic risk-calibrated abstention is NOT original. Any formal coverage bound must explicitly state true-score exchangeability and complete candidate-history assumptions; cannot be advertised as physical safety under contact regime changes.
- **CoRL 2025 OOD safety filters** (https://proceedings.mlr.press/v305/seo25a.html): conformal latent OOD filtering and physical robot trial. Our distinguishing achievement must be **physical execution-memory observation correctness** and task-level genuine query savings, not a broad safety claim.

## Already observed unrevised evidence (DO NOT pool across changed trajectories)

| Stage | Actual original physical result | Implication |
|:--|:--|:--|
| first ACK mixed, second held, 64 states | public 58/64 tasks with 31 private reads vs task-ID strong 58/64 with 58; zero-query held shortcut 43/64 | Real information economy in specified actual task regime |
| two real ACKs independently mixed, different 64 | 58/64 task success, 46 reads, **2/18 wrong confident history selections** | An old empirical response model can endorse the WRONG native target |
| two identical extra neutral physical actions, different 64 | paired both 48/64; one public model 41 reads vs two correlated 43; no wrong observed in either | Extra correlated public evidence did NOT improve result |
| prior max true-residual calibration, different 64 | both 58/64; narrow 51 reads, 13 confidence; conservative 53 reads, 11; both 0 wrong | Conservative radius itself did NOT improve task outcome or witnessed dangerous wrong confidence |
| retrospective original unseen residual audit of previous row | narrow true-model miscoverage 12/64 vs enlarged 6/64; both 0 wrong authority | **Coverage miscalibration != wrong authority != task failure**, three distinct endpoints |
| true physical Panda stiffness/damping shift, new 64 | [Source-frozen original registered run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37928529745) | New factual evidence MUST be read from independent physical source; no method victory before result |

## Acceptance gates for a credible main-conference submission

**Gate A — genuine innovation:** demonstrate a *load-bearing* model-validity mechanism with an identified failure set. Must outperform (or yield a nontrivial Pareto frontier against) frozen narrow observer, always-query, strong task-ID selective-query, strong zero-query/always-held, and a custom same-budget ActionShift-style active-information method. A simple threshold or multiple correlated observations producing worse frontier cannot be the centerpiece.

**Gate B — domain generality:** more than one controller response regime, one robot family and two narrow tasks. At minimum four independent task/source policy configurations, multiple actual physical native controller dynamics settings, and at least one independent robot/controller embodiment or a physically principled transfer domain. Domain shift must be **implemented and physically read back**, not just annotated in a JSON.

**Gate C — adversarial failure mechanism:** replay all original physical false-confidence negatives, plus a source-independent new prospectively chosen OOD regime where the correct candidate target lies OUTSIDE the empirical response envelope. Report all false-confidence, wrong-ACK, non-exposure, and task failures in denominator. Show *which observable physical validity cue* causes selective authorization to abstain **before** a wrong native target is acted upon.

**Gate D — cost/accounting fairness:** explicit native action steps/probe displacement, two additional XYZ readings if any, decision-time target getters, any private calibration labels from earlier simulator episodes, total inference latency, failure/refusal count and task binary success. Every baseline must be physically executed; counterfactual result splicing cannot be substituted for trajectories.

**Gate E — statistical validity:** pre-register objective hierarchy and risk criterion; matched-seed binary outcome discordance counts and exact paired uncertainty per task/shift regime, confidence bounds for wrong-conviction rate conditional on accepted predictions, cost-vs-success Pareto. Do NOT call 58/64 vs 58/64 statistical noninferiority without specified effect margin and adequately powered test. Original 0/25 confident wrong labels still leaves a nontrivial confidence upper bound.

**Gate F — genuine external scientific signal:** at least one third-party account runs unchanged code with its own **previously unseen** physical initial states and opens a concrete issue/PR with full raw results, or an independent laboratory runs and publicly attests replication. Green original-author fork CI is source reproducibility, not independent adoption. An official upstream external library software merge is separately valuable, but is not paper method acceptance.

**Gate G — publication ethics and rigor:** anonymized double-blind submission when required, genuine prior-art credit, frozen source + public raw experiments and failures, full calibration data provenance, hardware safety/packet-loss disclaimers, figures generated from raw data with axis units + source SHA, no universal certificate or L8/L9 level assertion, not a self-merged upstream claim.

## Reviewer-dangerous shortcut observations

1. Some physical ACK-truth assignment is derived from a preregistered seed parity; the *policy must never read seed, hidden fault injection truth or post-step private native target during public authorization*. Verify with a source audit and a concrete mutation test that injecting privileged truth into the policy is rejected.
2. Original reference frozen PPO source and destination controller may use different native action semantics; verify actual mapped frame and SE(3) orientation, including normalized native SO(3) BALL constraints, with source controller-only tests.
3. A t1 known-ACK anchor is **not guaranteed to predict t4 dynamics**. If stiffness/contact/phase changes *after* t1, there are indistinguishable pre-fault public histories with different future models. This impossibility counterexample is included in [public pure-Python regression](test_public_ack_authority_core.py). Do not describe earlier evidence agreement as a deterministic safety certificate.
4. PhysX gain-domain changes must apply to the SOURCE frozen PPO environment and ALL destination comparator worlds; otherwise the baseline competency/task comparison is fundamentally confounded.
5. The manuscript must credit that conformal extreme-rank bounds are conventional and **conditional on source/future residual exchangeability**; a new physical regime explicitly challenges that assumption.

## Concrete venue-ready experiment package

- **Table 1:** task/robot/policy and domain identity, fixed source/checkpoint hashes, initial reset splits.
- **Table 2:** actual task successes, private controller target reads, public observation count, extra physical probes, admitted histories and wrong confident labels for every method and physical domain.
- **Figure 1:** real native controller memory causality and two possible latent actual execution histories; **not** a vague generic VLA architecture.
- **Figure 2:** true-history response residual vs frozen envelope across before/after dynamics, calibration distribution shift, errors and early valid signal, with all true labels marked AUDIT ONLY.
- **Figure 3:** method Pareto frontier (wrong authority ↓, private getter cost ↓, real task success ↑), confidence bounds and each domain separately.
- **Figure 4:** a genuinely physically stepped failure case with exact source native command/action history, public XYZ, claimed index, actual target and authoritative readback correction.
- **Figure 5 (if genuinely supported):** independent robot embodiment or released visual policy closed-loop deployment, not an illustrative fake image.
- **Appendix:** 64 × all comparator raw native episodes per cohort, SHA256SUMS, full injected fault truth and seed coverage, honest null or negative results.

**Go/no-go rule:** If actual dynamic-shift experiments show the known-t1 anchor adds queries/observations without lowering observed wrong authority or raising task success, preserve it as a mechanistic negative result. Then explicitly refocus research onto causally informative probes or physically certified observation-regime tests; do not portray a negative anchor as a top-conference breakthrough.
