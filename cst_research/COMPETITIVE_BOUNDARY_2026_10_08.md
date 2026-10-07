# Competitive Boundary — 2026-10-08

This note narrows CST's novelty claim against newly surfaced public action-interface work.

## Closest public projects

### ActionABI

ActionABI treats undocumented robot action semantics as an offline forensic
inference problem.  It searches a finite grammar covering target convention,
joint/cartesian space, frame, permutation, sign, scale, lag and gripper
semantics, retains an equivalence set, emits a converter only when the evidence
supports it, and otherwise abstains.

Therefore CST must **not** claim novelty for:

- making hidden action contracts explicit;
- recovering permutation / sign / scale / target / frame / lag / gripper
  semantics from logs;
- converter-or-refusal as a generic idea;
- calibrated abstention on an underdetermined static contract.

### ActionShift

ActionShift turns the same hidden action contract into an online adaptation
benchmark.  It holds task dynamics fixed, changes the action interface, and
uses bounded probing / belief adaptation to rescue frozen policies.

Therefore CST must **not** claim novelty for:

- showing that frozen policies fail under hidden action-interface changes;
- adapting a frozen policy online to a hidden static contract;
- active probing to identify action-interface semantics;
- a benchmark whose primary axis is permutation / sign / scale / target /
  frame / lag / gripper.

## CST's remaining candidate contribution

CST should be positioned around **controller migration as a closed-loop dynamic
system compilation problem**, not hidden-ABI identification.

The intended input is not an unknown flat action grammar.  It is a pair of
concrete controller implementations plus a frozen policy.

The compiler should extract / model:

- controller action chart and physical command semantics;
- controller-owned state such as previous targets, integrators and filters;
- action saturation / clipping / interpolation semantics;
- plant-facing actuation image and local closed-loop response;
- reference ownership and chunk-lifetime semantics.

The output is:

- a state/action adapter when the declared closed-loop behavior can be
  preserved;
- an explicit validity region / finite-horizon error certificate when only an
  approximation is supported;
- an impossibility / saturation / state-handshake witness when exact migration
  cannot be realized.

The core mathematical object is therefore closer to a controlled simulation
morphism between **implemented controller+plant systems** than to recovery of a
hidden static action ABI.

## Strongest falsifiable flagship claim

> Given a frozen policy and two concrete controller implementations, compile a
> stateful migration layer that preserves a declared closed-loop physical
> behavior when feasible, and produce machine-checkable refusal evidence when
> the target controller cannot realize that behavior.

This claim only becomes strong if it is demonstrated on real stack boundaries,
not synthetic matrices alone.

## Evidence gates

Required before claiming a strong L8-level representative work:

1. ManiSkill #429 trajectory-level baseline failure and fixed replay recovery on
   the same official demonstrations.
2. Runtime implementation-to-contract extraction from real controllers.
3. A second independent maintained stack (robomimic or LeRobot) with an
   upstream review / merge or an independently reproduced integration.
4. A case where action dimensions and static metadata look compatible but a
   controller-state / closed-loop certificate correctly rejects or requires a
   stateful handshake.
5. Honest comparison against ActionABI / ActionShift showing that CST is not
   solving hidden-contract identification and does not rely on privileged
   access unavailable to those methods.

Until these gates are crossed, use **L8-candidate**, not L8 achieved.
L9 additionally requires independent adoption / reuse or strong paper-level
external recognition.
