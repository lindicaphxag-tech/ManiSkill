# lerobot_processor_eprc

A minimal third-party LeRobot ProcessorStep plugin for EPRC / Differential Execution Contracts.

## Status

This is an external plugin prototype, not an upstream LeRobot component.

It targets the third-party processor discovery convention proposed in LeRobot PR #4592:

- distribution name: `lerobot_processor_eprc`
- import package: `lerobot_processor_eprc`
- registered step: `eprc_contract_gate`

Until #4592 (or an equivalent processor-plugin mechanism) is merged, users can still import the package explicitly before loading or constructing a pipeline.

## Contract

The step deliberately does only five things:

1. read `eprc_evidence` and `eprc_provenance` from `complementary_data`;
2. compile PASS / TRANSPORT / REPAIR / REJECT;
3. attach `eprc_certificate`;
4. leave the action unchanged;
5. optionally raise on REJECT with `fail_closed=True`.

This package does not perform CASJ probing or mutate robot commands. Those are separate runtime responsibilities.

## Why this shape

The safest first ecosystem integration is a typed audit/admission primitive, not an opaque action-repair step. It is suitable for logging, telemetry, policy-independent rejection gates, external replication, and future full-chunk repair processors once LeRobot exposes the appropriate boundary.

## Example

```python
import lerobot_processor_eprc
from lerobot.processor import ProcessorStepRegistry

step_cls = ProcessorStepRegistry.get("eprc_contract_gate")
step = step_cls(fail_closed=True)
```

The runtime must provide the evidence bundle. Missing evidence fails explicitly rather than silently treating an action as certified.
