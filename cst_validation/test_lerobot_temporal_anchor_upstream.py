from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Sequence

import pytest
import torch


UPSTREAMS = (
    ("main", Path("../lerobot-main")),
    ("pr4779", Path("../lerobot-pr4779")),
)


def _load_function(path: Path, function_name: str):
    """Execute one real upstream function without importing the whole package."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    module = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(module)
    scope = {"torch": torch, "Tensor": torch.Tensor, "Sequence": Sequence}
    exec(compile(module, str(path), "exec"), scope)
    return scope[function_name]


def _pi05_state_delta_indices(config_path: Path) -> list[int]:
    """Execute the real PI05Config property body on a minimal semantic fixture."""
    source = config_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    cls = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "PI05Config"
    )
    prop = next(
        node for node in cls.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "state_observation_delta_indices"
    )
    prop.decorator_list = []
    # Keep the exact upstream body, but make it a standalone function.
    module = ast.Module(body=[prop], type_ignores=[])
    ast.fix_missing_locations(module)
    scope = {}
    exec(compile(module, str(config_path), "exec"), scope)
    dummy = SimpleNamespace(
        use_proprioceptive_memory=True,
        memory_frames=6,
        memory_stride=30,
    )
    return list(scope["state_observation_delta_indices"](dummy))


@pytest.mark.parametrize("label,root", UPSTREAMS)
def test_real_upstream_relative_action_anchor_disagrees_with_pi05_memory_semantics(label, root):
    rel_path = root / "src/lerobot/processor/relative_action_processor.py"
    cfg_path = root / "src/lerobot/policies/pi05/configuration_pi05.py"
    proc_path = root / "src/lerobot/policies/pi05/processor_pi05.py"

    deltas = _pi05_state_delta_indices(cfg_path)
    assert deltas == [-150, -120, -90, -60, -30, 0]
    current_index = deltas.index(0)
    assert current_index == len(deltas) - 1

    proc_source = proc_path.read_text(encoding="utf-8")
    assert "RelativeActionsProcessorStep(" in proc_source
    assert "enabled=config.use_relative_actions" in proc_source

    # PI0.5 itself treats the last proprioceptive-memory slot as the current
    # state when it needs a current state for prompt construction.
    assert "prompt_state = state[:, -1] if state.ndim == 3 else state" in proc_source

    to_relative_actions = _load_function(rel_path, "to_relative_actions")

    # Give every history slot a distinct physical value.  Delta 0 / current is
    # the last slot (50); the oldest slot is 0.
    state = torch.tensor(
        [[[0.0], [10.0], [20.0], [30.0], [40.0], [50.0]]],
        dtype=torch.float64,
    )
    actions = torch.tensor([[[52.0], [55.0]]], dtype=torch.float64)
    actual = to_relative_actions(actions, state, [True])

    semantic_current = state[:, current_index]
    expected = actions - semantic_current[:, None, :]
    oldest_slot_result = actions - state[:, :1, :]

    # This is the pinned upstream witness: the shared processor currently
    # follows the oldest array slot, not the semantic delta-0/current slot.
    torch.testing.assert_close(actual, oldest_slot_result)
    assert not torch.allclose(actual, expected)


@pytest.mark.parametrize("label,root", UPSTREAMS)
def test_roundtrip_is_not_a_valid_oracle_for_temporal_anchor_semantics(label, root):
    rel_path = root / "src/lerobot/processor/relative_action_processor.py"
    to_relative_actions = _load_function(rel_path, "to_relative_actions")
    to_absolute_actions = _load_function(rel_path, "to_absolute_actions")

    state = torch.tensor(
        [[[0.0], [10.0], [20.0], [30.0], [40.0], [50.0]]],
        dtype=torch.float64,
    )
    actions = torch.tensor([[[52.0], [55.0]]], dtype=torch.float64)

    # The same wrong slot can be subtracted and added back perfectly.
    relative = to_relative_actions(actions, state, [True])
    recovered = to_absolute_actions(relative, state, [True])
    torch.testing.assert_close(recovered, actions)

    # Yet the semantic relative command against PI0.5's delta-0 state differs.
    expected = actions - state[:, -1:, :]
    assert not torch.allclose(relative, expected)
