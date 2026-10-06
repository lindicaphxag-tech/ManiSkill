# Official VQ-BeT PushT DEC smoke

This is the first public frozen-policy execution gate for DEC.

It uses:

- checkpoint: `lerobot/vqbet_pusht`
- dataset metadata: `lerobot/pusht`
- LeRobot commit: `8c920c4270460851cedd2737657584586d3dc66f`
- environment: `gym_pusht/PushT-v0`
- physical support: T-block `x / y / yaw`
- held fixed: agent position and RNG within each central-difference pair.

The smoke performs three independent RNG-seed Jacobian assays. Three replicates
are intentionally **insufficient** for the >=5-replicate DEC stability
certificate, so the workflow can establish real checkpoint execution without
silently upgrading a smoke test into a paper claim.

A zero or unstable support response is retained as a scientifically useful
negative result. The workflow fails only on infrastructure/semantic contract
violations such as non-repeatable paired RNG replay, not because DEC itself is
unfavorable.
