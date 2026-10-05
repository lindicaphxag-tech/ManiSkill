# CST Public Validation Mirror

This branch is a **public, frozen validation surface** for the dependency-minimal
Controller-Semantic Transport (CST) core. It is intentionally separate from any
ManiSkill upstream patch.

## Question under test

A native robot-controller action does not by itself define a controller-
independent command. CST decodes a source action into a physical semantic goal,
checks whether the target controller can represent that goal, and either
constructs the target-native action or refuses.

This public mirror adds one further question:

> If the target cannot represent the semantic displacement in one control
> interval, what is the minimum command-level horizon under its declared
> per-step reachable set?

For a bounded incremental joint-position chart with physical per-step box B and
required semantic displacement d, one-step exact conversion requires d in B.
For a state-independent box that contains zero, the minimum E1 semantic horizon
is the smallest H such that d lies in the H-fold Minkowski sum of B.

## Important boundary

This is **E1 semantic-command evidence only**.

- delta_target: the internal target reference can be propagated at the command
  level, so the minimum-length E1 sequence is constructive.
- delta_current: every later action is defined relative to the realized
  measured joint state. Multi-step exactness therefore requires intermediate
  state feedback or a target transition model.
- No E2 controller-reference, E3 realized-trajectory, or E4 task-success claim
  follows from these tests.

## Reproduce

    python -m pip install "numpy>=1.24" "pytest>=8"
    PYTHONPATH=cst_validation pytest -q cst_validation/tests/test_core.py cst_validation/tests/test_reachability.py

The GitHub Actions workflow on this branch executes exactly this minimal gate.

## Why this branch exists

The research source currently lives outside this public fork. This mirror makes
the precise implementation and tests independently inspectable while keeping
research code out of the upstream ManiSkill bug-fix diff.
