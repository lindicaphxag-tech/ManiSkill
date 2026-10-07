# 30-minute independent CRG replication

This is the shortest path for an external researcher to produce a result that is
machine-checkable and counts as **independent evidence**.

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

A valid external record prints:

```json
{
  "eligible_external_evidence": true
}
```

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

Owner-authored records, stars, forks, and owner CI count as zero external
validation.
