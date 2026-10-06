# CST prospective external audit V1

Frozen before inspecting the holdout repositories below.

## Purpose

Test whether Controller-Semantic Transport (CST) can prospectively identify
action-semantic defects or explicit refusal boundaries in maintained robot
software that were not used to design the current CST method.

This is not a bug-count benchmark. Negative repositories and ambiguous cases
are retained.

## Frozen defect predicates

A case is promoted to **I2 defect candidate** only when current repository
source supplies all evidence needed for one of the following predicates.

### P1 — hidden-reference mismatch

A stateful action is defined relative to controller-owned state (for example a
previous target), but a conversion / replay / adapter interprets it relative to
a different state (for example measured current qpos) without an explicit
equivalence proof.

### P2 — chart-local effect leakage

A preprocessing effect such as clipping, normalization, scale, offset, limit
lookup, or coordinate mask is keyed in one semantic chart but applied to values
in another chart merely by index, shape, or unrelated names.

### P3 — representation contract mismatch

Producer and consumer disagree on the representation of the same action
coordinate (for example Euler vs axis-angle, quaternion ordering, relative vs
absolute, frame, or unit), and no explicit conversion bridges the difference.

### P4 — state-lifetime mismatch

A stateful action adapter / processor carries semantic state across an episode,
reset, robot switch, or control-scope boundary where that state should be
reinitialized, or resets it earlier than its semantic lifetime.

## Evidence levels

- **I0 / no finding:** inspected relevant current source; no frozen predicate
  established.
- **I1 / ambiguity:** suspicious semantics, but source evidence is insufficient
  to establish a predicate without guessing runtime intent.
- **I2 / defect candidate:** source establishes one frozen predicate and a
  minimal deterministic witness can be constructed.
- **I3 / externally confirmed:** maintainer, issue, merged patch, or independent
  downstream evidence confirms the I2 interpretation. I3 is never inferred
  from our own fork.

## Holdout repositories

These repositories are frozen as the V1 source holdout and must be inspected at
their then-current default-branch commit. Previously used CST design cases
ManiSkill #429/#1138 and IsaacLab #1548 are excluded.

1. `robosuite/robosuite`
2. `huggingface/lerobot`
3. `Physical-Intelligence/openpi`
4. `real-stanford/diffusion_policy`
5. `octo-models/octo`
6. `ARISE-Initiative/robocasa`
7. `facebookresearch/habitat-lab`
8. `google-deepmind/mujoco_mpc`

## Search surface

Only action-semantic code paths are in scope:
- action preprocessing / postprocessing;
- absolute/relative/delta conversions;
- controller target state;
- normalization / clipping / limits;
- action frame / rotation representation;
- action-processor reset / episode lifetime;
- trajectory replay conversion.

A repository may be classified I0 after focused searches find no relevant
conversion/stateful-adapter surface.

## Anti-leakage rules

- Do not change P1-P4 after viewing holdout source.
- Do not add a repository because a known issue looks promising.
- A known historical issue discovered *after* an I2 source finding may upgrade
  it to I3, but may not define the predicate retroactively.
- Repository-native tests or docs can support a finding; our own checker alone
  cannot make it I3.
- All I0/I1/I2 outcomes remain in the ledger.
