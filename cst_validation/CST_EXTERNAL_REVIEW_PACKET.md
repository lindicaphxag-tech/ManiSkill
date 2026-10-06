# Controller-Semantic Transport — External Review Packet

Status: **research artifact; not an upstream endorsement**.

## One-sentence problem

Robot action tensors can be shape-correct and numerically reversible while
encoding the wrong controller semantics. CST asks whether a source action can
be translated into a target controller while preserving the **commands the
controller actually emits**, including normalization, measured-state anchors,
hidden target state, interpolation and saturation.

## Externally reported trigger

ManiSkill issue #429 reports 0% success for
`pd_joint_delta_pos -> pd_joint_pos` replay.  The clean candidate fix is kept
separate from this research branch:

- upstream base: `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3`
- clean patch branch: `fix/issue-429-clean-v2`
- patch footprint: production conversion file + focused regression test only.

The concrete semantic chain is:

    normalized source action
      -> physical delta q
      -> physical target q
      -> target-controller native action

A fork CI has already run the same focused regression against the frozen
upstream base and the patch: base fails, patch passes.  This is patch evidence,
not maintainer adoption.

## What CST adds beyond the bug fix

CST represents one controller period as

    trace  = T_u u + T_x x + T_z z + t
    goal   = G_u u + G_x x + G_z z + g
    z_next = H_u u + H_x x + H_z z + h

and distinguishes:

- exact command-trace equivalence;
- endpoint-only agreement;
- bounded approximation;
- source information projection;
- target ambiguity;
- local non-representability.

For a non-representable linearized relation it can emit a concrete primal and
dual witness

    v: source semantic direction
    w: separating observable

with

    w^T B = 0
    w^T A v != 0,

so failure is a checkable non-existence certificate, not merely a failed
optimizer call.

## Independent implementation evidence

### ManiSkill

Pinned host tests match `PDJointPosController` semantics, including
normalization, current-relative vs target-relative modes and interpolation.

### robosuite

Pinned `JointPositionController` parity checks delta/absolute goal semantics.
The piecewise compiler also matches real qpos saturation over 2000 random
action/state samples, including samples that actually cross a clipping
boundary.

### LeRobot differential witness

Pinned LeRobot PI0.5 proprioceptive-memory metadata orders history offsets from
oldest to current, ending in delta 0.  The shared relative-action helper
currently collapses a rank-3 state tensor with `state[:, 0]`, while PI0.5's
own prompt preparation uses `state[:, -1]` as current.

A constructed multi-frame witness demonstrates why an ordinary
relative->absolute round trip cannot detect a wrong temporal anchor: subtract
and add the same wrong history slot and the tensor round-trips exactly.

This is currently a **differential semantic witness**, not an upstream bug
claim; maintainer confirmation is required before promotion.

## Automatic black-box extraction

The current research branch also contains a fail-closed affine semantic
identifier.  It probes a resettable controller oracle at designed
action/state/hidden-state points, reconstructs a candidate `StatefulTraceIR`,
then validates it on fresh held-out probes.

A controller that is clipped, nonlinear, hysteretic or otherwise outside the
single-affine model is rejected rather than silently assigned a converter.

System identification itself is prior art.  The CST claim is the software
pipeline from controller implementation -> semantic IR -> transport/refusal
certificate.

## Public task gate

The frozen task-level protocol uses the official ManiSkill `PickCube-v1`
teleoperation demonstration:

    official pd_joint_pos demo
      -> pd_joint_delta_pos
      -> pd_joint_pos

The second leg is exactly the #429 direction.  The same generated intermediate
trajectory is replayed with the frozen upstream base and the clean patch.  The
promotion rule is strict: the fix must complete without crashing and achieve
more successful replays than the base.

Rendering is explicitly disabled and state observations are used, so the gate
tests simulation/controller/task behavior rather than Vulkan availability.

**No task-level improvement is claimed until this gate produces a completed
machine-readable artifact.**

## Claim boundary

CST does **not** claim to invent:

- absolute/delta or joint/task action spaces;
- affine system identification;
- pseudoinverse transport;
- controller refinement / simulation relations;
- stateful transducer mathematics;
- clipping or saturation analysis.

It also does not yet claim plant/contact trajectory equivalence, arbitrary
nonlinear IK equivalence, safety, or external maintained adoption.

## Fast external-review path

For the narrow ManiSkill contribution, review only
`fix/issue-429-clean-v2`.  The research branch is supporting evidence and is
not intended to be merged into ManiSkill.

For research review, the evidence order is:

1. externally reported failure (#429);
2. minimal base-fail/fix-pass patch;
3. host-semantic parity in ManiSkill;
4. independent robosuite parity;
5. LeRobot temporal counterexample;
6. public task round-trip;
7. maintainer-retained upstream use.

This ordering is intentional: no later research claim is used to justify an
earlier production patch.
