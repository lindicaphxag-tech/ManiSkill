# LeRobot Cross-Stack Compensation Witness V1

Public workflow: `37406064561`

Pinned upstream:

- repository: `huggingface/lerobot`
- commit: `8c920c4270460851cedd2737657584586d3dc66f`
- source: `src/lerobot/processor/relative_action_processor.py`
- source SHA-256: `1c99f2a66649579cf6536d1970f71172b0b50bcb8decd226a9aa8969c0b0f171`

Related upstream issue: `huggingface/lerobot#3863`  
Related community fix PR: `huggingface/lerobot#4111`

## Attribution boundary

The underlying state/action mapping defect was reported and worked on by the LeRobot community. This artifact does **not** claim discovery or ownership of that upstream bug or its proposed fix.

The contribution of this SemRepair case study is narrower:

> bind an executable witness to the pinned upstream source and show that symmetric use of the same wrong semantic mapping makes an exact roundtrip test pass while the one-way training target remains semantically wrong.

## Pinned source contract

The witness AST-inspects the exact pinned helper bodies and confirms that both:

- `to_relative_actions`;
- `to_absolute_actions`

derive their reference from the same positional prefix contract:

```
state[..., :dims]
```

Thus the forward and inverse transforms share the same latent anchor assumption.

## Concrete non-prefix layout

State:

```
[j0_pos, j0_vel, j1_pos, j1_vel, ..., j5_pos, j5_vel, gripper]
```

Action:

```
[j0_pos, j1_pos, j2_pos, j3_pos, j4_pos, j5_pos, gripper]
```

Correct state indices:

```
[0, 2, 4, 6, 8, 10, 12]
```

For the frozen witness:

Correct relative target:

```
[1, 2, 3, 4, 5, 6, 7]
```

Current positional-prefix target:

```
[1, 21.9, 13, 43.8, 25, 65.7, 7]
```

Yet the current forward result passed through the current inverse recovers the original action exactly.

## Quantitative result

| Metric | Result |
| --- | ---: |
| one-way forward semantic L∞ error | **59.7** |
| one-way forward semantic L2 error | **77.7440673** |
| forward→inverse roundtrip L∞ error | **0.0** |
| deterministic sweep cases | **32** |
| maximum roundtrip L∞ error over sweep | **0.0** |
| minimum forward semantic L∞ error over sweep | **65.97** |

Certificate:

- source bound to same prefix contract: **true**
- self-consistency passes: **true**
- forward semantics fail: **true**
- all 32 sweep roundtrips pass: **true**
- all 32 sweep forward semantics fail: **true**
- compensating inverse hides forward defect: **true**

## Identifiability interpretation

For a latent anchor (b),

[
F_b(a)=a-b,qquad G_b(r)=r+b.
]

Then

[
G_b(F_b(a))=a
]

for any (b).

Therefore a roundtrip observation alone cannot identify whether (b) is the physically correct state/action correspondence.

This algebra is not claimed as a new theorem. The research implication for SemRepair is operational:

> a repair or semantic mapping must not receive authority from self-consistency evidence when the evidence is invariant under a latent semantic degree of freedom.

It requires an **external semantic anchor** such as:

- named state/action correspondence;
- explicit index map;
- independently specified physical quantity;
- repository-native semantic oracle.

## Cross-stack relation to ManiSkill

The two cases expose different forms of compensation:

### ManiSkill

Two distinct semantic defects partially compensate across a converter/controller boundary.

A singleton repair can worsen behavior.

### LeRobot

Forward and inverse transforms share the same wrong latent mapping.

The pair cancels exactly, allowing a perfect self-consistency test despite a wrong one-way semantic target.

The common structure is:

[
	ext{internally consistent evidence}

otRightarrow
	ext{externally identified semantics}.
]

## Claim boundary

Established:

- exact pinned-source contract;
- executable non-prefix counterexample;
- exact roundtrip cancellation;
- 32-case deterministic sweep;
- external community corroboration that the underlying mapping issue is real.

Not established:

- SemRepair adoption by LeRobot;
- SemRepair authorship of #3863/#4111;
- policy-performance impact measured by this witness;
- universal failure of roundtrip testing.

The broader oracle / metamorphic-testing problem is established prior art.
