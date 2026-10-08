# Trajectory-Effect Certificate — Exhaustive Discordance Protocol

Status: **protocol frozen before tracing source episodes 63 and 96**

## Selection rule

The current same-base 100-demo audit is frozen at:

- current main: 92/100;
- clean contract adapter v2: 91/100;
- adapter v2 + controller-sign fix: 91/100;
- main-only successes: {1, 63};
- candidate-only successes: {96};
- both-success: 90;
- both-fail: 7.

The mechanism audit includes **every discordant source episode** from this frozen paired result:

- episode 1: main succeeds, candidate fails;
- episode 63: main succeeds, candidate fails;
- episode 96: main fails, candidate succeeds.

No discordant episode is omitted.

## Per-episode certificate fields

For each discordant episode, the trace must bind:

- source episode ID;
- exact implementation SHA;
- endpoint outcome for main/candidate/candidate+controller-fix;
- first tiny post-step physical divergence;
- first material physical divergence;
- first retry/protocol divergence;
- maximum EE position divergence;
- maximum EE rotation divergence;
- maximum post-rotation residual divergence;
- rotation clipping count;
- retried source-step count;
- candidate-vs-controller-fixed divergence.

Material divergence is frozen as the first source step where at least one holds:

- EE position difference > 1 mm;
- EE rotation difference > 1 degree;
- task-success predicate differs.

## Derived trajectory-effect quantities

For each main-vs-candidate trace define:

- tau_material: first material physical divergence step;
- tau_protocol: first retry-count divergence step, if any;
- protocol_lag = tau_protocol - tau_material, when both exist;
- effect_sign = harmful if main succeeds and candidate fails;
- effect_sign = beneficial if main fails and candidate succeeds.

Candidate-vs-controller-fixed is a migration-invariance control. If it materially diverges, controller-sign migration cannot be excluded as the mechanism.

## Questions

1. Do all discordant episodes show material trajectory divergence before endpoint outcome changes?
2. Is controller-sign migration irrelevant across all three cases?
3. Does protocol/retry divergence systematically occur after physical divergence, or only in some cases?
4. Are harmful and beneficial repair effects two signs of the same trajectory-basin transition mechanism?

## Claim boundary

This protocol can support a trajectory-effect / basin-transition interpretation only for the frozen discordant set. It does not establish a general hybrid-systems law.
