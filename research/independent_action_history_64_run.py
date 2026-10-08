"""Predeclared independent observer evaluation using frozen original method."""
import json
import os
from pathlib import Path
import frozen_ppo_action_history_observer as experiment

starts = {"pull_cube": 83001, "stack_cube": 93001}
task = os.environ["ABI_TASK"]
chunk = int(os.environ["ABI_CHUNK"])
if task not in starts or chunk not in range(4):
    raise ValueError("Unexpected task or seed partition")
first = starts[task] + 8 * chunk
experiment.FIRST_SEED = first
experiment.SEEDS = tuple(range(first, first + 8))
experiment.CHUNK = str(chunk)
experiment.OUTPUT_NAME = f"independent_observer_{task}_{chunk}.json"
experiment.main()
record = json.loads(Path(experiment.OUTPUT_NAME).read_text())
if record["seed_list"] != list(experiment.SEEDS):
    raise RuntimeError("Frozen seed mismatch")
print("INDEPENDENT_OBSERVER_SEEDS", task, chunk, record["success_count"])
