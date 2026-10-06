# Fatal-neighbor audit — DEC / CRG flagship

Date: 2026-10-06

This audit exists to prevent the project from turning familiar ingredients into
an inflated novelty claim.

## Surviving narrow research claim

The claim under test is **not** counterfactual probing, uncertainty, frozen-policy
repair, action-representation invariance, trust regions, or active experiment
design in isolation.

The narrow surviving question is:

> Can physical support interventions separate *identifiability* of a frozen
> policy's local response from *adequacy/locality* of that response model, and
> can a model that passes both gates support independently verifiable
> repairability / impossibility decisions under controller authority?

The current constructive chain is:

```text
physical support interventions
  -> repeated-probe DEC identifiability
  -> multi-scale local-model adequacy
  -> controller authority
  -> CRG repairability set
  -> proof-carrying repair/refusal
  -> certificate-directed next evidence
```

## Closest 2026 neighbors

### CFNBC / Counterfactual Action Sensitivity Coverage
arXiv:2607.27261

Uses task-preserving counterfactual nuisance observations and action drift to
select a compact repair dataset for robustness training.

**Overlap:** policy-specific counterfactual action sensitivity.

**Separation:** offline data selection / retraining target versus runtime
physical-support model admissibility and repairability certification.

Do not claim first counterfactual action-sensitivity probing.

### Perturbation-Based Epistemic Uncertainty for VLA failure detection
arXiv:2606.20754

Uses low-rank model/weight perturbations for training-free epistemic uncertainty
and failure detection.

**Overlap:** perturbation-based evidence and runtime uncertainty.

**Separation:** perturbing model hypotheses to detect failure versus physically
intervening on scene supports to identify a local physical response map and test
whether that map is admissible for repair.

Do not claim first perturbation-based VLA uncertainty.

### CoRe — Imagining Recovery
arXiv:2608.14822

Inference-time recovery for frozen VLAs by counterfactual imagined continuation
and realignment to a viable trajectory.

**Overlap:** frozen-policy, training-free runtime recovery.

**Separation:** trajectory/state realignment versus intervention-identified
physical repairability geometry and explicit impossibility/refusal certificates.

Do not claim first frozen-policy inference-time repair.

### Robot world models and action representation
arXiv:2609.23252

Shows that robot world models can change substantially when equivalent action
trajectories are written using different action parameterizations.

**Overlap:** action representation is part of execution semantics.

**Separation:** representation sensitivity/invariance of world models versus
semantic lifting of policy response maps and runtime physical repairability.

Do not claim first action-representation invariance problem.

### dWorldEval — action-centric robot policy evaluation
ICML 2026 / PMLR 306

Builds an action-centric world model for scalable policy evaluation and studies
failure-enriched/action-causal evaluation.

**Overlap:** reliable policy evaluation under action-conditioned dynamics.

**Separation:** learned world-model evaluation versus black-box local physical
intervention certificates.

Do not claim first action-causal policy evaluation.

## Classical ingredients that are explicitly not novel

- finite differences / Jacobians;
- multi-scale convergence and local model adequacy;
- Taylor / response jets;
- trust-region logic;
- support functions and convex separation;
- nullspaces;
- Sherman-Morrison updates;
- optimal experimental design / active learning;
- controller coordinate conversion.

In particular, the project's scale-locality gate should be described as a
runtime use of established model-adequacy logic, not a new numerical-analysis
theorem.

## Real evidence that changed the method

### Seed-17 VQ-BeT witness

Repeated DEC is deterministic, but the finite-difference map does not contract
under a smaller physical probe. The method therefore rejects the first-order
local model rather than authorizing repair.

### Frozen five-state prospective test

The richer response-jet rescue produced 0/5 upgrades and was dropped under its
pre-registered rule.

More importantly, the states populated all four combinations of:

- repeated-probe stability;
- scale locality.

This motivates a two-axis admissibility hypothesis instead of a single scalar
uncertainty score.

## Fatal tests for the surviving claim

The flagship should be narrowed or killed if:

1. one scalar uncertainty statistic routes the next experiment as well as the
   two-axis stability/locality gate;
2. generic controller-space projection matches CRG at equal false-accept rate;
3. perturbation magnitude/controller headroom predicts repair outcomes as well
   as CRG;
4. certificate-directed probing does not reduce black-box queries at matched
   decision validity;
5. independent replication finds feasible repairs in cases with valid robust
   impossibility witnesses;
6. the two-axis structure does not reproduce on a second policy family;
7. semantic lifting gives no advantage over raw action-space comparisons.

## Publication discipline

A paper should lead with the real failure boundary and the resulting problem
formulation, not with the number of internal modules.

Preferred framing:

> **When Is a Frozen Robot Policy Locally Repairable? Identifiability,
> Model Adequacy, and Proof-Carrying Runtime Repair**

The response-jet extension is not part of the flagship claim after its
prospective 0/5 rescue result.
