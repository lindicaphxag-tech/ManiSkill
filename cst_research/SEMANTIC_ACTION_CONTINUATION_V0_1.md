# Semantic Action Continuations

## Problem

A predicted action chunk is often treated as a tensor, while the state that
gives those numbers meaning lives elsewhere in mutable runtime caches. LeRobot
issue #3312 is a concrete example: a relative ACT chunk must keep the state from
the chunk-generation tick, but a moving cached state can silently change the
meaning of queued actions.

## Candidate abstraction

CST represents a transported chunk as a partially evaluated continuation:

```
(query-time captures, source actions, source semantics, target semantics)
    -> target action at execution step
```

The compiler partitions reference provenance into:

### Query-time captures

Values that can and should travel with the chunk:

- source chunk anchor;
- target chunk anchor;
- initial previous-command reference.

### Step-time runtime slots

Values that do not exist yet when a chunk is predicted:

- future source physical state;
- future target physical state;
- source controller-owned target;
- target controller-owned target.

If no step-time slot remains, the continuation can be fully precomputed and no
execution-time mutable reference cache is necessary. If slots remain, they are
explicit function inputs rather than hidden global state.

## Why this adds something beyond the existing CST causal checker

The earlier causal checker classifies PRECOMPUTABLE vs REQUIRES_STEP_HOOK. The
continuation is an executable IR:

- it freezes the query-time provenance into the action object;
- exposes the exact remaining runtime signal names;
- partial-evaluates transport when possible;
- consumes previous-command references internally after one initial capture;
- eliminates irrelevant dependencies on dimensions whose relative mask is
  false.

## External mapping

- LeRobot #3312: CHUNK_ANCHOR -> ABSOLUTE. The anchor is a query-time capture,
  so the full chunk is precomputable; moving future state must not affect it.
- ManiSkill delta-current target: target CURRENT_STATE remains a step-time slot.
- robosuite desired-goal mode: CONTROLLER_TARGET remains a step-time slot.

## Novelty boundary

Closures, partial evaluation, dataflow dependencies and provenance are not new.
The research hypothesis is that compiling robot action migration into an
explicit continuation with minimal reference ownership prevents a class of
cross-controller / chunk-execution semantic failures and gives a mechanically
checkable deployment obligation.

The key evaluation burden is therefore external: real framework bugs,
cross-stack parity, and upstream use—not merely the existence of this IR.
