# CST claim-evidence matrix v0

| ID | Claim | Current status |
| --- | --- | --- |
| C1 | Absolute, delta-current and delta-target joint-position controllers share a physical q_target normal form. | Implemented algebraically; public-stack integration in progress. |
| C2 | Native tensor copying can change physical meaning across controller charts. | Supported by deterministic witnesses. |
| C3 | Exact CST preserves q_target when the target native image contains the goal. | Implemented and unit-tested. |
| C4 | Target saturation can be detected before execution. | Implemented fail-closed. |
| C5 | Delta-target conversion requires previous target_qpos. | Implemented; missing state is rejected. |
| C6 | CST fixes ManiSkill #429 trajectory replay. | Unproven; minimal patch prepared, full replay pending. |
| C7 | CST predicts conversion viability across ManiSkill controller pairs. | Unproven. |
| C8 | The same abstraction transfers to robomimic / robosuite. | Unproven; robomimic #270 is a candidate second stack. |
| C9 | Cross-family joint / Cartesian / velocity transport can be certified. | Not claimed in v0. |
| C10 | CST has maintained external adoption. | False currently. |

C6-C10 must not be promoted in a paper or profile until external evidence exists.
