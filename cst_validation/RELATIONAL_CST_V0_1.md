# Relational CST — sequence-level controller transducer morphisms

Status: **method core, controlled affine evidence**.

One-step controller equivalence is insufficient for stateful interfaces.  A
converter can match the current command while causing controller-owned memory
to drift, so the next command is no longer equivalent.

Relational CST models source and target controllers as affine command
transducers and compiles two maps simultaneously:

    u_B = P u_A + Q c + K z_A + q
    z_B = R z_A + r

where `c` is shared measured context and `z_A,z_B` are controller-owned
memories.

The compiler verifies coefficient identities for:

- the full low-level drive-target trace;
- the endpoint canonical goal;
- closure of the hidden-state relation under each controller's update.

If the relation is true at the initial step, hidden-update closure preserves it
after one step.  By induction the same compiled action interface therefore
preserves command-trace semantics for arbitrary sequence length, subject to the
declared affine region and target native bounds.

## Novelty boundary

Simulation/bisimulation relations, feedback refinement relations, state-space
homomorphisms, affine systems, and linear constraint solving are established
control/formal-methods concepts. Relational CST does not claim those ideas.

The narrow research contribution candidate is an executable compiler for the
*software action interfaces used by robot-learning stacks*: normalization,
current-relative versus target-relative semantics, interpolation traces,
controller memory, saturation regions, and cross-stack host parity are lowered
into a relation that emits the actual runtime action adapter or refuses it.

This remains controller-command semantics. It does not imply plant/contact
trajectory equivalence or task safety.

## Promotion gate

Before a strong paper claim, the sequence certificate must:
1. match at least two production controller implementations;
2. predict a real multi-step conversion failure that endpoint-only conversion
   misses;
3. survive a public task-level replay;
4. be independently reviewed or retained upstream.
