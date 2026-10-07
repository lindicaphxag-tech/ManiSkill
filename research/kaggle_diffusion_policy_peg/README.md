# PegInsertionSide Diffusion Policy A/B assay

This Kaggle T4 experiment compares the official ManiSkill Diffusion Policy PegInsertionSide preset on the frozen base `62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3` with #1495 and the exact changed-file patch from [ManiSkill #1472](https://github.com/mani-skill/ManiSkill/pull/1472).

## Protocol

- Official public `PegInsertionSide-v1` motion-planning demos; the raw data stays in Kaggle and is not exported.
- Each arm independently replays the raw demonstrations under its own checked-out source tree; converted-dataset HDF5 and JSON SHA-256 hashes are recorded per arm.
- The treatment is frozen at #1495 `875ae4d8777678119b2f192ee186c6c15e6894d5` plus the controller line change and regression test file from #1472 `eed9be164797d41540421bda8adb3840377d7087`.
- Same seed (1), 100 demos, state observations, `pd_ee_delta_pose`, `physx_cpu` evaluation, 300-step horizon, batch size 1024, and 100,000 training updates.
- The measured variant uses 20 evaluation episodes every 10,000 updates and disables video to reduce runtime. The upstream script's default 100 episodes every 5,000 updates and video capture are not used; the training/update configuration is unchanged.
- TensorBoard curves are exported as CSV/JSONL. W&B is disabled because no W&B credential is part of the experiment environment.
- Checkpoints and demonstrations are deleted or kept outside the exported artifact set; only logs, scalar curves, source identities, and hashes are emitted.

## Previous run history

The private Kaggle kernel `oblivicore/maniskill-dp-peg-1495-1472` was submitted with a Tesla T4 request. Versions 1–3 stopped before training during dependency or demo preparation. Version 4 ended in `ERROR` after 2,735 seconds, before baseline training produced metrics: Gymnasium's `forkserver` evaluation workers inherited initialized CUDA state after `torch.manual_seed`, then failed with `Cannot re-initialize CUDA in forked subprocess`. Its paired data protocol was also invalid because it reused one base-replayed dataset across arms, so it provides no policy evidence. Version 5 ended during setup before training: Kaggle's Python 3.13 cannot resolve ManiSkill's pinned Linux dependency `mplib==0.1.1`. Its `experiment_log.json` records `status: failed` and a finish time, even though the Kaggle status endpoint still reports `RUNNING`. The #1472 test file also is not present in the exposed root-shaped commit tree, so the corrected runner fetches the pinned PR Files API patch and checks its blob SHA. Version 5 provides no policy evidence.

The runner installs ManiSkill in editable no-dependency mode, then installs its explicit runtime requirements without the unrelated `mplib` extra; policy training does not call motion planning. It then fetches and independently replays the official PegInsertionSide demos for each arm. The raw demos and generated replay datasets are deleted before output packaging.

## Paired assay run

The corrected runner from research commit `704a9f9` was submitted as private Kaggle kernel [maniskill-dp-peg-paired-assay-corrected](https://www.kaggle.com/code/oblivicore/maniskill-dp-peg-paired-assay-corrected), version 1, on 2026-10-08. Kaggle now reports `ERROR` after 3,234 seconds. The log reaches the baseline's initial 20-episode evaluation, then `diffusion_policy/evaluate.py` raises `KeyError: 'final_info'`; no policy metrics or training curve were produced. The output listing is empty.

Version 1 installed `gymnasium>=0.29.1` without an upper bound and neither recorded the resolved Gymnasium version nor selected the vector autoreset mode. A local smoke test on Gymnasium 1.2.0 reproduced the API mismatch: default `NEXT_STEP` returns no `final_info`, while `SAME_STEP` returns the `final_info` structure this evaluator reads. This identifies a concrete compatibility mechanism; because version 1 did not record its resolved package version, the local reproduction alone does not prove which exact Gymnasium version Kaggle installed.

Version 1 downloaded demonstrations using ManiSkill's helper, without pinning or recording the raw archive digest. A post-hoc check found that Hugging Face revision `d674485bbffdd533914e52d272fdda34c0515608`, file `demos/PegInsertionSide-v1.zip`, has SHA-256 `7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c`; fresh downloads from `main` and that revision matched.

Version 2, from research commit `3ea1aa4`, pinned the dataset revision and digest, verified the archive before extraction, rejected paths escaping the extraction root, and recorded source identity in `raw_dataset.json`. It pinned Gymnasium 1.2.0 and patched the isolated assay checkout to use `spawn` workers with `SAME_STEP` autoreset. Kaggle ran it on a Tesla T4; the runtime log records Python 3.13.15 and Gymnasium 1.2.0. Version 2 ended with `ERROR` after 1,179 seconds. Its baseline replay saved 90 converted trajectories from the selected 100 raw demonstrations, but the runner still requested 100; Diffusion Policy stopped at `AssertionError: num_traj: 100 > len(keys): 90` before training. Thus version 2 produced no policy metrics. The source archive's first 100 demonstrations are all marked successful, but that does not guarantee action replay succeeds under the target controller.

The next runner revision first replays each arm independently, indexes successful converted trajectories by the source `episode_seed` preserved in ManiSkill metadata, and forms a common-seed intersection. Both arms train on that exact intersection, in the same deterministic order; training is not started if fewer than 32 matched demonstrations survive. It records the selected-seed digest, paired HDF5 digests, and actual paired demo count. This preserves the treatment-specific conversions while eliminating the sample-count and episode-selection mismatch that invalidated version 2.

## Novelty boundary

This experiment does not claim a new general SO(3) action representation: the [SO(3) action representation study](https://openreview.net/forum?id=g4ZrpMQL1Z) already compares common representations at scale. It also does not claim that Cartesian delta actions or action adapters are new; [SPACE](https://arxiv.org/abs/2606.24049) studies them across embodiments and dynamics shifts. Controller-gain effects on behavior cloning are studied in [Tune to Learn](https://arxiv.org/abs/2604.02523). The narrower engineering question here is whether two specific ManiSkill action-conversion/controller changes compose correctly and alter the official PegInsertionSide diffusion-policy pipeline. The current two-arm comparison only estimates their combined effect; it cannot attribute an effect to either PR individually. No performance claim is justified without a four-cell factorial comparison and replicated seeds.

### Validity audit and correction

Before interpreting v4, an audit found that its runner replayed the raw demos
only once under the frozen base, then reused that converted dataset for both
arms. That is not a valid paired comparison for a change to action conversion.
No result from v4 is evidence for either PR. An earlier local audit used an
unpublished stale branch (`034e40c`) and incorrectly concluded the public PR
heads were sign-incompatible. The actual public #1495 head was `cdd6db7` and the
current PR branch now includes a runtime scale adapter; see
[the corrected action-sign audit](ACTION_SIGN_AUDIT.md).

A single seed supports a paired mechanistic comparison, not a statistically powered performance claim. Success-rate increments have 0.05 resolution at each 20-episode evaluation point.
