# Source-pinned independent task-extension test, PullCube + StackCube
Source: successful real PhysX Actions 37815152548 on 9ffa86c6d3a86d2cee44b6e13c560033a8b373cf.
Frozen before code: protocol commit 582e39206cedf3565217514b1fdc1872c1cffae7.
Two new released frozen PPOs. Every original controller/task row is copied unchanged and SHA-256 verified against this workflow.
PullCube: source 31/32; naive 14/32; exact 17/32; memory bounded 31/32; state-blind bounded 14/32; paired memory-only 17 vs blind-only 0.
StackCube: source 28/32; naive 0/32; exact 11/32; memory bounded 30/32; state-blind bounded 0/32; paired memory-only 30 vs blind-only 0.
Original task competence and declared memory-gain criteria PASSED on both new task families.
NON-EXACT bounded projections: PullCube 15, StackCube 33. This is not an exact action equivalence or safety proof.
Owner-run simulation, NOT independent external replication, hardware transfer or general VLA performance.
