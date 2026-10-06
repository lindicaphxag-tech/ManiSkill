# LeRobot #4592 compatibility evidence

This gate tests the EPRC processor plugin against the exact open LeRobot
processor-plugin proposal rather than against a mocked interface.

Frozen upstream proposal:

`huggingface/lerobot#4592 @ a37961cb098cf3d0cb9fc18603e7922b09b4e311`

The CI builds and installs the real distribution
`lerobot_processor_eprc`, invokes LeRobot's
`register_third_party_plugins()`, retrieves `eprc_contract_gate` through the
real `ProcessorStepRegistry`, executes a provenance-bound certificate, checks
that the action is unchanged, and verifies repeated discovery is idempotent.

Passing this gate is compatibility evidence only. It is not LeRobot adoption and
does not count as L8 until an external maintainer/project actually uses or
adopts the primitive.
