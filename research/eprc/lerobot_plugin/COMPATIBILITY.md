# LeRobot plugin compatibility contract

Target upstream mechanism:

- LeRobot PR: `huggingface/lerobot#4592`
- inspected head: `a37961cb098cf3d0cb9fc18603e7922b09b4e311`
- discovery prefix: `lerobot_processor_`
- package/distribution: `lerobot_processor_eprc`
- registered ProcessorStep name: `eprc_contract_gate`

## Compatibility boundary

The plugin intentionally uses only the public processor surface already present
in LeRobot:

- `ProcessorStep`
- `ProcessorStepRegistry.register`
- `EnvTransition`
- `TransitionKey.COMPLEMENTARY_DATA`

The plugin does not patch policy classes, inference engines, ActionQueue, or
robot drivers.

## Current integration mode

Before #4592 (or an equivalent discovery mechanism) lands:

```python
import lerobot_processor_eprc
```

registers the processor explicitly.

With the #4592 discovery contract, a correctly named installed distribution can
be imported automatically by LeRobot's existing third-party discovery pass.

## Deliberate non-goals

This first plugin does not:

- estimate CASJ online;
- modify an action;
- assume it sees a full chunk;
- claim policy safety;
- claim external LeRobot adoption.

It is a small audit/admission surface that makes provenance-bound EPRC evidence
usable by the ecosystem without requiring core changes.

## Adoption event that counts

The following would count as external L8 evidence:

1. a third party installs the plugin and publishes a result-bearing certificate;
2. a maintained runtime composes the step into a real policy pipeline;
3. LeRobot or another maintained robotics project adopts an equivalent contract
   gate or provenance primitive.

Self-authored CI, forks, stars, and imports do not count.
