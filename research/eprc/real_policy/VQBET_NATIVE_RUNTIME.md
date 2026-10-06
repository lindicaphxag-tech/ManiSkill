# VQ-BeT checkpoint-native runtime gate

The current `lerobot/vqbet_pusht` checkpoint contains the historical
`mlp_hidden_dim` configuration field. Modern LeRobot VQ-BeT schemas no longer
contain that field, and the previously pinned 2026 runtime therefore fails
before policy execution.

This gate does not delete or rewrite checkpoint metadata. It uses an official
LeRobot revision from the checkpoint's own era:

`a1809ad3de96c6989acd33c0650849bf4f631929` (2025-02-25)

The public model card reports the checkpoint was last updated on 2025-03-06.

## Pass condition

The official checkpoint must load natively, expose the historical architecture
field, contain finite weights, and report its action/state shapes without a
schema migration shim.

Only after this gate passes is a PushT physical-support intervention meaningful.

## Why this matters for EPRC

A frozen checkpoint is not an executable policy by itself. Runtime code and
configuration schema are part of deployment provenance. This is a negative
result for the old 2026 pin, not a DEC result, and it is retained explicitly.
