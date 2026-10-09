# Independent reproduction challenge: hidden ACK and controller-target authority (v1)

**Status: open reproducibility request, not evidence of outside-laboratory validation.**
**Original frozen evidence:** [source-backed 32-reset/128-cell protocol](WHEN_ROBOT_ACTIONS_LEAVE_NO_TRACE_FLAGSHIP_V08.md) · [first-run author-operated PhysX archive](../frozen_policy_transfer/evidence/isolated_query_factorial128_first_3010001_3020016).
**Corresponding research-fork PR:** [#161](https://github.com/lindicaphxag-tech/ManiSkill/pull/161). This is **not** a ManiSkill upstream-merged research method and has not passed peer review.

## Why another lab's test matters

The existing source is author-operated CPU PhysX, using two unchanged published PPO checkpoints and one Panda-family controller. In the original cohort there are **32 separate initial reset IDs** (16 PullCube and 16 StackCube), physically crossed with all four ACK-held/applied truth patterns; **128** correlated task/truth cells and **1,280** native simulator controller-world trajectories. Three predecision-matched arms achieved the **same individual 104/128 task outcomes**. Public set-membership / same-public 0.95-score / fixed authoritative read used **102 / 122 / 127** actual privileged target reads, respectively, whereas the two adaptive arms consumed **256** extra public XYZ sample events each. **Twenty** independent reset clusters contributed the **26** accepted (zero observed wrong) complete target-history labels. It is scientifically incorrect to interpret 0/26 as a hardware safety guarantee or the 128 cells as 128 independent resets.

Two separate goals are offered. **Level A: verify the *existing records* independently**; **Level B: physically rerun *new initial states* at a different operator's discretion**. Level A is valuable software/data auditing but is **not** original-physics reproduction.

## Level A — Independent source-only re-audit (no simulator step)

Start in a fresh clone, ideally in an independently configured environment:

```bash
git clone --branch research/isolated-query-factorial-128-20261009 \
  https://github.com/lindicaphxag-tech/ManiSkill.git controller-ack-audit
cd controller-ack-audit

# Run from repository root; use the same evidence directory without edits.
python -m research.audit_query_isolated_same_reset_factorial128 \
  --source-dir research/frozen_policy_transfer/evidence/isolated_query_factorial128_first_3010001_3020016 \
  --output independent_source_audit.json

python -m research.review_original_factorial128_cluster_risk \
  --source research/frozen_policy_transfer/evidence/isolated_query_factorial128_first_3010001_3020016 \
  --output independent_cluster_risk.json
```

The audit depends on Git source identity and immutable original checksums; keep the original `.gitattributes` to avoid line-ending corruption on checkout. If the environment cannot import the package, report that as an unsuccessful replication attempt, not a silent source change. The author-run cross-platform audit is [public CI](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37946780980); an outsider must record **their own** command/environment/results to count as independent verification.

**Expected checks:** all 16 registered eight-reset original shard sources, all four ACK truths for each reset, original SHA256s, exact task identities and denominators, physically dispatched t2/t3 and neutral probe, actual achieved/target full-pose pre-t5 pairing, action-compiler/read-count provenance, all wrong-authority decisions (not only successful ones), and task-stratified cluster analysis. Do not change rejection gates to make the cohort pass.

## Level B — Independent *fresh PhysX source* with failure preservation

A truly new physical-in-simulation replication **must not** reuse the author-run 301xxxx / 302xxxx reset IDs, nor count the same raw archive again. The baseline physical runner is `research/run_query_isolated_factorial128.py` with CLI `--task {pull_cube,stack_cube} --chunk {0,1}`. **It is hard-pinned to the original protocol and original seed registry**, so a new-seed study requires a separate protocol and code branch; simply rerunning it does NOT create independent fresh states.

Before observing any new outcomes, the independent investigator should commit a timestamped specification with:

1. Independently chosen new seeds and *actual full simulator initial-state equality checks*, task distribution and complete 2×2 held/applied allocation;
2. Frozen model checkpoint hashes, controller source/action semantics, probe budget, response tolerance, stopping rules and the three comparator definitions;
3. Matched physically dispatched commands, full achieved/commanded SE(3) and public observations *before* method choice, audited per method and per truth;
4. Explicit decision-only privileged getter calls versus audit-only target reads, public XYZ acquisition events and actual physical probe steps;
5. A failure policy that retains any failed initial-state equivalence, missing fault exposure, mismatched action, early termination, or task failure in the complete denominator.

**Original candidate endpoints** are official task success, confident *wrong full-target* authorization, true target reads, extra public observations and actual actuation. Analyze whole four-truth **reset clusters** rather than treating repeated truths or ten controller worlds as IID task samples. A strong future comparison should add a **separately developed/tuned same-public-information scorer** and a genuine nonzero active probe with equal sensing/actuation budget; the frozen 0.95-score heuristic is not official ActionShift DualABI.

## Accepted independent report format

Provide a public repo/commit SHA, code and protocol differences from original, hardware/OS/simulator/GPU-or-CPU details, source-shard SHA256 manifests, *full source logs including failures*, reviewable per-reset decision ledger, task-specific results and exact methodology (including negative outcomes). Include one of:

- **A — data/implementation verification:** independently executed Level A audit on original archived author-operated results;
- **B — new original physics:** independent investigator actually executes unseen reset states with own frozen protocol;
- **C — external adoption:** another project *integrates/uses* the proposed method; this is a separate claim requiring a real upstream review/merge or documented downstream use.

Please report failed attempts and contrary evidence. No reward or authorship is promised automatically; collaboration and manuscript credit require explicit agreement. A successful author-controlled GitHub Actions workflow is *not* a substitute for an independent investigator.

## Falsification/stop rules

- If the full physical prefix is not matched, **do not infer task-level method causation** from a success difference.
- If the public-response model excludes the true controller target, **do not call low residual an authority certificate**.
- If additional public sensing/probing costs are not measured or priced, **do not claim total efficiency superiority** from fewer privileged reads alone.
- If wrong-authority errors occur in new sources, **preserve and report them**, even if task success remains high.
- If an independent test cannot run, **publish the failure log** instead of treating it as a passing replication.

**Contact:** open a focused discussion with exact reproducibility logs or contact the owner through the public GitHub profile. Do not confuse a contributor's fork or self-merged PR with an accepted official upstream feature.
