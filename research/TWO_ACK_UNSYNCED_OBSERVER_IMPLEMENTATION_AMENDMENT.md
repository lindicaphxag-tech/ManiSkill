# Pre-result implementation amendment — two consecutive unknown ACKs

Original clean-cohort protocol was committed as `research/TWO_ACK_ACTUATION_AUTHORITY_FRESH16_PRECOMMIT_V2.json` before any new 430/440 result. First technical CI [37898675865](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37898675865) FAILED **before completing ANY full 8-case source task shard**.

## Root cause

At the first held command (step 2), the protocol intentionally hides delivery acknowledgment from the *mandatory one-read-at-step-4* observer. The observer correctly becomes unsynchronized. At step 3 a second actual native zero-arm command is physically injected, but the initial runner unnecessarily called the observer's next-command `prepare` while it is correctly unsynchronized, resulting in `RuntimeError: Observer unsynchronized; reset/resync required`.

**This is a test-harness bug, NOT a successful policy recovery or a proposed relaxation of fail-closed controller behavior.** The original frozen observer is correct to refuse command authorization under unknown delivery.

## Exact necessary implementation correction

For only the *mandatory-read* comparator at the second planned physical fault step (step 3), whose native arm output the injector forces to ZERO regardless of policy, call native PhysX `env.step` with exactly the same ZERO arm delta and original policy gripper. Record the forced-native-hold event, check pre/post actual private target **in an audit-only pathway**, do NOT call the unsynchronized observer's `prepare`, and never assert a hypothetical intended-command certificate. At the following nonfault step (step 4) perform the originally specified **one** genuine private-target read and explicitly resynchronize the observer.

No source policy weights, controller chart, threshold, real fault step, budget or task success evaluator may change. Retain all registered seeds and negative outcomes. No missing simulator outcome is silently treated as success. The current 430/440 cohort is an **amended pilot**, not a pristine untouched hypothesis test. A genuinely additional unseen cohort would be required for a stronger prospective replication claim.

The first technical failure is permanently linked above; do not present it as a passed 16-state experiment.
