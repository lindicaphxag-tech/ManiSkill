# Source-normalized XYZ vs ordinary reset-centering: a critical identifiability control

**Formal limitation identified before reading the new held-out PhysX results, 2026-10-13.** This document prevents a positive pilot result from being misrepresented as a novel source-specific invariance.

The currently frozen native control chart is `root_translation:root_aligned_body_rotation`, with `use_target=True`, `use_delta=True`. The two uncertain commands and the prefix commands are *fixed for each robot*, and the native translation mapping uses fixed symmetric per-axis bounds.

For robot body `r`, reset seed `s`, commanded target reset position `p_reset(r,s)`, and the same fixed source nominal command sequence, the source-replayed all-applied goal has the **additive** structure

`g(r,s) = p_reset(r,s) + c_r`

where `c_r` is a constant across all reset seeds for this robot/controller/nominal command sequence. Root-frame translation increments do NOT depend on orientation under this pinned ABI, and all candidate-specific rotational components for t2/t3 are zero.

The advertised source feature of the first held-out experiment is

`f_source(r,s,h) = x_public(r,s,h) - g(r,s)`

so equivalently

`f_source(r,s,h) = [x_public(r,s,h) - p_reset(r,s)] - c_r`.

Let `f_reset=x_public-p_reset`; for a within-robot Euclidean nearest-centroid classifier whose class centers are fit to the corresponding same-shift training features,

`argmin_h ||f_source_test - mean_train(f_source_h)||^2`

**equals exactly**

`argmin_h ||f_reset_test - mean_train(f_reset_h)||^2`

because the same constant `c_r` cancels from both distances.

Thus even if the fully frozen prospective 128-world experiment shows significant/complete improvement of SOURCE_RELATIVE_XYZ relative to ABSOLUTE_XYZ, it **does not isolate a source-specific mechanism over an ordinary reset-centered feature**. Both may be equivalent within this very narrow fixed-root-translation controller experiment. This confound was recognized after the *earlier exploratory* 160-world analysis but **before the prospective held-out outcomes were available**. We do not modify the preregistration, seeds or classifier in response.

## What can legitimately be established by the current prospective test?

Only that the pre-frozen relative-coordinate classifier is valid under new PhysX reset states compared with raw absolute XYZ, no-action and a privileged oracle. A result at or near the oracle proves that simple observability, not necessarily Theory-of-Mind, extra active information or a novel VLA recovery operator, suffices under this restricted task.

## Required stronger prospective falsification experiment

1. Include **reset-centered public XYZ** as an explicit strong baseline, with an independently recorded public reset achieved pose. Both source and reset-centered methods must use the exact same train/test reset cohorts and candidate actions.
2. Vary **nominal commanded action histories**, controller frame/rotation semantics or state-dependent dynamics to test a situation where a mere constant spatial origin shift is mathematically insufficient. Only registered source-compatible charts are admissible; fail closed otherwise.
3. Include a calibrated publicly observable/noisy ACK sensor and a policy that actually selects an action without knowing the hidden ACK. Evaluate abstention, cost, actual task success, contact and physical limits, not only end-effector target error.
4. Test new robot bodies/tasks, stronger learned and system-identification baselines, and independent external replication before claiming novel scientific superiority.

**Priority/narrative rule:** The claim `source normalization is a breakthrough over reset normalization` is **invalid for the frozen fixed-command root-translation setup**. The separate 160-world PhysX cost matrix and information-capacity lower bound remain valid *within their published constrained decision class*; they do not depend on this novelty interpretation.
