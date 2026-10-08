# Episode 8 First-Divergence Result V1

Public workflow: `37405141224`  
Episode: `PegInsertionSide-v1 / episode 8`

## Why this assay exists

The clean controller-contract adapter was semantically better than current main but still lost one execution episode:

- current main: 9/10;
- adapter: 8/10;
- adapter + controller fix: 8/10.

The regression was isolated to episode 8.

Rather than comparing only final success, this assay traces every converter invocation during episode 8 and records:

- requested delta pose;
- normalized action;
- controller-scaled physical action;
- clipping condition;
- EE pose before conversion;
- controller target pose when available;
- converter→controller SO(3) semantic error.

## Main vs revised adapter

Both traces contain **155 conversion calls**.

Clipping schedule is identical:

`[12, 18, 23, 29, 83, 89, 95]`

Observed first divergences:

| Quantity | First divergent call |
| --- | ---: |
| physical scaled action | **0** |
| controller state | **1** |
| requested delta pose | **2** |

Maximum differences over the aligned trace:

- physical scaled action L2: **0.000801541**
- requested position delta: **2.1533e-05 m**
- requested rotation delta: **0.0276343°**

Mean local SO(3) semantic error:

- current main: **0.0219896°**
- revised adapter: **0.0155809°**

Thus the execution failure is not explained by the revised adapter being less locally faithful. The adapter is locally **more** faithful under the converter→controller SO(3) metric.

## Adapter vs adapter + controller fix

The two repaired-controller variants are observationally identical in this trace:

- call count: 155 vs 155;
- clipping schedule: identical;
- first physical-action divergence: none;
- first controller-state divergence: none;
- first request divergence: none;
- maximum physical scaled action L2 difference: 0.

This confirms that the clean adapter successfully removes the historical controller-sign migration dependency for this episode.

## Interpretation

The data support the following narrower mechanism:

[
	ext{tiny action-level semantic correction}
ightarrow
	ext{immediate state perturbation}
ightarrow
	ext{closed-loop request divergence}
ightarrow
	ext{different terminal task outcome}
]

with no change in clipping schedule.

The result is consistent with episode 8 lying near a narrow execution basin / task-margin boundary.

It does **not yet prove** that the first small physical-action difference is causally sufficient for final failure.

## What this rules out

For episode 8, the evidence rules against these as the primary differentiators:

- controller sign convention after the contract adapter;
- clipping schedule;
- residual retry count induced by clipping;
- gross local semantic error.

## Next causal test

Interpolate continuously between current-main and semantically corrected physical rotation commands while holding the same task/seed fixed.

If task success changes over a narrow interval of interpolation coefficient (alpha), this provides a direct repair-path margin witness:

[
a_alpha=(1-alpha)a_{main}+alpha a_{repair}.
]

The transition point should be frozen before any policy-level claim.

## Claim boundary

This result establishes a first-divergence trace and narrows plausible mechanisms.

It does not by itself establish a general dynamical-systems law, safety margin, or policy-performance effect.
