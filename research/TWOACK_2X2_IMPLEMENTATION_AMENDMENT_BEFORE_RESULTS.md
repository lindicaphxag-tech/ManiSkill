# Pre-result implementation repair: fixed-read comparator must not access a desynchronized observer

**9 October 2026; after first attempted CI #37919161678 failed at the first registered physical episode, before any complete original eight-trial shard / 64-case result was produced.**

## Specific discovered failure

The first attempt used `as_pose(observers[n].pose)` at the second unknown-ACK action on the fixed-read comparator. `ActionHistoryObserver.pose` intentionally raises `RuntimeError("Observer unsynchronized; reset/resync required")` after an unknown acknowledgement. Multiple original CI shards correctly failed. The experiment therefore produced **no complete task-level 2×2 study and no numerical efficacy evidence**. Preserve CI #37919161678 with original failed-step logs; do not label this a method efficacy result or erase it.

## Locked, minimally authorized correction

The fixed-at-step-5 target-read comparator may not consult an unsynchronized memory observation at physical fault step 3. It now uses the **public, achieved end-effector pose `arm.ee_pose_at_base`** as the `old_override` for a provisional, potentially semantically wrong relative-action rewrite. Its exact physical target-dispatch truth still varies across both `(t2,t3)` ACKs on the precommitted seed-modulo-four schedule. There is **no private target getter used as the step-3 action decision input**. At step 5 it performs the same **single counted authoritative target read** previously preregistered, resetting its observer. This is an intentionally information-poor fixed-late-read comparator, not an oracle. Failures resulting from a pose-vs-target mismatch must remain in the denominator.

**Unchanged:** source PPO/checkpoint, seed range and four truth assignments, task horizon, empirical public-response model and epsilon/margin, position/rotation native setpoint bounds, nine arm identities, physically delivered known neutral probe step 4 for all faulted arms, delayed read at step 5 and the independent audit logic. No outcome-conditioned retuning or sample exclusion.

## Reporting requirement

Source gate pins the amended Git blob, not the crashed pre-amendment blob; report both attempts in the manuscript and show exact completed run SHA. A complete study may be reported only once eight physical shards and all-population source auditing succeed. Even then, the 2×2 truth groups are assigned to **different reset IDs**, so cross-truth comparisons are not per-reset counterfactuals; within a truth group each method is paired on its own reset identity.
