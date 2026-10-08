# Pre-registration: physical executable-witness parity over 32 unseen PushCube seeds

Registered after **4 developer seeds** validated mechanics, but
BEFORE running this new disjoint 32-seed cohort.

New fixed seeds: **31001 through 31032** inclusive, in order.
Task PushCube-v1/Panda/PhysX CPU, separate published frozen PPO
`ppo/push_cube_final_ckpt.pt` checksum
`a4a02198b309e73cb877959079023d967d5f63ec78380de9703a10c9efafc0cf`.
No PPO weight update, no per-seed dynamic controller gain changes,
50-step horizon.

Four task-controller arms as in earlier PushCube experiment:
source achieved-delta, target memory exact/refuse, target memory
bounded-projected, raw-native direct copy. Policy inference uses each
own observation with verified omission of the 7D extra controller
state field. Initial policy observations must match.

**New intervention:** independent numerical `FeasibilityWitness`
computes the exact/nonexact/refusal decision and predicted translation
+ SO(3) orientation residual between desired and realizable *target
goal*. After each actual environment `step`, read the destination
controller's stored `_target_pose` and assert absolute difference
between its measured residual and witness predicted residual
is <=5e-5 for both meters and radians. If any check disagrees,
**fail CI**, not merely print a warning or count task success.

For every episode report successes, strict refusals, approximation
count and required native amplitude, number of post-step witness
checks and largest residual-check error. Do not condition on source
success or omit failed episodes. The 4 observed development seeds
(42,270,429,2026) and 32 prior PushCube pilot seeds (30001–30032)
are excluded from this cohort.

The witness validates only a **local one-step controller-goal calculation**,
not actual achieved end-effector tracking, global task equivalence,
physical safety, formal proof, or neural policy novelty. Native
bounded projection is ordinary prior art; novelty requires the
complete runtime state/observation/action contract and compelling
cross-implementation adoption/replication.
