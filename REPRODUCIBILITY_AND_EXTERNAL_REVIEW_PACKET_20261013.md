# Reproducibility challenge: engineering, algorithmic evidence, outside review

**Public third-party research review packet. Date: 2026-10-13.**
This is a ready-to-run reproduction plan, NOT a paper accepted by anyone, NOT an independent researcher's replication, and NOT an official admissions score.

## A. The single strongest new upstream engineering candidate: EEGCLIP distributed global negatives

Official [braindecode/braindecode #1320](https://github.com/braindecode/braindecode/pull/1320). **Status open, unmerged**, source head since the maintainer base sync `42621f6c6b381d7a57343c4987104d2cc73bc936`.

A reproducible falsifiable result: true PyTorch DDP two ranks with 2+3 and 0+5 paired EEG/Text examples should exactly match central five-pair gradients (EEG encoder parameters, text projection and learnable temperature). The 0-local forward used to fail via `reshape(0,-1,D)`; collectives must fail in sync for invalid paired shapes, rather than deadlock.

Reproduction protocol (CPU Gloo, no private data):
1. Checkout exact official PR source SHA above. Python 3.12, `pip install -e '.[tests]'`.
2. `python -m pytest -q test/unit_tests/models/test_models.py -k eegclip -ra`.
3. `python -m pytest -q -n 2 --dist worksteal test/unit_tests/models/test_models.py -k eegclip -ra`.
4. Verify real loss/gradient oracle numerically and actual 0+5 distributed backward, not just abstract mocked gather.

**Verified old-head result:** [normal three-OS 14/14 each](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38383960348) and [xdist three-OS 14/14 each](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38385161611) under head `b3a30049`; all successful. **Exact latest maintainer-synced head** [three-OS + normal/xdist validation](https://github.com/lindicaphxag-tech/braindecode/actions/runs/38386647465) was submitted, but its status must be checked; no retrospective pass assumed. Official full upstream test [#38342524442](https://github.com/braindecode/braindecode/actions/runs/38342524442) **cancelled after ~6h**, not passed. Latest head official full suite is separate.

**Reviewer question:** Is a model-scoped opt-in distributed loss acceptable in Braindecode or should it be a generic reusable contrastive loss helper? Implementation correctness and public API ownership are different dimensions. Approval and Merge require actual project maintainers.

## B. Research prototype requiring independent native-controller study, not another coding theorem

Original public source repository branch [native-one-bit-robust-receipts-20261013](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/native-one-bit-robust-receipts-20261013). Program [robust_onebit_native_receipt.py](research/robust_onebit_native_receipt.py), [pre-registered *new* reset seeds and 96 graph conditions](research/NATIVE_ONEBIT_ROBUST_RECEIPT_PREREG_20261013.json), [basic tests](research/test_robust_onebit_native_receipt.py), [independent reconstruction auditor](research/audit_robust_onebit_native_receipt.py).

Four hidden real CPU PhysX controller ACK histories per task/seed/variant. Receiver observes quantized original public end-effector pose and a binary receipt with **up to one adversarial bit flip**. The new controller-specific artifact finds the shortest code with pairwise Hamming distance >=3 only on pairs that share possible sensor values but need different future corrective commands. Compare against a **best possible full four-symbol 5-bit error-correcting code**, not a weak 6-bit repeated ACK. Every feasible observation and bit flip must be checked.

**Independent verification of finite combinatorics:** all 64 possible undirected four-history graphs were exhaustively examined by a separate local code implementation, agreeing 64/64 with the known min-bit classification 0 bits (1 edgeless), 3 bits (40 triangle-free nonempty), 5 bits (23 graphs with triangle). These are classical codes/graphs, not a first mathematical theorem.

**Original new data status:** [64 new PhysX worlds, 96 cases workflow](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38385873953) **QUEUED when written**; no native-result win claimed. The test is of **idealized known bounded camera noise and a trusted sender**. It does not establish recovered PickCube task completion, true camera calibration, medical utility or independent research validation.

## C. Not a public manuscript: source-only EEG regularisation and time-correlation correction

The unpublished DefaultReg manuscript stays in a **PRIVATE** user-owned repo. A new private [temporal-logvariance exact quadrature source module](https://github.com/lindicaphxag-tech/defaultreg-eeg/blob/research/crossfit-spectral-geometry-logcalib-20261013/defaultreg_experiment/temporal_logvariance_bias.py), independent AR(1) Gaussian controls and full **2880 original draws + 480000 independent numerical checks** are available to collaborators with permission. Frozen superiority gate FAILED (exact estimator better than equal-oracle-information effective-n in 6/8 strongly autocorrelated null cells, 7/8 absolute bias threshold), and the real 16-subject EDF experiment has not run. Mathematically the Laplace weighted chi-square logarithm identity and sample splitting are prior art. **Do not mirror this manuscript publicly or claim any out-of-cohort decoding AUC benefit.**

## External-review question and strict evidence requirement

A genuine third-party can independently (i) reproduce real DDP centralized-vs-distributed parameter gradients and evaluate API scope; (ii) verify whether the true PhysX receipt's information requirements and assumptions survive a different robot/sensor/error model and meaningful end-task success; or (iii) critically audit private EEG projection identity under properly authorized access.

Technical feedback, independent new samples or legitimate upstream merge on the **same** mechanism would count as outside recognition. A self-authored GitHub CI, GitHub star, profile badge, preprint upload or review-request message alone does NOT.

This challenge intentionally exposes falsification paths and original negative outcomes rather than a manufactured multi-flagship success claim.
