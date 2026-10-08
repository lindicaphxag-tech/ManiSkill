# Canonical Evidence Index — ManiSkill semantic interaction case

This file is the reviewer-facing source of truth for the current validation
state. Historical experiments remain in the branch for auditability, but they
must not override the canonical evidence below.

## Executive decision

**Do not recommend upstream merge of converter-only #1495 as a standalone fix.**

The strongest current evidence establishes:

1. the converter/controller pair contains a real compensating semantic
   interaction;
2. either singleton repair is semantically harmful under paired identical
   requests;
3. the composed repair is semantically better than current main under two
   independently generated request corpora;
4. task-level replay remains a separate gate;
5. a clean controller-contract adapter still shows a stable execution
   non-regression failure: current main 9/10 vs adapter 8/10 in 5/5
   fresh-process repeats.

Therefore semantic correctness is necessary but not sufficient for deployment.

## Canonical evidence ladder

### E1 — direct semantic mechanism

Canonical record:
`validation/pr1495/PAIRED_SEMANTIC_FIDELITY_RESULT_V2.md`

Public workflow:
`37401619096`

Two frozen request corpora, 10 episode clusters each.

Baseline-generated corpus:

- main: 0.0198999° episode-weighted mean SO(3) error
- converter-only: 2.7191730°
- controller-only: 2.7166088°
- composed: **0.0139691°**

Composed-generated corpus:

- main: 0.0212494°
- converter-only: 2.8296431°
- controller-only: 2.8268872°
- composed: **0.0143369°**

Episode-cluster bootstrap intervals keep both singleton harms above zero and
the composed-minus-main effect below zero.

Decision:

```text
converter-only -> reject
controller-only -> reject
composed        -> advance to execution-domain gate
```

This is the canonical semantic interaction certificate.

### E2 — execution measurement qualification

Canonical record:
`validation/pr1495/MEASUREMENT_QUALIFIED_EXECUTION_RESULT_V1.md`

Repeatability workflow:
`37407944746`

Measurement-qualification workflow:
`37458605789`

Current main success set in 5/5 fresh-process repeats:

```text
{0,1,3,4,5,6,7,8,9} = 9/10
```

Clean adapter v2 success set in 5/5 fresh-process repeats:

```text
{0,3,4,5,6,7,8,9} = 8/10
```

Stable discordance:

```text
episode 1: main succeeds; adapter v2 fails
episode 2: shared failure
```

Task success is externally anchored to the environment outcome and the exact
success sets repeat in every fresh process, so this channel is qualified for
execution evidence.

Decision:

```text
Authority(clean adapter v2) = REJECT
```

under the current frozen execution gate.

### E3 — stable episode-1 first divergence

Canonical record:
`validation/pr1495/STABLE_EPISODE1_DIVERGENCE_V1.md`

Workflow:
`37409297375`

Observed ordering:

```text
call 0: physical action differs
call 1: controller state differs
call 2: requested delta differs
later: clipping schedules diverge
```

At call 0:

- requested delta is identical;
- both actions are unsaturated;
- main local SO(3) error: about 3.79e-05°
- clean adapter v2 local SO(3) error: 0°
- physical action L2 difference: about 6.62e-07

Thus a locally more faithful action is followed by a different closed-loop
trajectory. This ordering is a mechanism witness, not proof that the first
microscopic difference is sufficient for terminal failure.

### E4 — evidence-channel qualification / identifiability

Canonical workflow:
`37458605789`

ManiSkill serial task success:

```text
identifiable  = PASS
repeatable    = PASS
measurement  = QUALIFIED
```

LeRobot symmetric relative-action roundtrip:

```text
repeatable    = PASS
identifiable  = FAIL
measurement  = NON-IDENTIFYING
```

The LeRobot case is source-bound and deterministic: 32/32 roundtrips are exact
while one-way forward semantics remain wrong. Therefore self-consistency is
not allowed to authorize a semantic mapping when the same latent assumption is
shared by forward and inverse transforms.

## Cross-stack corroboration

Canonical record:
`validation/crossstack/LEROBOT_MAPPING_COMPENSATION_V1.md`

Pinned LeRobot:
`huggingface/lerobot@8c920c4270460851cedd2737657584586d3dc66f`

The underlying LeRobot bug is community work; SemRepair claims only the
source-bound witness and evidence-qualification lesson.

Common structure:

```text
internal consistency != externally identified semantics
```

## Superseded / invalid evidence

Do not cite these as canonical causal conclusions:

- early single-run 9/10 vs 8/10 comparisons before repeatability qualification;
- episode-8 regression attribution based on recorder-local output trajectory
  numbering;
- the first prefix intervention, whose full-main endpoint failed to reproduce
  canonical main behavior;
- saturation/retry ownership as the primary cause of the stable regression;
- LeRobot roundtrip precision as semantic correctness evidence.

They remain in the branch as audit history precisely because the research
process falsified or invalidated them.

## Current unresolved scientific question

Why does a semantically cleaner adapter remain 8/10 while current main is
repeatably 9/10 on the frozen first-10 official-demo protocol?

The stable discriminatory source episode is episode 1.

The next valid causal experiment must:

1. reproduce the exact main and v2 endpoints;
2. alter the repair path in source, not through a non-equivalent runtime
   monkeypatch;
3. preserve source-episode identity;
4. preregister any interpolation/refinement grid;
5. refuse causal interpretation if endpoint reproduction fails.

## Upstream recommendation

Until the execution gate is resolved:

- keep #1495 open only as a diagnosis/review surface, or close/supersede it if
  maintainers prefer;
- do not merge #1495 standalone;
- do not merge #1472 as evidence that the combined semantic contract is solved;
- do not present the composed semantic improvement as task-level improvement.

A future upstream patch should be the smallest host-native change that passes
both:

```text
semantic interaction gate
AND
measurement-qualified execution non-regression gate
```

## External-evidence boundary

Everything in this validation branch is self-authored public evidence.

Current counters remain:

- maintainer review on #1495: 0
- maintainer-retained merge: 0
- external-authored reuse: 0
- prospective I2: 0
