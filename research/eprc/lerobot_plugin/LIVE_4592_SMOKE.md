# Live compatibility gate against LeRobot #4592

This branch contains a dedicated GitHub Actions smoke test against the exact current head of Hugging Face LeRobot PR #4592:

`a37961cb098cf3d0cb9fc18603e7922b09b4e311`

The gate performs a real package-level integration:

1. installs that exact LeRobot commit;
2. builds and installs the EPRC processor distribution;
3. invokes LeRobot's real `register_third_party_plugins()` discovery;
4. verifies `eprc_contract_gate` appears in `ProcessorStepRegistry` without explicit plugin import;
5. executes a fail-closed evidence case and requires the expected REJECT certificate.

This is stronger than source inspection but still counts as **self-authored compatibility evidence, not LeRobot adoption**.

If #4592 changes head, this pin should be deliberately updated only after reviewing the discovery contract. If #4592 merges, the pin can move to the merge commit and the README can drop the pre-merge caveat.