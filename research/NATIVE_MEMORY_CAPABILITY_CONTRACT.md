# Native controller-memory capability contract (research reference)
**Scoped, reviewable proof/test surface. No simulator task-performance result is produced by this PR.**

## Problem
In a target-relative controller, the same observed end-effector pose may coexist with multiple latent `target_pose` memories after unknown ACK delivery. A controller adapter must distinguish **physical target memory**, **epistemic information about that memory**, and **the actual privileges of an operation**.

## Exact scope
The finite-set reference here is for ManiSkill `PDEEPos/PDEEPoseController` with the independently verified `root_translation:root_aligned_body_rotation` native chart and known delivery; it does **not** generalize by assertion to joint, body-frame, multi-robot, or hardware controllers.

For all candidate memories `(p_i,R_i)`, a single known-delivered root-left target delta maps every candidate to `(p_i+d,R_d R_i)`; pairwise translational L-infinity and SO(3) geodesic diameters are invariant. In particular, common relative steps cannot make two distinct hidden commanded targets identical, even after repeated probing. `native_memory_funnel_certificate.py` additionally computes an exact bounded-translation worst-case goal-error lower bound and a universal SO(3) half-diameter lower bound. A negative certificate means impossible under that defined action class; a nonnegative check is **not** a proof of feasible/safe control.

`native_memory_recoverability.py` separately distinguishes:

- `relative_target_command`: requires both known-delivered ACK and verified native chart, transports hypothesis set without reducing diameter.
- `public_observation_without_validated_likelihood`: refuses to prune possible native targets based solely on a public EE sample.
- `trusted_target_read`: consumes one privileged getter and collapses knowledge, without modifying physical controller memory.
- `privileged_public_reanchor`: after independently verified simulator-internal native target write, collapses memory to the public achieved pose, counting one privileged write, with NO assumption of actual task success, safe contacts, or standard robot firmware support.

## Reproduction
```bash
python -m unittest discover -s tests -p 'test_native_memory_funnel_certificate.py' -v
python -m unittest discover -s tests -p 'test_native_memory_recoverability.py' -v
```

Tests cover unknown action delivery, unverified frame, quaternion double-cover, invariant memory diameters across multiple steps, impossible common actions, failed setter, and read-versus-write cost/semantics. Pure Python standard library; no GPU and no PhysX runtime required.

## Upstream handoff gates
1. Add a source-native end-to-end test against **real controller `set_action`, `get_state`, and `set_state`** in a version-pinned ManiSkill CPU environment; a mathematical reference alone is not sufficient to change upstream runtime behavior.
2. Demonstrate the behavior independently under at least two controller charts/robots, with no silent type conversion. Keep hardware unsupported claims out of the API.
3. Keep privilege types explicit. An application must never interpret `set_state` as a free, ordinary actuator command.
4. Keep the full PhysX development pilot and its statistical outcome evidence **separate** from this small reviewable patch: [pilot branch](https://github.com/lindicaphxag-tech/ManiSkill/tree/research/native-memory-reanchor-physx-pilot-20261010). It currently cannot be cited as a verified positive task result unless its all-shard source audit succeeds.

This PR does not claim to invent group invariance, belief-space planning or a new safety theorem. Its engineering goal is a reproducible, typed native-state authority boundary that downstream robot learning stacks could adopt after external review.
