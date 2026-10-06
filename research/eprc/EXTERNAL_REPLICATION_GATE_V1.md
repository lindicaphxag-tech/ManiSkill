# External replication gate v1

This file defines what counts as an **external DEC / CRG / AMRC result**.

The gate is intentionally about provenance and result-bearing independence, not
about producing a favorable number.

A third-party result may show that CRG works, fails, stays inconclusive, has
false accepts, or uses more queries than a fixed baseline. It still counts as
external evidence if the result is complete, immutable, independently produced,
and tied to a real frozen policy.

## Required properties

A record must bind:

- an external producer identity;
- immutable source commit and checkpoint;
- real frozen policy family and task;
- controller representation;
- frozen intervention protocol id;
- total held-out repair requests;
- counts for CERTIFIED_REPAIR / CERTIFIED_IMPOSSIBLE / INCONCLUSIVE;
- actual black-box policy-query count;
- false-accept and false-reject counts;
- at least one observed execution outcome;
- canonical SHA-256 evidence digest.

Synthetic matrices, owner-authored reruns, stars, forks, and owner CI do not
satisfy this gate.

## Machine validation

```bash
python research/eprc/validate_external_replication.py path/to/record.json
```

A successful run emits:

```json
{
  "eligible_external_evidence": true
}
```

along with query and error accounting.

## Why favorable performance is not required

The scientific trigger we care about is **external contact with the claim**.
A rigorous failure is more valuable than a self-authored success.

Performance claims are reported separately from external-evidence eligibility.
In particular, this validator does not hide false accepts or false rejects and
does not define arbitrary task-independent success thresholds.

## Stronger promotion gate

The flagship method should not be called externally validated until at least one
eligible record exists. A stronger L8-style signal is:

1. one eligible independent result-bearing replication; and
2. either maintained robotics-runtime adoption/merge or a second independent
   policy-family result under the frozen protocol.

L9 remains reserved for independent implementation/comparison plus sustained
citation, reuse, or ecosystem adoption.
