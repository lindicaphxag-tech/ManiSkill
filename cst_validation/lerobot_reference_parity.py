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
    spec = importlib.util.spec_from_file_location("reference_semantics", cst_path)
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
    sys.path.insert(0, str(cst_source.parent))
    from jit_reference_adapter import JustInTimeReferenceAdapter

    rng = np.random.default_rng(20261006)
    random_chunks = 500
    batch = 4
    horizon = 9
    dim = 7

    max_relative_error = 0.0
    max_absolute_error = 0.0
    checked_trajectories = 0
    checked_action_vectors = 0
    jit_max_goal_error = 0.0
    naive_copy_max_goal_error = 0.0
    jit_checked_action_vectors = 0
    jit_trace_errors = []
    naive_trace_errors = []

    for _ in range(random_chunks):
        state = rng.normal(size=(batch, dim)).astype(np.float32)
        mask = rng.random(dim) > 0.25
        offsets = rng.uniform(-0.2, 0.2, size=(batch, horizon, dim)).astype(
            np.float32
        )
        absolute = state[:, None, :] + offsets
        # Dimensions excluded from relative processing remain absolute-valued.
        if np.any(~mask):
            absolute[..., ~mask] = rng.uniform(
                -1.0, 1.0, size=(batch, horizon, int(np.sum(~mask)))
            )

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

            # Cross-reference runtime bridge: execute the real LeRobot
            # CHUNK_ANCHOR source chunk through CST into CURRENT_STATE deltas.
            # The execution state intentionally moves and includes tracking
            # perturbations, so query-time tensor copying is not equivalent.
            target_semantics = cst.ReferenceSemantics(
                kind=cst.ReferenceKind.CURRENT_STATE,
                relative_mask=mask,
            )
            adapter = JustInTimeReferenceAdapter(
                semantics,
                target_semantics,
                source_chunk_anchor=state[b],
            )
            execution_state = state[b].astype(float).copy()
            naive_state = execution_state.copy()
            trace_jit_error = 0.0
            trace_naive_error = 0.0
            for t in range(horizon):
                out = adapter.step(
                    rel_lr[b, t],
                    current_state=execution_state,
                )
                expected = abs_lr[b, t].astype(float)
                step_jit_error = float(
                    np.max(np.abs(out.reconstructed_target_goal - expected))
                )
                jit_max_goal_error = max(jit_max_goal_error, step_jit_error)
                trace_jit_error = max(trace_jit_error, step_jit_error)

                naive_goal = rel_lr[b, t].astype(float).copy()
                naive_goal[mask] = naive_state[mask] + rel_lr[b, t, mask]
                step_naive_error = float(np.max(np.abs(naive_goal - expected)))
                naive_copy_max_goal_error = max(
                    naive_copy_max_goal_error, step_naive_error
                )
                trace_naive_error = max(trace_naive_error, step_naive_error)

                # JIT remains goal-correct under changing measured state.
                execution_state = expected + rng.normal(scale=0.03, size=dim)
                # Naive copied deltas compound under ideal tracking.
                naive_state = naive_goal
                jit_checked_action_vectors += 1

            jit_trace_errors.append(trace_jit_error)
            naive_trace_errors.append(trace_naive_error)
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
        "jit_chunk_anchor_to_current_state_max_goal_error": jit_max_goal_error,
        "naive_copy_chunk_to_current_state_max_goal_error": naive_copy_max_goal_error,
        "jit_checked_action_vectors": jit_checked_action_vectors,
        "jit_trace_error_mean": float(np.mean(jit_trace_errors)),
        "jit_trace_error_p95": float(np.quantile(jit_trace_errors, 0.95)),
        "naive_copy_trace_error_mean": float(np.mean(naive_trace_errors)),
        "naive_copy_trace_error_median": float(np.median(naive_trace_errors)),
        "naive_copy_trace_error_p95": float(
            np.quantile(naive_trace_errors, 0.95)
        ),
    }

    assert max_relative_error <= 2e-6, result
    assert max_absolute_error <= 2e-6, result
    assert temporal_stack_error == 0.0, result
    assert divergence == 3.0, result
    assert jit_max_goal_error <= 2e-6, result
    assert jit_checked_action_vectors == checked_action_vectors, result
    assert naive_copy_max_goal_error > 1e-2, result
    assert result["naive_copy_trace_error_median"] > 1e-2, result

    print("LEROBOT_CST_PARITY_JSON=" + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
