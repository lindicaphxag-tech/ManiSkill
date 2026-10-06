# Temporal Contract: Controller-Rate Migration

Changing controller frequency changes executable action semantics even when the
action tensor shape and coordinate convention are unchanged.

This module studies a deliberately narrow contract:

> preserve each source-rate absolute physical goal under zero-order hold while
> executing through a faster target controller.

For an integer target/source rate ratio r, every source physical goal is held
for r target ticks and then re-encoded under the target reference semantics.

Examples:

- ABSOLUTE -> ABSOLUTE: repeat the held goal.
- PREVIOUS_COMMAND delta -> faster PREVIOUS_COMMAND delta: emit the delta once,
  then zeros for the remaining hold ticks. Repeating the numeric delta would
  accumulate it r times.
- CHUNK_ANCHOR -> CURRENT_STATE: future target-rate actions depend on future
  measured states, so the migration cannot be precomputed with the chunk and
  requires a per-step hook.
- CONTROLLER_TARGET targets similarly require controller-owned target state at
  execution time.

This is a goal-trace certificate, not a claim of continuous-time trajectory or
dynamics equivalence.

## Novelty boundary

High-frequency action chunks, interpolation, asynchronous chunk execution and
latency correction are established research topics (including ICML 2026 RTR,
RTC, and A2C2).  The candidate CST contribution is narrower: compile
controller-rate changes jointly with executable reference ownership and return
a precompute / step-hook / refusal obligation for frozen-policy controller
migration.

v0.1 intentionally supports only integer upsampling ratios and ZOH physical
goals.  Noninteger resampling, interpolation and SO(3) temporal refinement must
be treated separately rather than silently approximated.
