from __future__ import annotations

import hashlib
import urllib.request

import numpy as np

from cst.core import JointControllerContext, JointGoalChart


LEROBOT_COMMIT = "8c920c4270460851cedd2737657584586d3dc66f"
LEROBOT_BLOB_SHA1 = "3405402904cf15ca18227b3a3fe006d7936f9d53"
URL = (
    "https://raw.githubusercontent.com/huggingface/lerobot/"
    + LEROBOT_COMMIT
    + "/src/lerobot/processor/relative_action_processor.py"
)


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()


def assert_pinned_lerobot_contract(source: str) -> None:
    required = (
        'actions[..., :dims] -= state_offset',
        'actions[..., :dims] += state_offset',
        'if actions.ndim == 3:',
        'state_offset = state_offset.unsqueeze(-2)',
        'if state.ndim == 3:',
        'state = state[:, 0]',
        'if state is not None and not self._chunk_in_flight():',
        'self._last_state = state',
    )
    missing = [snippet for snippet in required if snippet not in source]
    if missing:
        raise RuntimeError(
            "pinned LeRobot source no longer matches the audited relative-action "
            f"contract; missing snippets: {missing}"
        )


def lerobot_relative_numpy(
    absolute: np.ndarray,
    state: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    """Numerical oracle for the pinned LeRobot source contract."""
    out = np.asarray(absolute, dtype=float).copy()
    state = np.asarray(state, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    offset = state[: len(mask)] * mask
    out[..., : len(mask)] -= offset
    return out


def lerobot_absolute_numpy(
    relative: np.ndarray,
    state: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    out = np.asarray(relative, dtype=float).copy()
    state = np.asarray(state, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    offset = state[: len(mask)] * mask
    out[..., : len(mask)] += offset
    return out


def cst_decode_chunk(
    relative: np.ndarray,
    latch: np.ndarray,
    mask: np.ndarray,
) -> np.ndarray:
    relative = np.asarray(relative, dtype=float)
    latch = np.asarray(latch, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    result = relative.copy()
    dims = len(mask)

    # LeRobot excluded dimensions remain absolute, so only masked coordinates
    # are represented by the relative_latched chart.
    chart = JointGoalChart("relative_latched", normalized=False)
    for t in range(len(relative)):
        masked_goal = chart.decode(
            relative[t, :dims][mask],
            JointControllerContext(q_latched=latch[:dims][mask]),
        )
        result[t, :dims][mask] = masked_goal
    return result


def main() -> None:
    payload = urllib.request.urlopen(URL).read()
    observed_blob = git_blob_sha1(payload)
    if observed_blob != LEROBOT_BLOB_SHA1:
        raise RuntimeError(
            f"LeRobot source identity drift: {observed_blob} != {LEROBOT_BLOB_SHA1}"
        )
    source = payload.decode("utf-8")
    assert_pinned_lerobot_contract(source)

    rng = np.random.default_rng(20261006)
    cases = 0
    max_roundtrip = 0.0
    max_cst_residual = 0.0
    semantic_separation_witnesses = 0

    for horizon in (1, 2, 8, 50):
        for action_dim in (3, 7, 8):
            for _ in range(40):
                absolute = rng.normal(size=(horizon, action_dim))
                latch = rng.normal(size=action_dim)
                mask = rng.random(action_dim) > 0.25
                if not np.any(mask):
                    mask[0] = True

                relative = lerobot_relative_numpy(absolute, latch, mask)
                recovered = lerobot_absolute_numpy(relative, latch, mask)
                max_roundtrip = max(
                    max_roundtrip,
                    float(np.max(np.abs(recovered - absolute))),
                )

                cst = cst_decode_chunk(relative, latch, mask)
                max_cst_residual = max(
                    max_cst_residual,
                    float(np.max(np.abs(cst - absolute))),
                )

                # Counterexample against "relative means per-step current delta":
                # change measured state after prediction while keeping the chunk
                # latch fixed. LeRobot must keep the old latch until the action
                # queue drains.
                changed_current = latch + rng.normal(scale=0.2, size=action_dim)
                first_masked = np.flatnonzero(mask)[0]
                current_chart = JointGoalChart("delta_current", normalized=False)
                current_goal = current_chart.decode(
                    np.array([relative[0, first_masked]]),
                    JointControllerContext(
                        q_current=np.array([changed_current[first_masked]])
                    ),
                )[0]
                latched_goal = absolute[0, first_masked]
                if not np.isclose(current_goal, latched_goal):
                    semantic_separation_witnesses += 1

                cases += 1

    result = {
        "lerobot_commit": LEROBOT_COMMIT,
        "lerobot_blob_sha1": observed_blob,
        "cases": cases,
        "max_lerobot_roundtrip_residual": max_roundtrip,
        "max_cst_relative_latched_residual": max_cst_residual,
        "delta_current_separation_witnesses": semantic_separation_witnesses,
    }
    print("CST_LEROBOT_RELATIVE_CONTRACT_V0")
    print(result)

    assert max_roundtrip <= 1e-12
    assert max_cst_residual <= 1e-12
    assert semantic_separation_witnesses > 0


if __name__ == "__main__":
    main()
