# Minimal independent admissibility replication

Third-party replication does not require understanding the full EPRC codebase.

Copy:

`research/eprc/replication_adapter_template.py`

and implement exactly one function:

```python
query(normalized_support_delta, seed) -> canonical_physical_command
```

Then run:

```bash
python research/eprc/run_minimal_admissibility_replication.py \
  my_adapter.py \
  --output my_admissibility_result.json
```

The harness automatically performs:

1. paired symmetric counterfactual probes;
2. five repeated fine-scale DEC estimates;
3. empirical q95 DEC stability;
4. coarse/fine/finer scale-locality test;
5. two-axis local-model admissibility routing.

The adapter must return a **canonical physical command**. Returning an arbitrary
raw action tensor is insufficient for a representation-invariant claim.

The resulting JSON can be attached to replication issue #76 and, after adding
execution outcomes/query accounting required by the full external gate, sealed
as an independent result record.

Negative outcomes are welcome.
