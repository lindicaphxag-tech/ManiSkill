# Novelty boundary — CRG Core v1

This artifact deliberately narrows its novelty claim.

## Already covered by prior work

The project does **not** claim novelty for any of the following in isolation:

- frozen-policy runtime recovery;
- counterfactual recovery or realignment;
- active learning for local model validity;
- Jacobian estimation or local linearization;
- trust-region reasoning;
- convex separation / support-function certificates;
- rank-one information updates;
- generic controller-space projection or safety filtering.

Relevant neighboring examples include:

- *Quantifying Local Model Validity using Active Learning* (UAI 2024), which
  actively acquires data to estimate whether a local model error stays below a
  validity threshold;
- *Imagining Recovery: Inference-Time Counterfactual Realignment for
  Vision-Language-Action Models* (2026), which performs training-free recovery
  for frozen VLAs after online disruptions;
- recent frozen-policy repair work that learns or applies runtime recovery
  mechanisms from counterfactual or failure evidence.

## Narrow surviving claim

The research question here is the **composition** of four constraints:

1. identify local policy response from controlled **physical support
   interventions** rather than only from observational uncertainty;
2. lift action-coordinate response through **controller semantics** into a
   canonical physical-command contract;
3. form a **repairability set** that combines the identified policy response,
   controller authority, and a validated locality region;
4. collect only the additional evidence needed to authorize or reject one
   concrete repair request, and carry an independently checkable rejection
   witness when possible.

The intended contribution is therefore not "active local validity" and not
"frozen-policy repair" generically. It is a **certificate-oriented physical
execution contract** for deciding whether a requested runtime correction is
supported by a frozen policy/controller stack.

## Main falsifier

If a simpler alternative using only perturbation magnitude, controller
headroom, generic local-validity estimation, or controller-space projection
matches CRG at equal false-accept rate and query cost, the flagship claim should
be narrowed or dropped.
