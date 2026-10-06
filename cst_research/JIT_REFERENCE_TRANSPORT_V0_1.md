# Just-In-Time Reference Transport

The causality checker identifies controller migrations that cannot be precomputed when an action chunk is emitted. This module provides the constructive runtime mechanism for those cases.

At each execution step:
1. read the source native action for that step;
2. obtain any reference owned by the source semantics (current state, chunk anchor, previous command, or controller target);
3. decode the physical goal;
4. obtain the target reference that is available at execution time;
5. encode the same physical goal in the target native action chart;
6. update state owned by PREVIOUS_COMMAND semantics.

Canonical cross-stack example:
- source: LeRobot-style CHUNK_ANCHOR relative action;
- target: ManiSkill-style CURRENT_STATE delta action;
- query-time tensor copying is wrong after the robot moves;
- step-time JIT re-encoding preserves the source absolute goal trace exactly.

For source native [1,2,3] with anchor 10, desired goals are [11,12,13]. Naively copying into current-state deltas reaches [11,13,16]. JIT instead emits [1,1,1] under ideal tracking and reaches [11,12,13].

The runtime mechanism does not solve numeric saturation or dynamics mismatch; those remain separate CST certificates.