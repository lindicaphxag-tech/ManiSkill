# CRG replication: 30-minute schema walkthrough

The **core example and JSON schema** can be checked quickly. Running and
validating a real frozen policy, especially on a new simulator/controller,
requires additional experimental work and is **not** guaranteed to take 30 minutes.
A schema-valid record is a submission for external audit, not proof of
independent reproduction.

## 1. Run the core certificate

```bash
python -m pip install numpy pytest
python -m pytest -q tests/test_crg_core.py tests/test_crg_active_probe.py tests/test_crg_local_model.py
python research/crg_core/demo.py
```

## 2. Connect one real frozen policy

Use any frozen policy/controller pair. You do **not** need PushT or LeRobot.

For each held-out repair request, record:

- immutable source commit and checkpoint;
- policy family, task, controller representation;
- frozen physical intervention protocol id;
- CRG decision: `CERTIFIED_REPAIR`, `CERTIFIED_IMPOSSIBLE`, or `INCONCLUSIVE`;
- black-box policy-query count;
- actual execution outcome for at least one request;
- false accepts and false rejects.

Synthetic matrices alone do not satisfy the external-evidence gate.

## 3. Seal and validate the result

Copy the template, fill in your real result, then seal and validate it:

```bash
cp research/crg_core/replication_example.json result.json
python -m research.crg_core.seal_replication result.json
python -m research.crg_core.replication_record result.json
```

The seal command rewrites `evidence_digest` with the canonical SHA-256 and
immediately validates the resulting record.

The offline validator reports:

```json
{
  "schema_valid": true,
  "claimed_independent": true,
  "independence_verified": false,
  "eligible_external_evidence": false
}
```

The first two fields are **self-reported consistency** only. The last two
remain false until a separate reviewer has corroborated the real source,
checkpoint, execution artifacts and producer identity. The unkeyed SHA-256
digest detects accidental edits after sealing, not authorship or authenticity.

A negative result is valid evidence. High false-accept rates, all-inconclusive
results, or higher query cost than a baseline are not filtered out.

## 4. Submit

Open a pull request adding the sealed JSON under:

```text
research/crg_core/replications/<producer>-<policy>-<date>.json
```

The scientific question is not "can you reproduce our favorite number?" It is:

> Does explicit model-validity / evidence-source routing predict when a frozen
> policy repair should be authorized, rejected, or left inconclusive better than
> raw local-Jacobian similarity or simply collecting more probes?

## 5. Independent adjudication (required before any external-recognition claim)

The reviewer independently checks the submitter's account/affiliation against
the repository owner; the actual frozen checkpoint and runtime revision; raw
per-request intervention/output/execution traces (not just summary counts);
and that the recorded failure labels follow a documented held-out protocol.
The reviewer should reproduce or independently verify at least a subset of
the claims. An ordinary pull request, an apparent non-owner username, and a
freshly recomputed hash **cannot** establish independent reproduction.

The example JSON is deliberately synthetic and **must never be counted as
research evidence**, even if the schema checker accepts its structure.
Negative results are retained, but they are subject to the same audit.

Owner-authored records, stars, forks, and owner CI count as zero external
validation.
