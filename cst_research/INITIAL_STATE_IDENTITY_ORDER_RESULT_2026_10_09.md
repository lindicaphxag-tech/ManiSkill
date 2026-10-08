# Same-seed 10014 physical-state identity order-effect diagnostic

**Public completed CI:** https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/37810657148

**Protocol written before run:**
[INITIAL_STATE_IDENTITY_DIAGNOSTIC_PROTOCOL_2026_10_09.md](INITIAL_STATE_IDENTITY_DIAGNOSTIC_PROTOCOL_2026_10_09.md).

In one job the same frozen ActionShift PPO, Panda/PickCube source / compiled
/ raw-copy code was executed in two schedules:

- **isolated**: seed 10014 only;
- **prefix**: run seeds 10001 through 10014, compare the last outcome.

Both seed-10014 schedules had **the same** source initial-observation hash
`993f09a396e8ec121b12feb14f11bd3add5d9930ea637cc50b01e5dfba53d151`
and **the same** genuine flattened simulator-physical-state hash
`5231d31a4e726cf9575f3a21c0a0d92ee00d179bc15f7f306cc4646d557a1887`.

For both: source **success at step 19**, compiled **success at step 25**,
raw-copy **failed within 50 steps**. Initial paired source/target
policy observations also matched exactly.

**Conclusion:** in THIS same-job test the execution order did not change
the initial state or success outcome. This rejects the specific hypothesis
that just running the 13 earlier task seeds necessarily changes the
sampled state for seed 10014 in the tested environment.

It does NOT explain the conflicting original 32-seed run, which observed
source success at step 31 and compiled failure for nominal seed 10014.
That run did not save an original source full-state hash, so physical
initial-condition identity cannot be independently verified retroactively.

The resulting caveat is precise: our public task seed is a declaration
of a pseudorandom-initialization intent, not a **cryptographic witness
of complete simulator initial state** across unpinned jobs. Future
provenance must log the actual physics-state and observation hash and
environment dependency snapshot. Repeated same-seed runs in one job
are not independent initial-condition trials. No source result has been
selectively replaced or dropped from the original 31/32 report.
