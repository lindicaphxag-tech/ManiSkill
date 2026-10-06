# ManiSkill Runtime Contract Extraction

This front-end removes a major weakness of the earlier prototype: controller
contracts no longer need to be manually copied into research dataclasses.

The extractor reads the runtime fields that determine executable joint-position
semantics:

- config.use_delta
- config.use_target
- config.normalize_action
- action_space_low / action_space_high for normalized controllers
- single_action_space.low / high for physical controllers

It then feeds the extracted contract into the same transport compiler.

This is still deliberately narrow: it currently targets the PD joint-position
controller family implicated by issue #429.  Expanding to EE pose, velocity,
interpolation and other controller families requires additional front-ends and
must not be inferred by name alone.
