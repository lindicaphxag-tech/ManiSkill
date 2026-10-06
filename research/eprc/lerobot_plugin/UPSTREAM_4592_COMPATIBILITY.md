# LeRobot #4592 source-anchored plugin compatibility

Target upstream discovery mechanism:

- PR: `huggingface/lerobot#4592`
- inspected head: `a37961cb098cf3d0cb9fc18603e7922b09b4e311`
- discovery prefix: `lerobot_processor_`

The inspected implementation enumerates installed distributions, reads each distribution metadata `Name`, checks `startswith(prefixes)`, and then imports that exact distribution name.

This creates a stricter compatibility rule than a generic Python packaging statement: for the current PR head, the distribution name must itself be a valid import package name. A hyphenated project name can be installed successfully yet be silently skipped by discovery.

EPRC therefore freezes:

- distribution: `lerobot_processor_eprc`
- import package: `lerobot_processor_eprc`
- registry key: `eprc_contract_gate`.

The public CI builds a real wheel and inspects its METADATA and package contents so packaging drift cannot silently break auto-discovery.

This still counts as zero LeRobot adoption until #4592 (or equivalent) is merged and an external user/runtime actually installs or composes the plugin.