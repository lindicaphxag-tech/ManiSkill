# Episode 8 Replay-Context Witness V1 — Corrected Interpretation

Public workflow: `37407061050`  
Artifact: `episode8-replay-context-witness`  
Artifact ID: `11387013598`  
Artifact zip SHA-256: `f8b63e12a08359907857a63261ad9f83f80c7a098d82c9c4b33164e6b0b8c3de`

## Correction notice

An earlier draft of this note incorrectly combined the **episode-8 failure from an earlier same-base workflow** with the prefix trace from this workflow and described them as two contexts inside one run.

The raw log for `37407061050` shows that this workflow's prefix replay reported:

- **7/9** total successes;
- episodes **1 and 2** explicitly unsuccessful;
- therefore episode **8 succeeded** in this prefix replay.

The fresh isolated episode-8 replay also reported:

- **1/1 = 100% success**.

So this workflow does **not** establish a prefix-vs-isolated outcome difference for episode 8.

The corrected finding is stronger in a different direction: episode-level success sets are not stable across repeated public serial replays of the same exact candidate/protocol.

## Within-run prefix vs isolated trace result

Candidate:

`lindicaphxag-tech/ManiSkill@bd0e4feae2491a0d433107210ce8c16b8e8fb69a`

Both episode-8 traces contain **155 conversion calls**.

Comparison:

- first request divergence: **none**
- first observed controller-state divergence: **none**
- first physical-action divergence: **none**
- maximum physical-action L2 difference: **0.0**
- maximum requested-position difference: **0.0 m**
- maximum requested-rotation difference: **1.2074e-6°**
- clipping schedule identical: **true**

Clipping schedule in both contexts:

`[12, 18, 23, 29, 83, 89, 95]`

Thus episode 8 was observationally equivalent under the instrumented converter/controller trace and successful in both contexts in this workflow.

## Cross-run instability that triggered the audit

Earlier same-base workflow `37403056943` reported for the adapter:

- successful episodes: **0–7**
- episode 8 absent from the success set
- 8/10 total

But workflow `37407061050`, using the same exact candidate SHA for its prefix trace, reported:

- **7/9**
- episodes 1 and 2 unsuccessful
- episode 8 successful

Therefore the currently important unresolved variable is **run-to-run replay stability**, not demonstrated prefix-vs-isolated context dependence.

## Authorization consequence

A serial replay count cannot be treated as a stable execution-effect certificate until repeated identical runs establish the measurement's own reproducibility.

Introduce a repeatability obligation:

[
C_{repeat}=PASS
]

before task-success replay is allowed to authorize or reject a repair.

At minimum the certificate should bind:

- executable SHA;
- demo identities;
- replay arguments;
- simulator/backend version;
- process/environment setup;
- repeated success sets, not only aggregate counts.

## Next prospective test

Run the exact same candidate, same first official demonstrations, same backend, and same replay arguments multiple times in fresh processes.

Report:

- per-repeat successful episode IDs;
- per-episode empirical success frequency;
- pairwise Jaccard agreement of success sets;
- aggregate count variance;
- whether disagreement concentrates on a small boundary subset.

Only after repeatability is characterized should a candidate-vs-baseline execution comparison be promoted to canonical evidence.

## Claim boundary

Established by this workflow:

- episode 8 succeeds in both prefix and isolated contexts **in this run**;
- the observed converter/controller traces for episode 8 are identical at the recorded precision.

Established across workflows:

- the same candidate has produced different serial success sets in separate public runs.

Not established:

- reset leakage;
- hidden controller-state leakage;
- a ManiSkill bug;
- the source of run-to-run variability;
- a stable execution regression caused by the repair.
