# Compound unknown-ACK prospective v3 — mandatory readback belief corrected

**Frozen before v3 native PhysX task results.** Previous failed runs remain inspectable and are not included as successful data.

### V1 result (failed before any full 16-state results)
[Native run #37897829784](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37897829784) correctly stopped because the first version tried to verify a command that had been intentionally replaced with a zero/hold action in the simulator.

### V2 result (failed before complete task denominator)
V2 correctly excluded masked commands from post-execution error checking, but its **mandatory post-fault readback comparator** still held only a single invalidatable command-history observer. Waiting until t=4 while two unknown ACKs occurred at t=2 and t=3 made the observer unsynchronized when asked to issue its prequery action. Explicit runtime error: `Observer unsynchronized; reset/resync required`. Do not falsify this result as a physics or performance success.

### V3 correction
- Every method requiring a bounded action before its first post-fault authoritative query, **including the fixed-t=4 mandatory-read comparator**, now retains a complete `UncertainDeliveryBelief` with 1–16 distinct target hypotheses. It may issue an action only when every candidate target satisfies the same certified setpoint error budget. If no common authorized command exists before its mandatory query, the comparator stops/fails closed. Only the explicitly named optimistic arm may keep an ACK-assuming single observer.
- At t=4, if still alive, the fixed-time method makes one **counted authoritative read**, collapses the belief to the returned target, then resumes. Selective method is allowed one evidence-triggered earlier or later read. Never pass a private controller state to prequery decisions or pretend all seven arms have matched information.
- The natural underlying two consecutive native target-hold faults remain t=2 and t=3, gripper unaffected; both acknowledgements remain unknown.
- Only physically dispatched certified actions undergo after-step real controller setpoint audits. Injected held actions are logged as **not dispatched** and never counted as physically verified bounded actions.
- **Fresh unexplored reset states:** PullCube-v1 400001–400008 and StackCube-v1 410001–410008, 8 per task, seven matched source worlds per state; no policy retraining.
- Unchanged registered ActionShift released PPO checksum and original single-fault/source SE(3) certifier blobs are verified in GitHub CI. New multi-hypothesis command selection remains conservative in SO(3) and checks exact measured post-dispatch setpoint residuals, not collisions, contacts, force or hardware safety.
- Complete denominator or explicit failed-trial/exception is mandatory. No predetermined favorable outcome. Reports: official task successes, private decision reads, maximum surviving belief width, masked-bound attempts, physically audited bounds, controller failures.

### Scientific status
Method development has used native failure logs from V1 and V2. **Only data generated from the new V3 seeds after this freeze can be called an untouched v3 prospective cohort.** No generalization claim to a new embodiment, unseen controller or robot hardware. A v3 experiment is candidate evidence, not original-paper peer review, model-free safety or independent external adoption.
