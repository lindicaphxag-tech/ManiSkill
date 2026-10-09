# The mandatory simple baseline: when to query is not the same as whether a command is certifiable

**Scientific status:** retrospective, author-derived analysis of an independently source-audited previous 64-original-reset-state, 448-real-native-controller-world PhysX benchmark. No new simulator world was stepped for this review, no policy was trained and the analysis is NOT an independently replicated or prospectively evaluated new controller.

Source: [original public real PhysX 8-shard run](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900209486), [successful source/checkpoint/full-denominator audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37900694213). Full original source raw artifacts remain linked to that run; this note's eight-source-job summaries are *derived transcriptions*, not byte-identical original trial records.

## 1. Original prospective result is negative for event-triggered task-success superiority

Two sequential native controller target holds at simulator steps 2 and 3 produce **four real plausible previous commanded target memories** under unknown delivery ACK. The original unchanged third-party released pretrained PPOs were tested on previously unseen PullCube 420001–420032 and StackCube 430001–430032 resets. Every original fault reached its target worlds. Same seeded full-controller comparisons:

| Actual original native method | PullCube successes | StackCube successes | Pooled successes | Real private target reads |
| --- | ---: | ---: | ---: | ---: |
| Zero-read bounded common action / refuse | 9/32 | 2/32 | 11/64 | 0 |
| **Reactive: wait until bounded certificate fails, then read once** | **32/32** | **13/32** | **45/64** | **44** |
| **Fixed: read once at step 4, before more contact-rich control** | **32/32** | **23/32** | **55/64** | **64** |

Paired original-state outcomes: 42 both succeed, 3 reactive only, 13 fixed only, 6 both fail. Two-sided exploratory exact McNemar p = 0.021270751953125 in the direction AGAINST the event-triggered policy (not multiplicity adjusted or robot-population-calibrated). The benefit from 20 fewer privileged target-memory reads comes at the empirical cost of ten failed original task states. There are only two frozen PPOs and one Panda native controller family; 64 reset states are not 64 unrelated robots/policies.

## 2. A simple **posthoc** task-conditioned opponent nearly defeats the research premise

Define a policy choice available *before the first action*, using only public task identity:

- PullCube: run the ORIGINAL reactive policy.
- StackCube: run the ORIGINAL early fixed-t4 read policy.

Because every original policy arm was ALREADY physically run on exactly the same task reset seeds, we may compose its conditional source-cohort task success/read outcomes **without pretending the combined hybrid was executed as an additional original physics trial**.

| Task-dependent rule on those fixed original source states | Composed successes | Composed reads | A physically executed combined controller? |
| --- | ---: | ---: | --- |
| Original reactive for both tasks | 45/64 | 44 | YES, actual previously run source arm |
| Original fixed-t4 for both tasks | 55/64 | 64 | YES, actual previously run source arm |
| **React for PullCube, early read for StackCube** | **55/64** | **55** | **NO — retrospective outcome composition ONLY** |

This trivial rule uses **nine fewer** reads than always-fixed, while yielding the **same observed per-seed binary task-success vector**. The reason is checkable: BOTH actually executed policies succeed on ALL 32 PullCube reset states, and the StackCube branch of the composed rule is identically the source-fixed branch.

CRITICAL: The rule was selected AFTER seeing the task-stratified original outcomes. It cannot be reported as an independently preregistered result, a new 64-state simulator run, a real deployment strategy, a causal policy improvement or a significant advantage. It requires fresh seed-disjoint evaluation and ideally a distinct controller family.

## 3. A limited mathematical mechanism for why delaying information is risky

For a known root Cartesian additive native controller command that applies in EVERY credible prior target history,

\[
p_i^+=p_i+u \implies \|p_i^+-p_j^+\|_\infty=\|p_i-p_j\|_\infty .
\]

For the SAME known root-left SO(3) native command applied to all previous target histories,

\[
R_i^+=\Delta R R_i \implies
d_{\mathrm{SO3}}(R_i^+,R_j^+)=d_{\mathrm{SO3}}(R_i,R_j).
\]

Thus **when all credible histories receive the identical known common command with no new unknown ACK**, their pairwise commanded-target separation is invariant. Common open-loop action alone cannot collapse hidden target-memory uncertainty. This is elementary translation/isometry geometry, NOT a novel general observability theorem, learned dynamics assumption, collision-safe control proof or a result about the achieved end-effector pose. Unknown later ACKs can branch histories, and trusted target-state reads can collapse them.

The bounded-action certificate answers: **Can we command this target without exceeding declared setpoint-error bounds for every credible private target history?** It DOES NOT answer: **Is it worth deferring information until an action becomes uncertifiable, after earlier movements and physical contacts?** In StackCube, the previous physically certified actions may change subsequent contact dynamics and gripper interactions even though the hidden target-memory separation does not shrink. The original task failure pattern is consistent with this possibility but does NOT isolate causation from earlier actions, contacts or observations.

## 4. Real original-science gate for a substantially better method

A future true contribution needs a **prospectively frozen** state-aware precontact information-value rule that can observe public gripper state, achieved-pose features and belief geometry, but NEVER peeks at the privileged controller target or test success. Then test on untouched independent original-seed cohorts against: (a) fixed step 4, (b) reactive geometry failure, (c) this simple task-conditioned hybrid, (d) zero-read bounded, and (e) full oracle. Match or explicitly price actual controller-private reads and probe actions. Preserve ALL missed actual injected faults, refused actions, original PPO task failures and task-stratified paired outcomes. More controller families and external researcher PhysX reproduction are needed for a broad research representative work.

### Independent short verification without installing PhysX

The standard-library code in review/strong_task_stratified_query_baseline64.py loads eight actual job-log-derived task summaries with exact original GitHub Actions Job IDs and source seed ranges. It verifies original prospective run 37900209486, all originally source-audited per-task successes/read counts, full fault exposure and K=4 hypothesis evidence. Mutating successes, job ID, seed ranges, private reads or a fault exposure fails closed.

Execute two commands in the repository:
1. python -m unittest discover -s tests -p test_strong_task_stratified_query_baseline64.py -v
2. python -m research.frozen_policy_transfer.review.strong_task_stratified_query_baseline64 --input research/frozen_policy_transfer/review/original_64_compound_ack_task_shard_logged_summaries.json --output /tmp/strong_baseline.json

This reviewer audit provides **a stronger and more falsifiable novelty threshold**, not a posthoc claim that existing reactive or task-based adaptation has already won against state-of-the-art active sensing on new robotics systems.
