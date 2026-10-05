from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import h5py
import numpy as np


URL = (
    "https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/"
    "resolve/main/demos/PickCube-v1/motionplanning/trajectory.h5"
)
OUT = Path("/tmp/maniskill_pickcube_motionplanning_trajectory.h5")


def describe_group(group, prefix="", depth=0, max_depth=4):
    if depth > max_depth:
        return
    for key in group.keys():
        obj = group[key]
        name = f"{prefix}/{key}" if prefix else key
        if isinstance(obj, h5py.Dataset):
            print(
                json.dumps(
                    {
                        "path": name,
                        "kind": "dataset",
                        "shape": list(obj.shape),
                        "dtype": str(obj.dtype),
                    },
                    sort_keys=True,
                )
            )
        elif isinstance(obj, h5py.Group):
            print(
                json.dumps(
                    {
                        "path": name,
                        "kind": "group",
                        "keys": list(obj.keys())[:20],
                    },
                    sort_keys=True,
                )
            )
            describe_group(obj, name, depth + 1, max_depth)


print(f"DOWNLOADING={URL}")
urllib.request.urlretrieve(URL, OUT)
print(f"BYTES={OUT.stat().st_size}")

with h5py.File(OUT, "r") as f:
    print("ROOT_KEYS=" + json.dumps(list(f.keys())))
    describe_group(f, max_depth=4)

    data = f.get("data")
    if data is not None:
        demos = sorted(data.keys())
        print(f"NUM_DEMOS={len(demos)}")
        if demos:
            demo = data[demos[0]]
            print(f"FIRST_DEMO={demos[0]}")
            print("FIRST_DEMO_ATTRS=" + json.dumps({k: str(v) for k, v in demo.attrs.items()}, sort_keys=True))
            if "actions" in demo:
                arr = np.asarray(demo["actions"])
                print(f"ACTIONS_SHAPE={arr.shape}")
                print("ACTION_FIRST=" + np.array2string(arr[0], precision=8, separator=","))
