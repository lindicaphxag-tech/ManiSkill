# robomimic #270 — Minimal Upstream Integration Plan

The candidate implementation is staged in:

`cst_research/upstream_candidates/robomimic/robosuite_add_delta_actions.py`

It is designed to mirror the existing
`robomimic/scripts/conversion/robosuite_add_absolute_actions.py`.

## 1. convert_robosuite.py

Add:

```python
from robomimic.scripts.conversion.robosuite_add_delta_actions import (
    add_delta_actions_to_dataset,
)
```

Add CLI:

```python
parser.add_argument(
    "--add_delta_actions",
    action="store_true",
    help="Set this flag to add delta actions to an absolute-action dataset",
)
```

Reject ambiguous simultaneous conversion:

```python
if args.add_absolute_actions and args.add_delta_actions:
    parser.error("--add_absolute_actions and --add_delta_actions are mutually exclusive")
```

Run:

```python
if args.add_delta_actions:
    add_delta_actions_to_dataset(
        dataset=args.dataset,
        num_workers=args.num_workers,
    )
```

## 2. extract_action_dict.py

The current function always assumes `actions` is relative.  That is correct
for the old workflow but wrong for an absolute-input dataset.

Generalize the signature without breaking old callers:

```python
def extract_action_dict(
    dataset,
    add_absolute_actions=True,
    add_delta_actions=False,
    actions_are_absolute=False,
):
    SPECS = [
        dict(
            key="actions",
            is_absolute=actions_are_absolute,
        )
    ]
    if add_absolute_actions:
        SPECS.append(dict(key="actions_abs", is_absolute=True))
    if add_delta_actions:
        SPECS.append(dict(key="actions_delta", is_absolute=False))
```

Then in `convert_robosuite.py` call:

```python
extract_action_dict(
    dataset=args.dataset,
    add_absolute_actions=args.add_absolute_actions,
    add_delta_actions=args.add_delta_actions,
    actions_are_absolute=args.add_delta_actions,
)
```

This preserves the old behavior exactly when `--add_delta_actions` is absent.

## 3. Scope guard

The candidate deliberately supports the same effective action semantics as the
existing delta→absolute path:

- OSC pose action: first six values are position + axis-angle;
- fixed impedance;
- remainder (gripper / mobile-base mode) preserved unchanged;
- one or two robots;
- robosuite <=1.4.1 and >=1.5 controller layouts.

Variable-impedance actions are rejected rather than silently misparsed.

## 4. Exactness / saturation

The inverse of `Controller.scale_action` is used.  If an absolute goal asks
for a physical delta outside `output_min/output_max`, no single native delta
action can exactly realize that goal.  The converter clips only to produce a
valid dataset action **and reports the count and maximum physical excess**.

This distinction is important for both upstream correctness and CST:

`representable -> exact semantic transport`

`out of range -> saturated / non-exact transport`

## 5. Required upstream validation before opening PR

1. Unit tests for scaling inverse and orientation convention (already green in
   the public CST branch).
2. One robomimic dataset generated with delta OSC:
   `actions -> actions_abs -> recovered actions_delta`.
3. Report:
   - max / p95 action error for non-saturated steps;
   - saturation count;
   - source vs round-trip replay success;
   - end-effector trajectory deviation.
4. Test both the currently supported robosuite branch and a legacy <=1.4.1
   fixture or controller stub.

Issue #270 already has an explicit maintainer statement: "Happy to accept a PR
for this functionality."
