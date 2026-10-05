# Controller-Semantic Transport (CST)

Status: research method candidate; exact joint-position family implemented.

## Core problem

Robot-learning systems often convert actions as if an action were only a tensor.
In a real controller, the same numbers can mean different physical commands
because interpretation depends on normalization, current robot state, prior
controller targets, rotation charts, IK, interpolation and actuator dynamics.

CST defines action conversion as semantic transport instead of tensor mapping.

For controller A with hidden state z_A and controller B with hidden state z_B:

    T_A_to_B(u_A; z_A, z_B)
      = encode_B(decode_A(u_A, z_A), z_B)

Version 0 uses physical target joint position q_target as the semantic normal
form for the exact joint-position family.

## Exact family implemented now

- absolute joint-position target
- delta from current joint position
- delta from previous controller target

The third case is explicitly stateful. Delta-current and delta-target are not
interchangeable labels:

    delta-current: q* = q_current + delta_q
    delta-target:  q* = q_target_previous + delta_q

If q_target_previous is missing, CST refuses to interpret the action.

## Certificate

A transport is accepted only when:

1. the source action decodes to a finite physical target;
2. that target lies inside the target controller's native action image;
3. target encode then decode reconstructs the same physical target within the
   frozen semantic tolerance.

The certificate therefore distinguishes exact transport from saturation or
semantic mismatch before rollout.

## Public upstream anchor

ManiSkill issue #429 reports 0% success for pd_joint_delta_pos to pd_joint_pos
trajectory conversion. The current conversion path exhibits the bug class CST
was designed to expose: a normalized delta action is converted to a physical
target qpos, and the physical qpos is then passed directly to a normalized
absolute-position controller, where it is interpreted as a native normalized
action again.

A separate minimal branch keeps that upstream bug fix small. This branch
generalizes the mechanism.

## Why this is more than the single bug

The research object is the controller action chart, including hidden controller
state and representable image. The immediate questions are:

- which controller pairs are exactly transportable?
- which pairs require hidden state?
- which target goals are not representable without clipping?
- when does a numerically plausible conversion preserve task-level behavior?
- can a certificate predict replay failure before simulation?

## Non-claims

CST v0 does not call the following exact:

- joint position to joint velocity
- joint to Cartesian pose
- IK-to-IK across different solvers
- torque to kinematic targets
- controllers with materially different interpolation or actuator dynamics

Those need a richer semantic normal form, such as low-level target traces,
reachable sets or rollout-equivalence certificates.

## L8 promotion gate

CST becomes an L8-level result only after all of the following are evidenced:

1. at least one acknowledged upstream conversion failure is fixed;
2. exact-family certificates predict success and failure across multiple
   controller pairs;
3. false accepts are near zero under frozen thresholds;
4. approximate-family certificate strength predicts trajectory or task
   preservation;
5. at least two independent robot stacks reproduce the semantic bug class;
6. at least one external maintainer retains the fix, contract test or API.

## L9 promotion gate

L9 additionally requires independent reuse or a strong publication / challenge
result showing that controller-semantic transport is a reusable robotics
abstraction rather than one repository's patch.
