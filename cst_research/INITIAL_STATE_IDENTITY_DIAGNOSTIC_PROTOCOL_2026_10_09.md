# Reconstructing the seed-10014 state identity discrepancy

Exploratory protocol, written before a new order-effect diagnostic run;
not a holdout or a new research claim.

Run the exact frozen official PPO and validated adapter under two fixed
execution schedules in a *single* GitHub Actions job:

A. Isolated evaluation: `10014`.
B. Sequential evaluation: `10001,10002,...,10014`, extract only the
   `10014` outcome for A/B comparison.

Use source / compiled / raw-copy controller triples, as in the original
32-seed holdout, unchanged. At initial reset before the first action,
record SHA256 of source 42D flattened policy observations AND
`env.unwrapped.get_state()` from the genuine simulator, along with
the first few observation floats and all three initial-observation
mismatches. Only compute hashes; do not replay or forcibly restore
state in the experiment.

Record full success/step results, never reset after observing a
result, and do not claim exact same-scenario replication unless both
actual physics state hashes match. Cross-job dependency fingerprints
must be separately checked.

Testable question: does a seed's realized environment state or policy
outcome depend on how many other task environments were built/reset
earlier in the same process?

The original 32-seed result remains as observed. This diagnostic does
not replace any held-out row.
