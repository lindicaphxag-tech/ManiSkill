# VQ-BeT executable-runtime provenance split

The official `lerobot/vqbet_pusht` checkpoint cannot be treated as a checkpoint
alone.

Current LeRobot main rejects its serialized `mlp_hidden_dim` field, while the
checkpoint-era VQ-BeT runtime declared that field as part of the model
configuration. The public assay therefore separates:

1. **historical-native**
   - LeRobot: `2cb0bf5d4154c8fefe03d1dca394fc5e1d778a97`
   - model: `lerobot/vqbet_pusht@bff7190`
   - no config-field deletion or migration;

2. **current-migrated**
   - current LeRobot runtime;
   - only after the upstream normalization migration/schema-drift path is
     explicit and reproducible.

DEC values from these two execution specifications must never be pooled without
recording the runtime provenance.

This is not evidence that either runtime is "correct" by itself. It is a
falsifiable separation intended to prevent executable-runtime drift from being
misreported as policy physical behavior.
