# Prospective five-state VQ-BeT adjudication — 2026-10-06

Run:
https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37462465890

Frozen states:
`101, 211, 307, 401, 503`.

The response-jet promotion rule was fixed before execution:

- 0 first-order-failure rescues -> DROP_JET_FROM_FLAGSHIP
- 1-2 rescues -> KEEP_AS_SECONDARY_MECHANISM
- >=3 rescues -> PROMOTE_TO_BROADER_PROSPECTIVE_TEST

Observed:

- first-order locality contracting states: **3 / 5**;
- jet model-order upgrades: **0 / 5**;
- jet rescues: **0 / 5**;
- states where first-order and jet were both rejected: **2 / 5**;
- all-state DEC stability: **false**;
- adjudication: **DROP_JET_FROM_FLAGSHIP**.

Per-state frozen measurements:

| seed | q95 DEC radius | DEC stable | locality ratio | jet error ratio | jet upgrade |
|---:|---:|:---:|---:|---:|:---:|
| 101 | 1.432452 | no | 0.350857 | 0.920676 | no |
| 211 | 0.000000 | yes | 0.655060 | 1.141606 | no |
| 307 | 0.180093 | no | 0.664868 | 0.760286 | no |
| 401 | 0.000000 | yes | 0.909078 | 0.938033 | no |
| 503 | 0.469409 | no | 2.771968 | 1.031391 | no |

The important surviving observation is not the failed jet. It is the
independence of repeated-probe stability and scale locality: the frozen states
populate all four combinations of those two gates.

This result is self-authored real-policy evidence, not external replication.
