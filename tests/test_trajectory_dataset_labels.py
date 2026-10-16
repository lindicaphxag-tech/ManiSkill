import json

import h5py
import numpy as np

from mani_skill.trajectory.dataset import ManiSkillTrajectoryDataset


def _write_fixture(path):
    with h5py.File(path, "w") as file:
        trajectory = file.create_group("traj_0")
        trajectory["obs"] = np.zeros((4, 2))
        trajectory["actions"] = np.zeros((3, 1))
        trajectory["terminated"] = np.array([False, False, False])
        trajectory["truncated"] = np.array([False, False, True])
        trajectory["success"] = np.array([False, True, True])
        trajectory["fail"] = np.array([False, False, False])

    path.with_suffix(".json").write_text(
        json.dumps(
            {
                "env_info": {"env_id": "PickCube-v1", "env_kwargs": {}},
                "episodes": [{"episode_id": 0, "success": True}],
            }
        )
    )


def test_trajectory_dataset_preserves_recorded_success_and_fail_on_device(tmp_path):
    path = tmp_path / "trajectory.h5"
    _write_fixture(path)

    dataset = ManiSkillTrajectoryDataset(str(path), device="cpu")
    try:
        np.testing.assert_array_equal(dataset.success.numpy(), [False, True, True])
        np.testing.assert_array_equal(dataset.fail.numpy(), [False, False, False])
    finally:
        dataset.data.close()
