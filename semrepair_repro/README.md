# SemRepair CPU reproduction capsule v1

This is a deliberately small, self-authored public reproduction surface.

It does **not** claim external adoption or independent reproduction.

## One command

```bash
bash semrepair_repro/reproduce_lerobot_cpu.sh
python semrepair_repro/measurement_gate.py lerobot_mapping_compensation.json
```

No GPU, simulator, model checkpoint, or LeRobot installation is required.

The command fetches one pinned upstream LeRobot source file:

`huggingface/lerobot@8c920c4270460851cedd2737657584586d3dc66f`

and tests one narrow question:

> Can a forward/inverse transformation be perfectly self-consistent while its
> one-way semantic mapping is wrong because both directions share the same
> latent state/action alignment error?

Frozen public witness:

- one-way semantic L∞ error: **59.7**;
- round-trip L∞ error: **0.0**;
- 32 deterministic sweep cases;
- 32/32 exact round-trips;
- 32/32 wrong forward semantics.

The second command converts that evidence into the SemRepair measurement rule:

```text
repeatable = PASS
identifiable = FAIL
=> measurement cannot authorize repair
```

## Why this capsule exists

The main SemRepair validation branch contains real ManiSkill simulator evidence
and a much larger experimental harness. That is useful for the paper, but it is
too large for a first independent check.

This capsule is intentionally five small files and uses only the Python standard
library plus curl.

## Independent reproduction

Agreement is not required.

If you reproduce, challenge, or falsify this result, please comment on the
public SemRepair evidence PR and include:

- exact capsule commit;
- OS / Python version;
- raw JSON;
- any source/network deviation;
- agreement / disagreement / null result.

Current independent third-party reproduction count: **0**.

## Attribution boundary

The underlying relative-action mapping bug was reported by the LeRobot
community in `huggingface/lerobot#3863`, with community fix PR `#4111`.

This capsule does not claim discovery or ownership of that bug. It isolates the
measurement-identifiability consequence for semantic repair authorization.
