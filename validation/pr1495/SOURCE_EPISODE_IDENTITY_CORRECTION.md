# Source-Episode Identity Correction

Status: **methodological correction; supersedes source-episode claims derived from output HDF5 trajectory keys**

## What was wrong

Early same-base replay summaries treated output groups such as `traj_0 ... traj_7` as if they preserved the source demonstration episode IDs.

That is not valid for ManiSkill's `RecordEpisode` wrapper.

The production implementation:

1. assigns a new recorder-local `_episode_id += 1` whenever a trajectory is saved;
2. skips failed trajectories when `allow_failure=False`;
3. runs `clean_trajectories()` on close;
4. explicitly renames retained trajectories to consecutive `traj_0, traj_1, ...` IDs.

Therefore an output key identifies the **saved-output ordinal**, not the source demonstration episode.

## Direct correction from the original replay log

For public same-base run `37403056943`, the replay program itself printed the original source `episode_id` on failures.

The true source outcomes were:

- current main: **9/10**, source failure = **episode 2**;
- contract adapter v2: **8/10**, source failures = **episodes 1 and 2**;
- adapter v2 + controller fix: **8/10**, source failures = **episodes 1 and 2**.

Thus the additional candidate regression in that run was source **episode 1**, not episode 8.

The count result `9/10 vs 8/10 vs 8/10` remains valid.

The old exact success-set interpretation `0–8 vs 0–7` does not.

## Consequence for the saturation-authority hypothesis

The earlier `SATURATION_AUTHORITY_HYPOTHESIS.md` targeted source episode 8 because of the invalid output-key identity assumption.

That causal target is therefore invalid.

The code-level observation remains real:

- the caller uses `||a_rot|| > 1` as both clipping and residual-retry control flow;
- internally clipping in the converter can hide that signal.

But the experiment tying that mechanism to the observed 9/10→8/10 regression is **superseded** and must not be cited as causal evidence.

A later exact source-episode-8 trace independently confirms that episode 8 succeeds under main, candidate, and candidate+controller-fix.

## Correct identity source

For serial ManiSkill replay, source episode identity may be recovered from the replay program's failure message because it prints:

`episode["episode_id"]`

before output recording/cleanup renumbers saved trajectories.

The current summarizer therefore:

- parses source failure IDs from the replay log;
- cross-checks the reported success count;
- treats HDF5 group keys as renumbered output identity only;
- marks execution decisions provisional until repeatability is established.

For stronger future audits, source episode identity should be retained explicitly in a machine-readable outcome manifest rather than reconstructed from HDF5 group names.

## Research-integrity implication

This correction is retained publicly because SemRepair's thesis is itself evidence-gated authorization.

The same standard applies to the research artifact:

[
ArtifactCountCorrect \not\Rightarrow IdentityCorrect.
]

A count can be right while the causal attribution to individual examples is wrong.

## Claim boundary after correction

Still established:

- 9/10 main vs 8/10 candidate vs 8/10 candidate+controller-fix in run `37403056943`;
- exact count-level controller invariance in that run;
- source failure IDs from the original replay log: main {2}, candidate {1,2}, fixed-controller candidate {1,2}.

Retracted / superseded:

- output `traj_k` interpreted as source episode `k`;
- claim that source episode 8 was the candidate-only regression;
- causal attribution of that regression to the saturation/retry ownership bug.

Next diagnostic target:

- source episode **1**, with identity bound from the input metadata/log rather than output HDF5 naming.
