# Independent reproduction protocol — evidence-gated controller target memory

This page is for outside research engineers who want to **replicate OR falsify**
the published frozen-policy claim on source-new robot task reset seeds. A
successful contributor-run GitHub Action is **not** independent outside-lab validation.

## One-click execution

1. Fork the public repository `lindicaphxag-tech/ManiSkill` into **your own GitHub account** (not the author fork). Enable GitHub Actions if requested.
2. Go to **Actions → Outsider-selectable 6-arm observability-gated PhysX reproduction → Run workflow**, choose `task` (`pull_cube` or `stack_cube`), actual `fault` (`applied_no_ack` or `neutral_arm_delta_no_ack`), an **unseen** `first_seed >=230001`, and `cohort_n=8`. For a quick functionality check first, use the author's one-seed smoke CI; it is **not** a research-level reproduction.
3. Retrieve the `outsider-selected-observability-gated-<run id>` artifact from your **own fork's run**. Keep the full `UNCHANGED_original_physx_*.json`, `external_hybrid_summary_*.json`, `SHA256SUMS`, Git/source blobs, Python environment freeze and entire stdout log.
4. For task-level generalization, run **BOTH command truths** on the **same newly selected seed interval**. This gives a paired task×truth comparison, not independent 16 policy implementations. Ideally also run the other frozen PPO/task. **Report all failed episodes and fault-step non-exposures**, never drop inconvenient seeds.

The **same six genuine native PhysX controller arms** are actually stepped:
original no-fault PPO with a common probe pause; blind optimistic history;
blind pessimistic history; public achieved-motion history inference that
refuses uncertainty; **public unique history OR one privileged target
read when ambiguous/model-incompatible**; mandatory privileged target
read after the same native probe.

The frozen source program is checked by exact Git blob identity:
`research/frozen_ppo_observability_gated_query_fresh32.py`,
`research/empirical_probe_response_classifier.py`. The published
two external frozen third-party PPOs are loaded from their exact
revision and verified by SHA256. The standard-library wrapper independently
recounts EVERY actual task success, private target read, public-history
label and wrong confident history label. You can run the same wrapper locally:

```bash
python research/external_observability_query_replay.py \
  --task pull_cube \
  --fault applied_no_ack \
  --first-seed 231001 \
  --count 8 \
  --output-dir replication_artifacts
```

Your computer needs the ManiSkill runtime, Python 3.11, the repository's
editable Python dependencies plus `huggingface_hub`, and an official
ManiSkill-compatible PhysX CPU environment. The GitHub workflow installs
these dependencies automatically. Any `cohort_n=8` can take longer than
the short integration smoke.

## Source-pinned benchmark to check reproduction against

**The original, already observed study is not new independent evidence.**
It is a reference for diagnosing mismatch:

| Condition, original 32 paired trials | Native task successes | Privileged reads at decisions |
| --- | ---: | ---: |
| Blind optimistic history | 23 | 0 |
| Public response with stop-on-ambiguity | 19 | 0 |
| **Public response OR single target read** | **27** | **11** |
| Always read the target after identical probe | **27** | **32** |

Original outcomes are exactly paired: 27 successes for BOTH query methods,
five failures for BOTH; no discordance, 21 public-only unique history
labels, zero observed wrong confident history labels in THAT cohort.
[Eight unchanged source PhysX JSONs, full independent audit and hashes](./evidence/observability_gated_query_fresh32/)
and [successful source-only audit](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37833936506).

**Do not reuse original reset seeds** 180101–180108 or 190101–190108
as supposedly unseen evidence. The historically calibrated error envelopes
are empirical and NOT externally attested: a different genuine PhysX
prospective cohort **excluded the true controller history in one state**,
which is a published falsifier. [Negative source evidence](./evidence/empirical_public_response_new32/).

## Exact metrics external replicators should report

For each task×actual execution truth: number of intended faults genuinely
reached, number of probes executed, number of source PPO competent cases,
actual official task success flags for all six arms, **paired discordant
successes** hybrid-only / always-only (not just pooled fractions), total
selective vs compulsory target reads, public unique-label coverage,
**wrong confident hidden-history labels**, and counts of ambiguous and
model-invalid public responses. Additional failure types: nonfinite
evidence, unknown model/weights, changed Git blob, missing native
PhysX success flags or incorrect readback budget, each of which should
**refuse to report success**.

On real robots, your private controller memory, physics update gains,
action frames, ROS ACK pathways, contact forces, latency and camera
noise differ. The current experiments **do not verify** hardware safety,
mathematical controller identifiability, model-free VLA transfer or
statistical noninferiority. A whole new physical calibration/error-bound
assessment would be needed before making such claims.

## What would constitute actual external scientific recognition?

An **unaffiliated** person or lab, controlling its OWN GitHub fork and
fresh seeds, publishes an auditably complete reproduction (including
negative cases); or an official upstream maintainer reviews and adopts
a relevant patch; or an independently reviewed paper accepts the work.
An author-side smoke CI, internal fork merge, GitHub star, unreviewed
comment, or issue opening is NOT those outcomes.
