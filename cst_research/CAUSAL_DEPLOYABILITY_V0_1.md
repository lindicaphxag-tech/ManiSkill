# Causal Deployability: Trace Conversion Is Not Runtime Migration

A controller trace can be convertible after a rollout while the same conversion is impossible to precompute when a frozen policy emits an action chunk.

Example: a policy emits H actions at query time tau. Under CHUNK_ANCHOR semantics all H actions reference x_tau, so their physical goals can be decoded immediately. If the target interface instead expects CURRENT_STATE-relative actions, target action t needs x_t. For t > tau, x_t is not available when the chunk is emitted.

Therefore:
- offline trace convertibility: YES;
- query-time whole-chunk migration: NO in general;
- exact migration with a per-execution-step adapter hook: YES, if physical state is observable.

The same issue is stronger for CONTROLLER_TARGET references: the adapter must observe target-controller-owned state at execution time.

CST reports PRECOMPUTABLE, REQUIRES_STEP_HOOK, EXECUTABLE_WITH_STEP_HOOK, or REFUSE_MISSING_RUNTIME_STATE separately from numeric representability and saturation.

This distinction is especially relevant to VLA/action-chunk deployment and is not captured by shape, unit, or normalization compatibility alone.