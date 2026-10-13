# Single-bit-corruption-safe executed-action receipts: exact code and native PhysX falsification gate

**2026-10-13 — reviewer-facing RESEARCH PROTOTYPE.** Do not assert robotics task success, original coding theorem, experimental gain, external approval or Merge from a queued run.

## New explicit system fault versus existing source coding

Original native [64-world Panda/xArm6 execution-receipt study](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38363869998) assumes a **trusted receipt delivered without transmission corruption** and reports 64/96 quantized-controller graph conditions with shorter exact receipts. If the binary receipt can be corrupted by even ONE bit, an ordinary graph color code can be accepted as the wrong ACK history. This implementation asks for a **joint observable-state and one-bit-corruption-safe binary receipt**, rather than treating ACK transport as perfect.

Given four hidden executed ACK histories h, a registered bounded quantized public EE observation support Y(h), and source-computed native corrective command mode A(h), define a graph edge when Y(h) intersects Y(k) and A(h) differs. For *every* edge, assign binary receipt codewords c(h),c(k) with Hamming distance >=3. Then even after at most one adversarial corrupted transmitted bit, no receiver can observe the same (public sensor bin, corrupted receipt) for two different required correction actions. The producer solver searches the exact shortest binary code length 0–5 by backtracking.

This is classical **zero-error side information + one-error-correcting binary coding**, **not first-priority information-theory mathematics**. Strong original sources include [zero-error source-channel with decoder side-information, IEEE ISIT 2003](https://ieeexplore.ieee.org/document/1228155/) and [standard binary d=3 Hamming packing bounds](https://ma.rhul.ac.uk/~uvah099/Maths/Codes11/MT3612011Notes.pdf).

## Strongest relevant bit-cost control, not a strawman

There are four *possible ACK histories*. A true correctable **full-history** code of length **FIVE** binary bits and min Hamming distance three exists; e.g. words 00000, 11100, 10011, 01111. With only 4 bits no 4-codeword d3 binary code exists, so **five** is the best full-ACK block length. Simply triplicating both original raw ACK bits to 6 bits would be an unnecessarily weak baseline and is NOT used to claim gains.

Our side-information joint code may use fewer than five bits on a quantized EE observation support if graph nonconfusability permits. Missing receipts and invalid sensor assumptions are NOT silently recovered by this scheme. A valid unprotected 2bit code does not claim one-bit corruption safety.

## Exhaustive independent mathematical verification

A standalone independent enumerator (separate from source producer) checked **all 64 simple undirected labelled graphs on four vertices**, using complete Hamming-code assignment search and a separate analytic classification:

| Four-ACK confusability | 4-node graph count | Minimal binary bits to correct 1 arbitrary bit |
|---|---:|---:|
| No graph edges | 1 | 0 |
| Some edges, no triangle (bipartite for <=4 nodes) | 40 | 3 |
| Contains triangle | 23 | 5 |

**64/64** exact minima agreed with independent graph-theoretic derivation. The independently executed full JSON and source enumerator are in the conversation's supplementary downloadable evidence, not an outside referee or an independent external lab. This supports mathematical implementation correctness for n=4, not a general new coding theorem.

## New native physics experiment registered before results

- [Frozen original native reset/variant/ACK source protocol](NATIVE_ONEBIT_ROBUST_RECEIPT_PREREG_20261013.json), Git blob `53a4429f786e01a69670d61202da921fcc993f5a`.
- 4 **new** original reset clusters per morphology (Panda S5800411–S5800414; xArm6 S5900411–S5900414), 2 native command variants and 4 executed hidden ACK states: **64 original CPU PhysX worlds**, 3 frozen sensor angular quantization cells and 2 frozen bounded sensor component errors = **96** correlated original graph test conditions.
- [Source](robust_onebit_native_receipt.py), [adversarial Hamming tests](test_robust_onebit_native_receipt.py), [independent original-geometry/command auditor](audit_robust_onebit_native_receipt.py).
- [Native original PhysX two-morphology workflow #38385873953](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38385873953). **Status as last checked: QUEUED, not run and not passed.** It executes all possible single-bit ACK corruptions for every allowed original sensor bin, and compares shortest safe side-information receipt with **optimal five-bit full ACK**.
- Frozen positive systems benchmark gate: >=48/96 graph conditions save >=2 bits while remaining safe to any one transmitted bit corruption, >=16/48 such conditions in **each** native robot, **zero unsafe corrections**. All 8 independent reset clusters retained; 96 correlated sensor condition cases are not 96 independent robots.
- An outside code reviewer, original hardware ACK sender, calibrated sensor error law, native full PickCube task recovery comparison and actual robotics maintainer acceptance remain unachieved; even a positive queued CI result would be a systems correctness/cost observation, not a complete PhD new-algorithm adoption claim.

## Falsification boundary

If the robust codec does not beat the **five-bit optimal full ACK** on new seeds at the preregistered threshold, preserve the negative study without relaxing observation bins. If it beats that particular bit-count baseline, next perform a real runtime ACK-channel state model and compare actual full-task success/cost against fully informed Bayesian/controller alternatives, not just no-receipt guessing.

**No GitHub PR has yet been submitted upstream for this research prototype; source/validation branch is author-run.**
