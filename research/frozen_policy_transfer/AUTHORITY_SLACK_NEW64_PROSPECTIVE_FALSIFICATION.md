# Authority-slack-only proactive readback: an honest prospective falsification

**2026-10-09 — complete original 64-state, eight-world true ManiSkill/PhysX study.** This is *contributor-operated* research with public source-hash reconstruction. Not accepted peer-reviewed work, external original-method adoption, actual network packet loss or robot safety.

## Evidence
- [Threshold .75, two-step unknown-ACK, all 64 untouched seeds preregistered **before** outcomes](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/authority-slack-proactive-new64-20261009/research/AUTHORITY_SLACK_PROACTIVE_NEW64_FROZEN_V1.json).
- [Real native PhysX 64 original reset states, 8 actually stepped paired controller variants each (512 runs) — SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37909638381).
- [SHA-verified full original eight-artifact reconstruction and paired outcomes — SUCCESS](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910234571). [Original all-64 result and source-hash artifact](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37910234571/artifacts/11606585133).
- [Original native runner](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/authority-slack-proactive-new64-20261009/research/frozen_ppo_authority_slack_proactive.py); [source-only original 64-state auditor](https://github.com/lindicaphxag-tech/ManiSkill/blob/research/authority-slack-proactive-new64-20261009/research/audit_authority_slack_new64.py).
- Published third-party PPO checkpoint files and originally accepted controller-command-mapping recurrence were frozen. The only novel candidate was the task-independent query timing rule: at step 4, when the common bounded command remains possible but its certified worst-case setpoint error / permitted error exceeds **0.75**, request a trusted controller target now; otherwise continue certifiably and query on future denial. The same two injected arm-target holds occur at steps 2/3 in all faulty methods.

## Complete original metric table
| Original full-native-controller policy | Official task successes /64 | Decision-time privileged target reads |
|---|---:|---:|
| Fixed early authoritative read at step 4 | **58** | 64 |
| **New task-blind authority-slack proactive query** | **56** | **61** |
| Strong task-ID route (selective on Pull, fixed on Stack) | 55 | **56** |
| Reactive read only after action authority refuses | 41 | 41 |

- **Actual paired task success proactive vs strong task-ID route:** 54 both succeed, 2 proactive-only successes, 1 task-ID-route-only, 7 both fail. Exploratory conditional exact two-sided sign-test p = **1.0**. No method task superiority.
- PullCube: proactive **29/32, 29 reads**; full fixed **32/32**; reactive **29/32, 24 reads**. The learned-quality claim that the 75% gate improves Pull transfer **fails**.
- StackCube: proactive **27/32, 32 reads**, fixed **26/32, 32 reads**, reactive **12/32, 17 reads**. This is one extra success without query reduction; not a general method win.
- **2,144 conditional post-dispatch native commanded-target tolerance checks** passed the source setpoint residual envelope; **256 physically held/overridden command attempts were excluded** rather than incorrectly certified.
- Real original tester had 8 matched controller variants per state × 64 reset states = 512 physically stepped ManiSkill controller instances, but only **2 independent pretrained PPO checkpoints in one Panda/controller family**.

## What the failures actually reveal

All THREE PullCube cases where fixed readback succeeded but reactive and proactive failed had step-4 normalized common-action authority ratios **below the precommitted 0.75 trigger**:
- Pull original seed **620003**: ratio 0.72056517.
- Pull original seed **620028**: ratio 0.72916934.
- Pull original seed **620031**: ratio 0.73784003.

The other 29 PullCube states had ratios above the threshold, and the newly proactive method spent 29 reads there; all 29 succeeded. This reveals a **descriptive counterexample to treating near-term setpoint authorization slack as a monotone surrogate for downstream task need for observation**. In the existing controller, a smaller immediate error bound can allow continued blind execution despite longer-horizon downstream opportunity cost. These 64 seeds are now INSPECTED and cannot be recycled as confirmatory tests after updating the trigger direction.

On StackCube, all 32 trial prequery ratios were above 0.75; the proactive policy read all 32, making it no more query-efficient than fixed-t4. An isolated StackCube improvement to 27/32 from 26/32 may reflect branch/controller behavior but does not justify inference of general advantage.

## Prior art and contribution boundary

- Krishna, Hu, Jayaraman, *The Value of Sensory Information to a Robot*, **ICLR 2025**: study of varying task-critical information values across robotics states, https://proceedings.iclr.cc/paper_files/paper/2025/hash/e1126028d9f1f69c13571ec462084d31-Abstract-Conference.html .
- Trombetta et al., *Asking for Information by Evaluating the Communication and Coordination Trade-Off in Multi-Agent POMDPs*, **IEEE RA-L 2026**: reasoning about when information cost is worthwhile, https://doi.org/10.1109/LRA.2026.3703246 .
- This research **does not invent the idea of query cost/value, uncertainty-aware action, sensing, setpoint minmax, or finite-state POMDP planning**. The narrower systems opportunity is correct integration of a frozen robot policy with an *unobservably stateful private actuator-target controller*, two unknown delivery ACKs, actual robust native controls and a measured readback cost.

## Next falsification

Use a **new** source-registered, untouched independent set of PhysX reset states to test any rule motivated by the above counterexample. A revised candidate may combine task phase or task context with a future value-of-information estimate, but such modifications cannot be evaluated as prospective on these 620001/630001 results. Stop if the more sophisticated controller does not beat a cheap task-ID route and fixed early read on the same information-cost/success frontier.

No claim of L8/L9, human safety, original paper acceptance or independent third-party replication is supported by this report.
