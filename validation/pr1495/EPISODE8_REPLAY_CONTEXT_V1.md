# Episode 8 Replay-Context Witness V1

Public workflow: `37407061050`  
Artifact: `episode8-replay-context-witness`  
Artifact ID: `11387013598`  
Artifact zip SHA-256: `f8b63e12a08359907857a63261ad9f83f80c7a098d82c9c4b33164e6b0b8c3de`

## Trigger

The clean controller-contract adapter previously appeared to fail episode 8 when replayed after episodes 0–7, while an isolated repair-path endpoint replay unexpectedly succeeded.

This assay compares the same candidate and the same recorded episode under:

1. serial-prefix context: episodes 0–8 replayed in one process;
2. fresh isolated context: only episode 8 replayed from an extracted one-episode trajectory.

Candidate:

`lindicaphxag-tech/ManiSkill@bd0e4feae2491a0d433107210ce8c16b8e8fb69a`

## Outcome label differs

Serial-prefix run:

- first 9 episodes replayed;
- aggregate: **7/9**;
- episodes 1 and 2 were reported as unsuccessful;
- episode 8 was not among the saved-success set in the earlier same-base gate.

Fresh isolated episode 8:

- **1/1 = 100% success**.

Thus the same recorded episode and same executable candidate can receive different terminal success outcomes depending on replay context.

## Observable converter/controller traces do not differ

Both episode-8 traces contain **155 conversion calls**.

The comparison reports:

- first request divergence: **none**
- first observed controller-state divergence: **none**
- first physical-action divergence: **none**
- maximum physical-action L2 difference: **0.0**
- maximum requested-position difference: **0.0 m**
- maximum requested-rotation difference: **1.2074e-6°** (numerical quaternion-distance floor)
- clipping schedule identical: **true**

Both clipping schedules:

`[12, 18, 23, 29, 83, 89, 95]`

At call 0:

- requested position delta difference: 0
- requested rotation delta difference: 0
- physical action difference: 0
- EE position difference: 0
- EE rotation difference: ~1.2074e-6°
- clipping decision: identical

## Interpretation

Within the currently instrumented action/converter/controller state, the two episode executions are observationally equivalent.

Yet the terminal success label changes.

Therefore the previous serial replay count cannot be treated as a clean independent-episode causal estimate of repair quality.

At least one of the following must hold:

1. task-relevant simulator/environment state is not represented in the current trace;
2. reset/state restoration leaves hidden execution context;
3. task evaluation depends on state not captured by the converter/controller trace;
4. low-level simulator numerical state or solver history affects the terminal predicate;
5. another replay-wrapper/context variable differs between fresh and prefix execution.

This assay does **not** yet identify which explanation is causal.

## Authorization consequence

A task-success effect certificate should not be issued merely from a serial replay count when:

[
SameObservedTrace
land
DifferentOutcome
]

has been demonstrated for the same episode.

Introduce a context-stability obligation before using execution evidence for repair authority:

[
C_{context}=PASS
]

only if the outcome/effect is stable across the replay contexts the certificate claims to abstract over, or if the relevant context is explicitly bound into the certificate identity.

## Reclassification of earlier evidence

The earlier public serial matrices remain valid observations of those workflow executions.

They should now be interpreted as:

> **serial-context replay evidence**

rather than:

> independent per-episode execution non-regression evidence.

In particular, `9/10 main vs 8/10 composed/adapter` must not be used alone to claim an intrinsic episode-level repair regression until context dependence is controlled.

## Next causal target

Instrument the task's terminal `success` predicate and the state variables it reads, then compare those variables between prefix and isolated episode 8.

If the predicate inputs differ while converter/controller traces are equal, the missing state channel is localized.

If predicate inputs are equal but labels differ, the evaluator itself or numerical timing/state update path requires audit.

## Claim boundary

Established:

- same candidate;
- same recorded episode;
- same 155 observed converter/controller calls;
- identical physical-action sequence at recorded precision;
- different replay-context success outcome.

Not established:

- the hidden state variable responsible;
- a ManiSkill reset bug;
- a simulator bug;
- general context dependence across tasks.
