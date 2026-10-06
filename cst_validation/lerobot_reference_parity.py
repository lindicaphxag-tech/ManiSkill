from __future__ import annotations

import ast
import importlib.util
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import torch


LEROBOT_COMMIT = "d40e8709cffb93644db66e30604ef50fdec003cb"


def load_lerobot_reference_functions(source_path: Path):
    """Execute the exact two public LeRobot conversion functions from pinned source.

    We intentionally extract only the two pure tensor functions so this parity
    assay tests their real implementation without pulling unrelated robot,
    dataset, camera, or policy dependencies into the evidence boundary.
    """
    source = source_path.read_text()
    tree = ast.parse(source, filename=str(source_path))
    wanted = {"to_relative_actions", "to_absolute_actions"}
    nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in wanted
    ]
    found = {node.name for node in nodes}
    if found != wanted:
        raise RuntimeError(f"missing pinned LeRobot functions: {wanted - found}")

    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "torch": torch,
        "Tensor": torch.Tensor,
        "Sequence": Sequence,
    }
    exec(compile(module, str(source_path), "exec"), namespace)
    return namespace["to_relative_actions"], namespace["to_absolute_actions"]


def load_cst_reference_module(cst_path: Path):
    spec = importlib.util.spec_from_file_location("cst_reference_semantics", cst_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main():
    root = Path(__file__).resolve().parents[1]
    lerobot_source = root / "lerobot-src" / "src/lerobot/processor/relative_action_processor.py"
    cst_source = root / "cst-src" / "cst_research/reference_semantics.py"

    to_relative, to_absolute = load_lerobot_reference_functions(lerobot_source)
    cst = load_cst_reference_module(cst_source)

    rng = np.random.default_rng(20261006)
    random_chunks = 500
    batch = 4
    horizon = 9
    dim = 7

    max_relative_error = 0.0
    max_absolute_error = 0.0
    checked_trajectories = 0
    checked_action_vectors = 0

    for _ in range(random_chunks):
        state = rng.normal(size=(batch, dim)).astype(np.float32)
        absolute = rng.normal(size=(batch, horizon, dim)).astype(np.float32)
        mask = rng.random(dim) > 0.25

        rel_lr = to_relative(
            torch.from_numpy(absolute),
            torch.from_numpy(state),
            mask.tolist(),
        ).cpu().numpy()

        abs_lr = to_absolute(
            torch.from_numpy(rel_lr),
            torch.from_numpy(state),
            mask.tolist(),
        ).cpu().numpy()

        # CST CHUNK_ANCHOR means exactly one frozen state anchor per chunk.
        for b in range(batch):
            semantics = cst.ReferenceSemantics(
                kind=cst.ReferenceKind.CHUNK_ANCHOR,
                relative_mask=mask,
            )
            current_states = np.repeat(state[b][None, :], horizon, axis=0)
            cst_transport = cst.transport_reference_semantics(
                rel_lr[b],
                semantics,
                cst.ReferenceSemantics(
                    kind=cst.ReferenceKind.ABSOLUTE,
                    relative_mask=mask,
                ),
                current_states=current_states,
                source_chunk_anchor=state[b],
            )
            max_relative_error = max(
                max_relative_error,
                float(np.max(np.abs(cst_transport.source_goals - abs_lr[b]))),
            )
            max_absolute_error = max(
                max_absolute_error,
                float(np.max(np.abs(cst_transport.target_actions - abs_lr[b]))),
            )
            checked_trajectories += 1
            checked_action_vectors += horizon

    # LeRobot explicitly collapses temporally stacked state to state[:, 0].
    stacked_state = rng.normal(size=(3, 5, dim)).astype(np.float32)
    stacked_actions = rng.normal(size=(3, horizon, dim)).astype(np.float32)
    mask = [True, True, True, True, True, True, False]
    rel_stacked = to_relative(
        torch.from_numpy(stacked_actions),
        torch.from_numpy(stacked_state),
        mask,
    )
    rel_current = to_relative(
        torch.from_numpy(stacked_actions),
        torch.from_numpy(stacked_state[:, 0]),
        mask,
    )
    temporal_stack_error = float(
        torch.max(torch.abs(rel_stacked - rel_current)).item()
    )

    # A sharp non-equivalence witness: the same numeric actions are not
    # interchangeable between LeRobot chunk-anchor semantics and sequential
    # previous-command deltas.
    numeric = np.array([[1.0], [2.0], [3.0]])
    states = np.repeat(np.array([[10.0]]), 3, axis=0)
    chunk = cst.decode_reference_trace(
        numeric,
        cst.ReferenceSemantics(
            kind=cst.ReferenceKind.CHUNK_ANCHOR,
            relative_mask=np.array([True]),
        ),
        current_states=states,
        chunk_anchor=np.array([10.0]),
    )
    sequential = cst.decode_reference_trace(
        numeric,
        cst.ReferenceSemantics(
            kind=cst.ReferenceKind.PREVIOUS_COMMAND,
            relative_mask=np.array([True]),
        ),
        current_states=states,
        chunk_anchor=np.array([10.0]),
    )
    divergence = float(
        np.max(np.abs(chunk.goals - sequential.goals))
    )

    result = {
        "lerobot_commit": LEROBOT_COMMIT,
        "random_chunks": random_chunks,
        "batch_per_chunk": batch,
        "horizon": horizon,
        "dimension": dim,
        "checked_trajectories": checked_trajectories,
        "checked_action_vectors": checked_action_vectors,
        "max_cst_vs_lerobot_goal_error": max_relative_error,
        "max_cst_vs_lerobot_absolute_error": max_absolute_error,
        "temporal_stack_current_frame_error": temporal_stack_error,
        "chunk_vs_sequential_same_numbers_max_goal_divergence": divergence,
    }

    assert max_relative_error <= 2e-6, result
    assert max_absolute_error <= 2e-6, result
    assert temporal_stack_error == 0.0, result
    assert divergence == 3.0, result

    print("LEROBOT_CST_PARITY_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
