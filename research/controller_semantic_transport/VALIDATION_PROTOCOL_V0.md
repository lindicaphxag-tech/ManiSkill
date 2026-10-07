# CST public validation protocol v0

Status: preregistered before public integration outcomes.

## P0 — deterministic semantic core

Already public:
- exact encode/decode tests;
- 5,000 randomized exact-family witnesses;
- semantic type rejection tests;
- CT-CST synthetic success / saturation / conditioning refusal tests;
- frozen 20,000-rotation chart mismatch sweep.

These validate implementation logic, not simulator efficacy.

## P1 — multi-robot exact-family semantic preservation

Goal: verify that the exact CST compiler preserves physical q_target across real ManiSkill controller objects and states.

Initial robot panel:
- Panda;
- SO100;
- UR10e;
- Unitree G1 or another high-DoF robot exposing both joint-position modes.

Controller pairs when available:
- pd_joint_delta_pos -> pd_joint_pos;
- pd_joint_pos -> pd_joint_delta_pos;
- pd_joint_target_delta_pos -> pd_joint_pos;
- pd_joint_pos -> pd_joint_target_delta_pos;
- delta-current <-> delta-target.

Sampling per robot:
- at least 50 valid controller states;
- interior and near-bound source actions;
- target actions only counted as executable when CST says representable.

Primary metrics:
- semantic residual ||q_target_source - q_target_reconstructed||;
- accepted coverage;
- false-accept rate: certificate accepts but residual > 1e-6 rad/m-equivalent joint units;
- target saturation/refusal rate;
- naive native-tensor-copy residual.

Promotion gate P1:
- median and p99 accepted semantic residual <= 1e-6;
- zero observed false accepts in the frozen panel;
- refusals correspond only to missing hidden state or target unrepresentability.

## P2 — public trajectory replay

Goal: test whether semantic equality at the controller goal level preserves recorded behavior.

Use public ManiSkill trajectories and exact reset states.  Compare:
- current upstream converter;
- minimal #429 bugfix branch;
- exact CST transport;
- naive tensor copy where shape permits.

Report for every episode:
- original task success;
- converted task success;
- state-trajectory RMS and maximum divergence;
- controller target residual;
- number of saturated or refused actions;
- conversion runtime.

No episode may be dropped silently. Conversion failure and task failure are separate outcomes.

Promotion gate P2:
- #429-like failure is reproduced on the upstream base;
- the patch/CST removes the controller-semantic error;
- task success is not lower than the source trajectory beyond a preregistered tolerance;
- any remaining divergence is analyzed as dynamics/controller mismatch rather than hidden by retry filtering.

## P3 — cross-family CT-CST

Goal: evaluate controller pairs that do not share an analytic semantic normal form.

Candidate pairs:
- joint position -> joint velocity;
- joint position -> Cartesian position;
- joint position -> Cartesian pose;
- Cartesian delta-current -> Cartesian delta-target where frame/IK details differ.

Every target-oracle query must restore the same simulator state and target-controller hidden state.

Frozen CT-CST authority gates:
- max relative trace residual: 0.05;
- max local Jacobian condition number: 1e6;
- minimum normalized saturation margin: 0.01;
- minimum improvement over initial target action: 0.20;
- default maximum Gauss-Newton iterations: 8.

Primary metrics:
- accepted coverage;
- accepted-case held-out trace residual;
- false-accept rate under held-out simulator rollout;
- task progress/success after converted action;
- policy/controller query cost;
- refusal causes.

Critical calibration plot:
certificate score / residual versus actual held-out rollout divergence. The certificate is useful only if acceptance separates safe-ish transport from harmful transport.

## P4 — #1138 / #1495 task-level factorial

PegInsertionSide Diffusion Policy is the maintainer-requested task-level validation.

Use a 2x2 factorial:
- old converter chart + old controller sign;
- fixed converter chart + old controller sign;
- old converter chart + fixed controller sign;
- fixed converter chart + fixed controller sign.

Freeze across all four cells:
- identical demo set;
- identical seeds;
- identical training steps;
- identical evaluation episodes;
- identical model architecture and hyperparameters.

Report learning curves and final success with per-seed values, not only best run.

## P5 — second-stack reproduction

Target: robomimic / robosuite because public issue #270 explicitly requests inverse absolute/delta conversion and robosuite has independent history of reference-frame / goal-update semantic bugs.

Required result:
- same CST type fields explain at least one independent stack's action semantics;
- either exact compiler or CT-CST detects / prevents a real conversion error;
- external maintainers can reproduce from public code.

## Evidence promotion rule

P0 cannot substitute for P1; P1 cannot substitute for P2; P2 cannot substitute for P3/P4 task evidence; none can substitute for external maintainer retention.

This protocol may be versioned only before the corresponding outcome is inspected. Any post-outcome change must be documented as exploratory rather than preregistered evidence.
