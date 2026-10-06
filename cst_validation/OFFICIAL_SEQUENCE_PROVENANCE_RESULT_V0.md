# Official ManiSkill sequence-provenance CST result v0

Status: **frozen public-data evidence; E1 sequence semantics only**.

Workflow run: 37393395020
Frozen validation commit: d3f9265fb8e7e05d9c13cc38cad907beca9d6542
Artifact: cst-official-sequence-provenance-v0, id 11382063085
Artifact digest: sha256:9625e36c746dfe2dca0a3ca2c97dfed44aa43ba0833ebd69a8436e8cfd6acc07

## Data

Four official ManiSkill motion-planning datasets were audited: PickCube-v1, StackCube-v1, PegInsertionSide-v1, and PlugCharger-v1. Total: 4,000 trajectories and 519,006 actions.

## Frozen result

### delta-current

- action-only decoding correctly refused: **4000 / 4000 trajectories**;
- after providing the required measured q_current trace: **3751 / 4000 trajectories** are losslessly reconstructible under the one-step chart;
- maximum semantic-goal residual over the full audit: **0.018655491620302195 rad**.

The 249 non-perfect trajectories are not an identifiability failure after q_current is supplied. They contain the same one-step target-image violations identified by the separately frozen reachability audit: 1,199 actions exceed the +/-0.1 rad delta-current one-step chart, and all have H_min=2.

### delta-target

- decoding without initial q_target correctly refused: **4000 / 4000 trajectories**;
- with exactly one initial q_target and the native action sequence: **4000 / 4000 trajectories** reconstruct the complete semantic-goal trace exactly;
- maximum semantic-goal residual: **0.0**;
- maximum recursively reconstructed q_target-reference residual: **0.0**.

No measured q_current trace is used for the delta-target reconstruction after initialization.

## Main interpretation

The result separates two logically different causes of failed action conversion:

1. **Identifiability failure** — the recorded action plus available controller state does not uniquely define the physical command semantics.
2. **Representability failure** — the physical semantic goal is identifiable but lies outside the target controller's current action image.

For delta-current, per-step q_current resolves the first problem but does not resolve the second. For delta-target, one initial q_target resolves the reference-state ambiguity and, on these four frozen public datasets, every action is also one-step representable.

This is stronger than saying one action representation has a higher empirical success rate: CST predicts *why* a conversion can or cannot be exact before task rollout.

## Claim boundary

This is E1 sequence-semantic evidence. It does not establish realized simulator-state equivalence, controller dynamics equivalence, task success, safety, or external adoption.
