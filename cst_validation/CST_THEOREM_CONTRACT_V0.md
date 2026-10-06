# Controller-Semantic Transport (CST): theorem contract v0

Status: **research theorem contract; joint-position charts only**.

This document states exactly what the current CST implementation is allowed to claim. It is intentionally narrower than "controller conversion is solved."

## Objects

A controller action chart is a map

    D_C(a, z) -> g

from native action a and controller/reference state z to a shared physical semantic goal g. For the current joint-position core, g is the physical joint-position goal.

The inverse encoding problem is

    E_C(g, z) -> a

with an explicit representability predicate. Encoding is not allowed to clip silently and still call the transport exact.

The current chart family is absolute, delta_current, delta_target, and relative_latched. Normalization and reference semantics are part of the chart, not preprocessing metadata.

## T1 — single-boundary exact transport

For fixed source and target controller contexts, an exact E1 transport from a recorded source action exists iff:

1. the source semantic goal is identifiable from the source action plus the available source controller state; and
2. that unique goal belongs to the target chart image under the available target controller state.

When both conditions hold,

    T_s->t(a_s) = E_t(D_s(a_s, z_s), z_t)

preserves the physical joint-goal semantics.

The compiler returns one of three constructive outcomes: exact, ambiguous, or nonrepresentable. No task-success or realized-state equivalence follows from T1.

## T2 — minimal sequence state provenance

Absolute actions need no hidden reference state. Delta-current actions require measured q_current at every step because later references depend on realized dynamics and cannot be inferred from actions alone. Delta-target actions need only the initial q_target; thereafter the controller reference is recursively reconstructible from the command sequence itself, assuming no hidden reset, target mutation, or undeclared saturation. Relative-latched actions require one q_latched per chunk; every action position shares that fixed reference until the chunk boundary, so the reference neither follows measured state nor accumulates the previous target.

## T3 — bounded incremental minimum semantic horizon

Let a target incremental chart have a state-independent physical command box B containing zero, and let required semantic displacement be d. The minimum E1 command-level horizon is the smallest H such that d lies in the H-fold Minkowski sum of B. For an axis-aligned box this reduces coordinate-wise to the sign-aware ceiling implemented in reachability.py.

For delta_target, a minimum-length semantic sequence can be constructed because the target reference is recursively propagated. For delta_current, the same H is only a command-level lower bound because every later action must be re-encoded from measured q_current.

## T4 — proof-carrying exact transport

An exact compiler result can be serialized into a proof record binding source and target chart definitions, controller contexts, source and target native actions, and the shared semantic goal. A separate verifier recomputes both controller semantics without calling the compiler and rejects chart/bound drift, stale reference state, target-action tampering, proof-payload tampering, and semantic residual above tolerance.

This is proof-carrying software evidence, not a formal safety proof or cryptographic remote attestation.

## Evidence levels

E1 is command/goal semantic equivalence. E2 is controller-reference trace equivalence. E3 is realized simulator or robot trajectory equivalence. E4 is downstream task-success equivalence. Current public official-data evidence is E1; E3/E4 are not inferred from E1/E2.

## Falsifiers

The current method claim must contract if a chart marked exact fails independent semantic reconstruction; if a supposedly identifiable sequence admits multiple goal traces under declared state; if target clipping is mislabeled exact; if the proof verifier accepts identity drift; if public data contradict frozen provenance predictions; or if prior work already provides the same state-identifiability plus target-image compiler with constructive refusal witnesses.


## T5 — reference-machine sequence transport

Treat each action convention as a small reference-state machine:

- absolute: no reference state;
- delta_current: exogenous measured q_current[t];
- delta_target: endogenous q_target updated to the decoded goal after every step;
- relative_latched: q_latched fixed for the entire predicted chunk.

An exact sequence transport is obtained by decoding each source native action
through the source machine into a physical semantic goal and encoding that goal
through the target machine while updating only the target machine state allowed
by its declared semantics.

For a LeRobot-style latched relative chunk and a target-delta controller,

    u_L[t] = q_goal[t] - q_latched

and

    u_T[0] = q_goal[0] - q_target[0]
    u_T[t] = q_goal[t] - q_goal[t-1], t > 0.

Therefore copying the same relative action tensor into a target-delta
controller is generally not semantics-preserving. The compiler must instead
transduce the reference state. At the first target-image violation it returns a
nonrepresentability witness rather than clipping.

The current deterministic cross-product test covers all 4 x 4 source/target
reference-machine pairs in a representable regime. This establishes E1
software semantics only.
