# CST novelty audit — 2026-10

Status: conservative working audit, not a novelty proof.

## Close prior directions

### Action-space design studies

Demystifying Action Space Design for Robotic Manipulation Policies (2026) systematically studies absolute vs delta and joint-space vs task-space choices at large real-robot scale.

Implication: CST cannot claim that action representation matters, that delta and absolute behave differently, or that joint/task-space choices affect learning.

### Implicit Kinematic Policies (2022)

IKP combines joint and Cartesian action representations inside a learned policy through differentiable kinematics.

Implication: CST cannot claim that multiple action spaces can be unified or related through kinematics in general.

### Robot / hand retargeting

Recent retargeting work maps human or source morphology motion into executable robot motion, often with kinematic/geometric objectives or optimization.

Implication: CST cannot claim trajectory retargeting, IK-based translation, or constrained action optimization broadly.

## Narrow CST hypothesis that remains to test

The current research wedge is:

> For already-trained / already-defined robot controller interfaces, action conversion can be compiled by an explicit semantic type system. Exact families are transported through a physical normal form and fail closed on missing hidden state or unrepresentability. Cross-family conversions are compiled by exact-state counterfactual physical-trace matching and receive execution authority only when residual, conditioning and saturation gates pass.

The potentially distinctive combination is therefore:

- controller-interface semantics rather than policy action-space selection;
- explicit hidden controller state as part of action meaning;
- exact-vs-approximate transport decided before execution;
- counterfactual same-state trace compilation for cross-family interfaces;
- fail-closed authority based on representability / conditioning rather than unconditional conversion.

## Claims explicitly not allowed

- first work to study robot action spaces;
- first absolute/delta conversion;
- first joint/Cartesian unification;
- first trajectory matching;
- first retargeting;
- first use of Gauss-Newton or finite-difference Jacobians;
- first simulator-based action optimization.

## What would make the research contribution real

A broad method claim requires evidence that CST predicts something existing conversion code does not:

1. exact-family compiler fixes or predicts a public upstream failure;
2. semantic type rejection identifies controller pairs where naive conversion fails;
3. CT-CST succeeds on some cross-family public pairs while refusing genuinely unrepresentable or ill-conditioned pairs;
4. certificate acceptance predicts rollout/task preservation under held-out states;
5. behavior transfers to at least a second robot software stack;
6. an external maintainer retains either the conversion, semantic contract test, or API.

Until those gates are met, CST is a method candidate anchored by real upstream problems, not a claimed state-of-the-art system.
