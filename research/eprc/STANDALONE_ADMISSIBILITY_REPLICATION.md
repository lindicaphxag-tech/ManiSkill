# One-file independent admissibility replication

For the smallest possible independent check, copy only:

`research/eprc/standalone_admissibility.py`

into another repository.

It depends only on NumPy and does not import EPRC.

Provide:

- one coarse physical-command Jacobian;
- at least five repeated fine-scale Jacobians;
- repeated finer-scale Jacobians.

Then call:

```python
from standalone_admissibility import evaluate

result = evaluate(
    coarse_map=G_coarse,
    fine_map_replicates=G_fine_repeats,
    finer_map_replicates=G_finer_repeats,
)
print(result)
```

The result separates two independently measurable gates:

1. repeated-probe DEC stability;
2. contraction of the physical local map as intervention scale shrinks.

It returns one of:

- `ADMISSIBLE_FIRST_ORDER`
- `INFORMATION_LIMITED`
- `LOCALITY_LIMITED`
- `REJECT_LOCAL_MODEL`

A regression test compares this standalone implementation against the owner
implementation field by field. The purpose is to make independent negative
replication possible without installing the research package.

This file does **not** itself establish external validation. It only lowers the
cost of obtaining it.
