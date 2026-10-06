# Late-Stage Dynamical Amplification Hypothesis

Status: **preregistered before inspecting the material-divergence raw-action window**

## Evidence available before this hypothesis

The source-identity and repeatability gates have already established one stable
discordant case under the frozen first-10 serial replay protocol:

- current main succeeds on source episode 1 in 5/5 fresh-process repeats;
- clean adapter v2 fails on source episode 1 in 5/5 fresh-process repeats.

The first source-bound episode-1 trace additionally established:

- main final success: true;
- adapter v2 final success: false;
- adapter v2 and adapter v2 + controller-sign fix are nearly identical;
- candidate vs fixed-controller has no retry-count mismatch;
- candidate vs fixed-controller maximum EE rotation difference is approximately 3.4e-6 degrees;
- main vs adapter has an initially tiny physical divergence;
- main vs adapter reaches a large late difference (max observed about 6.9 cm EE position and 5.84 degrees EE rotation);
- the first observed retry-count mismatch is at source step 144 (main: 1 iteration, adapter: 4).

The raw action/residual window around the first *material* physical divergence has not yet been inspected.

## Hypothesis

The stable episode-1 regression is not primarily caused by controller-sign migration and is not initiated by a retry-count mismatch.

Instead, a small main-vs-adapter action/pose difference is amplified late in the closed-loop trajectory. The amplification moves the executions into different physical basins; only after that physical divergence does the residual/retry protocol itself diverge.

This is a hybrid/dynamical hypothesis. It does **not** presuppose that contact is the cause.

## Frozen predictions

Define the first material divergence as the first source step satisfying at least one of:

- EE position difference > 1 mm;
- EE rotation difference > 1 degree;
- task-success predicate differs.

Before inspecting the new detailed trace window, the predictions are:

1. candidate and candidate + controller fix remain effectively identical around the material divergence.
2. The first material main-vs-candidate divergence occurs **before** the first retry-count mismatch at source step 144.
3. Before the material divergence, retry counts remain equal.
4. The raw action / residual window shows increasing physical residual or state separation rather than an abrupt controller-sign-dependent branch.
5. If the first material divergence occurs only *after* retry-count divergence, this hypothesis is falsified.
6. If candidate and fixed-controller materially separate, controller migration cannot be ruled out and this hypothesis is falsified/incomplete.

## Why this matters

If supported, the case demonstrates a stronger failure mode than simple value conversion:

LocalSemanticImprovement does not imply TrajectoryBasinPreservation.

A small semantic change can alter a closed-loop embodied trajectory enough to cross a hybrid/contact/task boundary, after which downstream residual control and task outcome diverge.

This would motivate an execution certificate that measures not just endpoint task success but also **trajectory-level effect sensitivity** around repaired semantic boundaries.

## Claim boundary

This is a preregistered mechanism hypothesis for one stable source episode. It is not yet evidence of a general hybrid-systems law, contact amplification, or safety property.
