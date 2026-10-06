# Fatal-neighbor audit — certification-oriented physical repairability — 2026-10-06

This note narrows the flagship claim after reviewing the closest adjacent work.
It is intentionally conservative: if a neighboring paper already owns a broad
idea, that broad idea is removed from the novelty claim.

## 1. Active learning for local model validity

**Lämmle et al., UAI 2024 — “Quantifying Local Model Validity using Active Learning”**
https://proceedings.mlr.press/v244/lammle24a.html

Already established:
- local, prediction-specific model-validity regions rather than only global error;
- adaptive data acquisition to reduce the cost of deciding local validity;
- acquisition concentrated near a validity boundary.

Therefore this project does **not** claim:
- first active learning method for local model validity;
- first use of additional samples to resolve a local validity decision.

Remaining distinction under test:
- the object being certified is a **physical repair request** for a frozen robot
  policy, not generic surrogate prediction validity;
- evidence is collected through controlled physical support interventions;
- the runtime output is constructive and operational:
  CERTIFIED_REPAIR / CERTIFIED_IMPOSSIBLE / INCONCLUSIVE;
- the certificate is coupled to controller authority, repairability geometry,
  proof-carrying impossibility, and explicit refusal to execute.

## 2. Task-informed active system identification

**Aoyama et al., 2026 — “Learning Task-Informed Exploration Policies for Active
System Identification”**
https://openreview.net/pdf?id=OaNJs5XsYs

Already established:
- task-relevant physical-property identification;
- exploration chosen according to downstream task sensitivity;
- active probing before irreversible task execution.

Therefore this project does **not** claim:
- first task-aware active system identification in robotics;
- first robot exploration policy that values information by downstream utility.

Remaining distinction under test:
- no learned exploration policy is required;
- the target is not full latent physical-property recovery;
- the query objective is the **minimum evidence needed for one repairability
  certificate**;
- the system may terminate with a proof-carrying impossibility or local-model
  rejection instead of a property estimate.

## 3. Test-time physical diagnosis may collect evidence a frozen policy never uses

**Zhang, 2026 — “When Does Test-Time Physical Diagnosis Pay? A Frozen Policy
Buys Evidence It Never Reads”**
https://arxiv.org/abs/2609.22299

Already established:
- successful physical diagnosis does not imply that a frozen policy uses the
  acquired evidence;
- evaluation should separate reference quality, identifiability, evidence use,
  decision value, selection value, and safe realization;
- richer evidence can be informative yet operationally useless.

This is a close conceptual neighbor and strengthens the need for explicit
evidence-action authority.

Therefore this project does **not** claim:
- first observation that frozen robot policies can ignore diagnostic evidence;
- first decomposition of test-time diagnosis into multiple failure links.

Remaining distinction under test:
- CRG does not ask the frozen policy to “read” a diagnostic trace;
- diagnostic evidence constructs an external repairability object and runtime
  authorization decision;
- the evidence router distinguishes repeated-evidence insufficiency from
  unsupported local geometry;
- execution is refused if evidence does not justify a repair.

## 4. Frozen-policy test-time guidance and recovery

Representative 2026 neighbors include:
- TraceFlow — frozen flow-policy guidance from success/failure traces:
  https://arxiv.org/abs/2609.20646
- Guided Action Flow — critic-guided inference for frozen flow-matching VLA:
  https://arxiv.org/abs/2607.02092
- Physical Agency / orchestration around frozen policies:
  https://arxiv.org/abs/2607.21725

These already occupy broad claims such as:
- frozen-policy runtime correction;
- test-time guidance without weight updates;
- external orchestration / recovery around a frozen policy.

Therefore this project does **not** claim:
- first frozen-policy runtime adaptation;
- first no-finetuning recovery layer;
- first external runtime correction around a frozen policy.

## Surviving flagship claim

The narrow claim worth testing is:

> **A frozen robot policy’s local physical repairability can be identified from
> controlled counterfactual interventions, and a runtime can use that evidence
> to certify repair, certify impossibility, request only decision-relevant
> additional probes, or refuse the local model when locality itself is
> unsupported.**

The strongest subclaim is not “active probing” by itself. It is:

> **certificate-oriented system identification for physical repairability,
> coupled to source-of-uncertainty routing and fail-closed execution.**

## Current real-policy evidence boundary

VQ-BeT / PushT:
- repeated-probe stochastic radius approximately zero;
- local finite-difference map fails scale-contraction gate;
- first-order local model is rejected under a preregistered protocol.

Diffusion / PushT:
- same physical protocol;
- repeated-seed DEC instability is nonzero and materially larger;
- robust CRG remains inconclusive under a much larger empirical uncertainty
  envelope.

This policy-family contrast is evidence that “uncertainty” should not be
collapsed into one scalar source. It is not yet external validation.

## Kill criteria after this audit

Drop or narrow the flagship claim if fair experiments show any of:

1. a standard local-validity active-learning method reaches terminal decisions
   with equal or fewer black-box policy queries at matched false-accept rate;
2. task-informed active system identification followed by a generic projection
   matches CRG on repairability decisions;
3. uncertainty-source routing does not beat a scalar uncertainty threshold;
4. certificate-directed probing gives no query advantage over fixed/coded
   probing;
5. fail-closed locality rejection discards corrections that execute reliably at
   a materially higher rate than its safety benefit justifies;
6. a second policy family does not support the same repairability abstraction;
7. independent replication fails to reproduce any separation between
   repeatability, locality validity, and repairability.

## Novelty discipline

The project does not claim invention of:
Jacobian estimation, active learning, local model validity, system
identification, Taylor models, nullspaces, convex separation, support
functions, runtime recovery, or frozen-policy guidance.

Any paper draft should keep those as foundations or related work, not novelty
claims.
