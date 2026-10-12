# Bounded-response active ACK probe design (research candidate)

**Status:** source/test prototype; no new native PhysX experiment, original
task-success improvement, real-world sensor validation, or official upstream
ManiSkill adoption is claimed.

## Mechanism

For each hidden action-execution history h, a *common prospective candidate*
native probe has a predicted hidden target `m_h(a)`. Conditional on an
**independently validated** response contract, the publicly observed next XYZ
is in

`S_h(a) = { x + alpha (m_h(a) - x) : alpha in [alpha_min, alpha_max] } + B(epsilon)`.

Here `B(epsilon)` is a 3D model-and-sensor-error ball, **not an empirical
confidence interval**. For candidate action a, calculate

`gap(a) = min_{h != h'} distance(Segment_h(a), Segment_h'(a)) - 2(epsilon + guard)`.

If `gap(a) > 0`, the response sets are pairwise disjoint, so an observation
inside the assumed true-history response set cannot also belong to another.
Select only an admissible, pre-outcome candidate that maximizes
`gap(a) / action_cost(a)` under a frozen action budget. Otherwise abstain.

The exact finite-segment separation minimization is a convex quadratic over
two scalars in [0,1]. Its solution lies at an interior stationary point or on
one of four edges; the implementation checks both, including parallel,
collinear, and degenerate cases. Cost does **not** imply safe execution.

## Existing evidence / falsification

- Local CPU suite: 8 tests passed, including 100 independent dense-grid
  comparisons against the geometric minimizer, misleading-overlap
  counterexample, monotonic noise rejection, multiple histories, admissibility
  and strict-budget checks.
- This prototype **does not estimate** alpha, epsilon, actuator admissibility,
  action costs, or `m_h(a)` from real robot state. Caller-supplied attestation
  booleans cannot themselves authenticate those assumptions.
- Prior original native PhysX 1280-world factorial results are related
  motivation only, **not results obtained using this algorithm**.

## Mandatory prospective original-experiment gates

1. Precommit candidate native action set, physical cost units, matched
   two-policy/ACK histories, native dispatched action logs, and an
   independently estimated response envelope on disjoint calibration states.
2. Execute the SAME selected predecision action under every paired truth and
   comparator. Verify actual controller target + achieved SE(3) prefix match
   before attributing any post-probe difference to the new estimator.
3. Compare zero-probe, fixed nonzero-probe, arbitrary candidate, active
   geometric-margin selector, and authoritative target getter at equal
   public sensing, action, time and privileged-read budgets.
4. Measure exact wrong-confident history identifications, abstention, private
   target reads, contacts, full task success and cluster-aware uncertainty
   across disjoint resets. Report non-identifiable histories and failed
   envelope calibrations as explicit negative evidence.
5. No safety or generalization claim absent fresh cross-robot and held-out
   controller-policy validation.

The engineering goal is to transform observed *passive non-identifiability*
into a falsifiable **action-conditioned hypothesis separation method**; its
novelty and value must still be demonstrated against established active
system-identification and set-membership methods.


## CRITICAL prior physical negative control (must not be omitted)

A **previously completed and precommitted** Panda+xArm6 original PhysX study
ran 16 reset clusters x two actual hidden ACK truths x two executed probes
(zero versus fixed +0.15 native X), producing 64 test worlds.
Both probes recovered **32/32 correct histories**, with zero wrong-confident
answers, zero abstentions, and 32/32 corrected native target XYZ.
The nonzero arm increased average observed separation by only ~0.415 mm
(Panda) and ~0.444 mm (xArm6) and **did not improve any decision**.
Source: `research/frozen_policy_transfer/ZERO_VS_NONZERO_PROBE_PANDA_XARM6_ORIGINAL64_RESULTS.md`.
This is scripted native control, not learned PPO/VLA task success, and does
not independently calibrate a deterministic physical-response envelope.

**Null certificate added in this branch:** For
`y_h(a) = x + alpha*(m_h(0) + u(a) - x) + e_h` with fixed shared
`alpha`, history-independent common shift `u(a)`, and action-invariant
bounded noise support, every pair of response centers has separation
`alpha*(m_h(0)-m_k(0))`, independent of the probe. Thus an expensive
common probe cannot improve ideal observation-ball pairwise separation.
The module explicitly tests the common-shift assumption and refuses the
claim when the physical gain/noise assumptions lack external attestation.
This identity is elementary algebra **not claimed to be a new theorem**.
It does not extend unchanged to uncertain shared gain, contact dynamics
or history/action-dependent nonlinear response distributions.

**Scientific consequence:** A positive gain from the new method requires
an action that changes history-*relative* observability under a genuinely
measured response model, not an arbitrary translation of the targets.
Under the old high-SNR Panda/xArm6 task, there is no room to improve the
32/32 classification count. Any new experimental protocol must first
prospectively demonstrate nontrivial baseline ambiguity and equalize or
explicitly charge actuation magnitude, sample timing, sensing, energy,
privileged target reads, and repeated correlated reset states. If these
gates cannot be met, report a negative result rather than an L10 claim.


## Source-faithful candidate generation and action-dependent observability

The original `Candidate.targets` API was a **pure geometry oracle**: users
could invent arbitrary, history-conditioned targets that no single 6D robot
command could produce. This is unsuitable as a robotic efficacy claim.

The new `research/ack_native_probe_source_adapter.py` **always replays one
identical native 6D command** through the existing, separately published
`ActionHistoryObserver`, once for each distinct initial commanded-target
history. For the supported root-frame relative-target translation, its
reconstructed XYZ displacement is identical in all histories, regardless of
their hidden prior position and initial orientation. A forged synthetic
history-dependent target gap is now explicitly rejected by
`verify_candidate_against_native_source`. Predictor-source fidelity does
NOT certify the real controller, actual motion, contact or response dynamics.

The new `research/ack_action_envelope_selector.py` is the minimal logically
permissible *conditional* extension: a **separate independently supported**
response-gain interval and absolute sensor/model uncertainty are required
for EACH physically source-valid action. Missing, borrowed or unattested
per-action envelopes cannot authorize the probe. Among admitted candidates,
the selection uses the same robust separation margin and declared action
cost. The caller cannot turn an unknown physical energy expenditure into a
measured budget by setting `declared_action_cost`.

**Synthetic mathematical falsifiers**:
- With identical fixed gain and noise for both native actions, the lower-cost
  zero probe wins; a common translation alone has no pairwise separation
  gain.
- With hypothetically *independently calibrated* gains 0.4 for zero and 0.9
  for nonzero, a 0.04 m hidden-target gap and 0.009 m error envelope give
  nonseparation for zero but a positive 0.018 m conditional separation margin
  for a source-legal nonzero action. This is **NOT an observation from PhysX**,
  and no actual robot calibration substantiates these particular numerical
  gains.

Thus any real novel advantage must be attributable to a *measured action
response change* (gain, nonlinear contact, orientation/sensing interaction,
or calibrated uncertainty), not to fabricated controller-target predictions.
This is the falsifiable mechanism tested in the prospective design.


## Recent external work and hard novelty boundaries (checked 2026-10-13)

- [ActionShift / DualABI](https://github.com/Archerkattri/actionshift)
  already uses finite-contract belief updates, bounded active probes and
  task-regret-aware probe choice under hidden **action-interface semantics**.
  Choosing informative actions or maintaining beliefs is **not a first-ever
  contribution** here. Unknown **past execution ACK and persistent hidden
  commanded-target memory**, not unknown permutation/sign/frame grammar,
  distinguishes this study's problem specification.
- [Observable quotient world models for knowledge-state abstraction under
  partial observability](https://doi.org/10.1016/j.knosys.2026.116768),
  *Knowledge-Based Systems*, 9 October 2026, explicitly studies
  action-conditioned observation laws, quotient beliefs and information
  gain. Observational equivalence and action-conditioned uncertainty
  reduction are **not our new conceptual primitives**. The candidate
  contribution here is a narrow, testable source-correct finite-controller
  ACK-state decision rule coupled to action-specific physical response
  evidence, without claiming to beat that learned world-model framework.

A future method paper must demonstrate that controller-memory ambiguity,
the source-correct action constraint, and the physical cost/false-authority
tradeoff create measurable new value beyond strong active-system-ID
and task-regret-driven baselines. Without that evidence the present
method is a well-scoped engineering/research prototype, not L10 theory.


## Conditional minimax value-of-information gate (2026-10-13)

A new CPU-only `research/ack_robust_readback_value.py` module turns the
**negative physical probe result** into a prospectively falsifiable
*probe versus authoritative target readback versus abstention* decision.
It addresses **binary** prior-ACK histories and **binary** calibrated
public signals; it is not yet a multi-history active VLA planner.

Let `p=P(ACK applied)`, `a=(1-p)*C(false applied)`,
`b=p*C(false held)`, and `q_h=P(Z=1|hidden history h, candidate action)`.
With an observation the Bayes error loss is

`R(q_held,q_applied)=min(a*q_held,b*q_applied)+min(a*(1-q_held),b*(1-q_applied))`.

When each `q_h` is only known within an independent **held-out calibrated
probability interval**, worst-case `max_q R` is obtained by a **four-variable
linear program**, not by naively maximizing over the corners: `R` is a
concave piecewise-linear function. For example, `q_held in [.2,.6]`
and `q_applied in [.4,.8]` have worst classification risk **0.5**
with balanced binary history prior and unit misclassification costs,
but all four rectangular corners yield at most **0.4**. Corner-only
optimism would falsely authorize a low-value probe.

The method compares declared, *independently verified* nonzero probe costs
plus robust post-observation loss against the trusted-readback cost, a
calibrated no-probe prior decision, and explicit abstention. It enforces a
strict maximum acceptable expected wrong-classification loss. It requires
source-replayed single native action provenance, a genuine disjoint
calibration receipt, a calibrated action-cost interpretation, and
independently authoritative target-read semantics. Every undecidable
situation may return `READBACK` or `ABSTAIN`; the return value is an
**action choice**, never proof of a correctly inferred history.

**What remains unproven:**

- The 48-world Panda/xArm6 pilot provides *raw public XYZ pair differences*
  for fixed probes. It does **NOT** estimate or validate any conditional
  `P(Z|ACK,action)` on held-out resets. Therefore **none** of those data
  are passed as attested likelihoods into this decision engine.
- The tests use explicitly synthetic probabilities, costs, and provenance
  flags. These are mathematics/implementation tests, not empirical active
  decision improvements or deterministic controller safety certificates.
- The rectangular probability uncertainty model, sensor symbolization,
  true readback availability, loss calibration and policy effects need
  prospective external verification before any performance assertion.

Existing Bayesian experimental design and robust classification already
study value of information; **the LP is not asserted to be a new theorem**.
The potential specific research contribution is connecting real hidden
*past execution acknowledgement and persistent controller memory* to
action-source provenance, robust decision risk and physically matched
action/readback budgets in one non-privileged manipulation experiment.
If strong fixed probing / calibrated readback baselines match it, report
the negative result and do not claim method superiority.


## Familywise finite-sample calibration — never certify from 4 resets

The risk-based probe/readback selector requires interval-bounded
`P(Z=1 | ACK history, prospective native action)`. The initial prototype
accepted those bounds from callers; that is **not a statistical certificate**
and could hide invented confidence intervals.

`research/ack_finite_sample_signal_calibration.py` now constructs exact
two-sided **Clopper–Pearson binomial intervals** from an enumerated original
calibration denominator, for *both* held/applied histories under *every*
frozen candidate action. Allocate family error probability
`delta/(2*K)` to each of `2*K` marginal intervals (K actions) by the
Bonferroni union bound, yielding at least `1-delta` simultaneous
coverage **conditional on iid independent reset-level Bernoulli outcomes,
a precommitted binary observation rule, and no reused evaluation resets**.
A SHA256 digest preserves the source arithmetic; it does NOT authenticate
real robot logs or independence. The code refuses duplicated, missing,
mixed-ACK or evaluation-overlapping reset rows; no posthoc candidate
subsetting is covered without a new error budget.

CPU adversarial/coverage tests enumerate exact discrete binomial sampling
distributions and demonstrate a key decision effect:

- A synthetic four-reset dataset with perfect apparent separation produces
  very wide intervals and forces **trusted READBACK**, not unsupported
  confident active probing.
- A synthetic one-hundred-reset iid dataset with the same apparent outcomes
  gives tighter intervals, and the conditional robust risk engine can select
  a legal, independently cost-calibrated probe under a declared risk cap.
- This is a finite-sample uncertainty *mechanism*, not measured physical
  success. The 48-world Panda/xArm6 pilot had only four separate reset
  clusters per robot, did not precommit a binary signal threshold, and is
  **NOT reused as a positive calibration set**.

Clopper–Pearson confidence intervals, multiple-comparison corrections and
robust Bayesian decisions are existing statistical concepts, NOT new
theoretical inventions. The research hypothesis is whether connecting
source-faithful hidden target-memory uncertainty, disjoint physical
calibration, and risk-constrained query allocation improves real robot
operation relative to a mandatory trusted target read and fixed probes.
Without a genuinely independent held-out native PhysX experiment, this
remains a transparent, CPU-validated algorithm *candidate*.


## Prior-shift robustness and executable no-probe history

The original risk selector treated the ACK execution prior as a single
externally declared probability, which could make a calibrated binary probe
appear safe even when ACK delivery prevalence changes between acquisition
and deployment. It also returned `NO_PROBE` without the actual fixed
`HELD` or `APPLIED` policy needed for execution.

The backward-compatible optional `prior_applied_interval=[p_lo,p_hi]`
now evaluates **one frozen deterministic decoding rule** against all
priors in that interval *and* all independently bounded observation
likelihoods. There are exactly four deterministic binary `Z -> ACK`
rules. For each one, expected misclassification loss is multi-affine in
`(p, q_held, q_applied)`, so its maximum over the declared product
interval occurs at a vertex. Minimize those four worst losses; enforce
the same action/risk budgets against the winning risk. For `NO_PROBE`,
choose the single minimax history label under the entire interval.
This avoids incorrectly comparing a different post-hoc MAP decision
for every possible prior after the actual episode.

Synthetic, independently enumerated 300-rectangle tests check the exact
worst-case risk of the emitted decoder. In an explicit adversarial
counterexample, nominal `p=.5`, conditional public-signal likelihoods
`P(Z=1|HELD)=.01` and `P(Z=1|APPLIED)=.8` imply a fixed-decoder
error risk of `0.105`. At `p=.95`, the **same fixed decoder** has
error risk `0.1905`. Under a declared `0.12` risk cap, a probe
authorized using only the nominal prior is therefore refused when
`p in [.5,.95]` is the stated uncertainty, and the selector instead
uses independently authoritative READBACK if available and cheaper
than abstention. This is a **synthetic decision counterexample**, not
a measured robot prior shift or method-success outcome.

Both the **prior support interval** and the per-action observation
probability intervals require external, disjoint, population-relevant
calibration. This implementation does NOT estimate a prior interval
from the 48 previously completed PhysX worlds. A nominal user flag or
hash cannot prove stationarity, actual hardware safety or per-decision
correctness. Mathematical prior/likelihood robustness is established
decision theory, not a claimed original theorem; research value would
depend on prospective physically valid cost reductions and task outcomes.
