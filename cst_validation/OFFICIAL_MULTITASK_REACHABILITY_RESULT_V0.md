# Official ManiSkill multi-task CST reachability — frozen result v0

Status: **public official-data evidence; E1 semantics only**.

Frozen protocol: `OFFICIAL_MULTITASK_REACHABILITY_PROTOCOL_V0.md`.
Successful GitHub Actions run: `37385656919`.
Frozen validation commit: `5af7cc9e14358ff3dafdaa1ef31aeec1e5139e40`.
Artifact: `cst-official-multitask-reachability-v0`, id `11377651652`,
digest `sha256:00867ff61fe9ef845f861234d0605dd97294f92332a26a80271e54a8d9eafe04`.

## Aggregate result

| Metric | delta-current | delta-target |
|---|---:|---:|
| Official tasks | 4 | 4 |
| Trajectories | 4,000 | 4,000 |
| Actions | 519,006 | 519,006 |
| One-step exact actions | 517,807 | 519,006 |
| One-step exact fraction | 99.768981% | **100.000000%** |
| Actions requiring H_min > 1 | 1,199 | **0** |
| Maximum H_min | 2 | **1** |
| Tasks with 100% action-level one-step exactness | 1 / 4 | **4 / 4** |

## Per-task result

| Task | Actions | delta-current exact | current H>1 | current trajectory-perfect | delta-target exact |
|---|---:|---:|---:|---:|---:|
| PickCube-v1 | 77,976 | 99.697343% | 236 | 928/1000 | **100%** |
| StackCube-v1 | 107,420 | 99.104450% | 962 | 824/1000 | **100%** |
| PegInsertionSide-v1 | 149,055 | **100%** | 0 | 1000/1000 | **100%** |
| PlugCharger-v1 | 184,555 | 99.999458% | 1 | 999/1000 | **100%** |

All 1,199 delta-current out-of-image actions have H_min=2 under the frozen
per-joint +/-0.1 rad semantic box. This H_min is only an ideal E1 reachability
lower bound for delta-current because later commands require measured q_current
feedback.

## Interpretation

The result does **not** say that delta-target is universally a better robot
controller. It establishes a narrower interface fact for these official
motion-planning trajectories:

> Changing only the incremental controller's reference state changes the
> one-step semantic image of the action interface.

`pd_joint_delta_pos` is defined relative to measured q_current. Tracking lag
can therefore make an otherwise small change in successive absolute goals fall
outside the next one-step +/-0.1 rad box. `pd_joint_target_delta_pos` is
defined relative to the previous controller target; across all four frozen
datasets, every adjacent recorded absolute goal remains inside that box.

This is evidence for CST's exactness decision problem, not the main novelty.
The method contribution is the proof-producing boundary compiler:
identifiability -> target image membership -> exact action or explicit
ambiguity/non-representability witness -> minimum semantic horizon when useful.

## Transparency

The first multi-task run (`37385539961`) failed because the reader assumed the
HDF5 articulation key was literally `panda`; StackCube/Peg/Plug use
`panda_wristcam`. The frozen protocol constrained the articulation by its 31D
Panda state schema, not by group name. The reader was changed only to discover
the unique 31D articulation dataset. No task, bound, tolerance, metric, or
claim threshold changed before the successful rerun.

## Claim boundary

- E1 semantic-command reachability only.
- No E2 controller-reference-trace equivalence.
- No E3 realized-state trajectory equivalence.
- No E4 task-success claim.
- No safety claim.
- Author-controlled public validation is not external adoption.