# CST novelty audit

Status: **working boundary, not a priority claim**.

## What is not novel

CST does not claim novelty for:

- absolute versus delta actions;
- joint-space versus task-space actions;
- affine coordinate transforms;
- pseudoinverse-based least-squares maps;
- interval propagation through affine maps;
- controller equivalence / simulation / refinement as a general formal idea;
- symbolic controller refinement or feedback refinement relations;
- trajectory interpolation;
- runtime clipping or saturation analysis.

Feedback Refinement Relations and related abstraction-based control literature
already provide rigorous notions under which controllers synthesized for one
system/abstraction can be refined to another system. CST should be positioned
as an application-specific semantic compiler for robot-learning software
interfaces, not a replacement for that theory.

Large-scale 2026 robot-learning work also establishes that action-space choice
itself materially affects learning and deployment. CST therefore cannot claim
that action representation is an overlooked phenomenon in general.

## Narrow research hypothesis

Modern robot-learning software exposes action interfaces whose semantics are
distributed across:

- policy-visible native action normalization;
- measured robot state;
- controller-owned hidden targets / references;
- interpolation over simulator or control substeps;
- saturation and joint/task limits;
- controller-specific action charts.

A dataset or policy converter can be wrong even when tensor dimensions and
endpoint action values appear valid.

CST tests the narrower hypothesis that these implementation semantics can be
compiled into an executable intermediate representation that:

1. distinguishes endpoint-goal agreement from full command-trace agreement;
2. includes controller memory needed for compositional multi-action semantics;
3. compiles exact affine morphisms over an entire action/context region when
   the target interface can represent them;
4. proves target native-bound containment over that full region;
5. identifies piecewise boundaries such as robosuite qpos clipping and refuses
   a single affine certificate when the region crosses them;
6. emits an executable transport formula rather than only a relation witness.

## Evidence needed before a strong claim

A strong paper claim requires all of:

- parity between the IR and at least two real controller implementations;
- at least one externally reported conversion defect whose mechanism CST
  predicts;
- exact and negative / non-representable examples;
- public frozen tests with no outcome-driven tolerance tuning;
- a second independent software stack;
- ideally one maintainer-retained upstream use.

Plant/contact/task equivalence remains outside the current theorem boundary
unless dynamics are explicitly lifted into the semantic observable.

## Current evidence boundary

Supported:
- ManiSkill PDJointPosController host parity;
- exact/goal-only distinction;
- whole-action-box affine certificate;
- contextual action x state-region compiler;
- analytic bound refusal;
- robosuite semantics adapter implemented; pinned host parity is under CI.

Not yet supported:
- task-success preservation;
- nonlinear IK branch certificates;
- force/torque trace equivalence;
- external maintained adoption;
- broad controller-refinement theory novelty.
