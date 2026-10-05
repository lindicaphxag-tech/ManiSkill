from __future__ import annotations

import argparse
import json
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def summarize(values):
    if not values:
        return None
    return {
        "latest_step": int(values[-1].step),
        "latest": float(values[-1].value),
        "best": float(max(v.value for v in values)),
        "series": [
            {
                "step": int(v.step),
                "value": float(v.value),
                "wall_time": float(v.wall_time),
            }
            for v in values
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    event_files = sorted(args.run_dir.rglob("events.out.tfevents.*"))
    if not event_files:
        raise SystemExit(f"no TensorBoard event file under {args.run_dir}")

    acc = EventAccumulator(str(args.run_dir))
    acc.Reload()
    tags = set(acc.Tags().get("scalars", []))
    wanted = [
        "eval/success_once",
        "eval/success_at_end",
        "losses/total_loss",
        "charts/learning_rate",
    ]
    report = {
        "schema_version": 1,
        "run_dir": str(args.run_dir),
        "event_files": [str(x) for x in event_files],
        "available_scalar_tags": sorted(tags),
        "metrics": {},
    }
    for tag in wanted:
        report["metrics"][tag] = (
            summarize(acc.Scalars(tag)) if tag in tags else None
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
