"""Frozen PushT *direct* requested-response probe. Oracle simulation only.

Run with PYTHONPATH pointing at the exact upstream simulator-query source
8207ac01c56e75ccee19cba0e75eb0978cde37b2 and exact LeRobot checkout.
Not a certified controller or a closed-loop task-success study.
"""
import argparse
from hashlib import sha1, sha256
from importlib.metadata import version
import json
from pathlib import Path

import gymnasium as gym
import gym_pusht  # noqa: F401
import numpy as np
from research.eprc.real_policy.cross_policy_prospective_state import (
    DIFFUSION_REV, VQBET_REV, LEROBOT_COMMIT, SUPPORT_SCALE, PolicyProbe,
)
from research.eprc.real_policy.pusht_exact_state import (
    STATE_RESTORE_PROTOCOL, capture_snapshot, restore_snapshot,
)

HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "direct_counterfactual_pilot_v1.json"
FROZEN_GIT_BLOB = "495eb5f65695cb6b4e7cb22e89e2841fd25c7d6f"


def frozen_protocol(path=PROTOCOL):
    raw = Path(path).read_bytes()
    git_blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if git_blob != FROZEN_GIT_BLOB:
        raise ValueError("pre-outcome protocol Git blob changed")
    p = json.loads(raw)
    if (p["schema"] != "crg-direct-counterfactual-policy-response-pilot-v1"
        or p["state_seeds"] != [311, 313, 317, 331, 337]
        or p["hard_controller_action_bounds"] is not None
        or p["policy_rng_seed_split"] != {
            "decision_only": [911, 977, 997],
            "independent_audit_only": [1009, 1013, 1019],
        }
        or p["sources"]["lerobot_sha"] != LEROBOT_COMMIT
        or p["sources"]["diffusion_revision"] != DIFFUSION_REV
        or p["sources"]["vqbet_revision"] != VQBET_REV
        or STATE_RESTORE_PROTOCOL != "reset-fresh-space-block-position-4ulp-v2"):
        raise ValueError("frozen source/state/probe contract mismatch")
    return p, sha256(raw).hexdigest()


def run(reset_seed, destination, protocol_path=PROTOCOL):
    p, digest = frozen_protocol(protocol_path)
    if reset_seed not in p["state_seeds"]:
        raise ValueError("state seed was not preregistered")
    env = gym.make("gym_pusht/PushT-v0", obs_type="pixels_agent_pos",
                   render_mode="rgb_array", observation_width=96,
                   observation_height=96)
    try:
        env.reset(seed=int(reset_seed))
        snap = capture_snapshot(env)
        fixed_agent = np.asarray(snap.agent_position, dtype=np.float64).copy()

        def render(s):
            restore_snapshot(env, s)
            observation = env.unwrapped.get_obs()
            if not np.array_equal(np.asarray(observation["agent_pos"], np.float64), fixed_agent):
                raise RuntimeError("intervention changed fixed agent")
            return observation

        original = render(snap)
        pixels_hash = sha256(np.asarray(original["pixels"]).tobytes()).hexdigest()
        if sha256(np.asarray(render(snap)["pixels"]).tobytes()).hexdigest() != pixels_hash:
            raise RuntimeError("base snapshot rendered differently twice")
        a = PolicyProbe("diffusion", original, render)
        b = PolicyProbe("vqbet", original, render)
        if a.revision != DIFFUSION_REV or b.revision != VQBET_REV:
            raise ValueError("unexpected official policy checkpoint")
        zero = np.zeros(3, dtype=float)
        observations = []
        for request, physical_h in p["physically_requested_block_deltas"].items():
            h = np.asarray(physical_h, dtype=float) / SUPPORT_SCALE
            for split, seed_list in p["policy_rng_seed_split"].items():
                for seed in seed_list:
                    actions = [
                        np.asarray(a.query_delta(snap, h, seed), dtype=float),
                        np.asarray(a.query_delta(snap, zero, seed), dtype=float),
                        np.asarray(b.query_delta(snap, h, seed), dtype=float),
                        np.asarray(b.query_delta(snap, zero, seed), dtype=float),
                    ]
                    if any(x.shape != (2,) or not np.isfinite(x).all() for x in actions):
                        raise ValueError("nonfinite or wrong-shaped action")
                    z = actions[0] - actions[1] - actions[2] + actions[3]
                    observations.append(dict(
                        heldout_id=request, split=split, rng_seed=int(seed),
                        four_raw_first_actions=[x.tolist() for x in actions],
                        paired_full_response_gap_vector=z.tolist(),
                    ))
        counts = {"diffusion": a.query_count, "vqbet": b.query_count}
        if len(observations) != 12 or counts != {"diffusion":24, "vqbet":24}:
            raise ValueError("lost a paired query or changed the precommitted budget")
        result = dict(
            schema="crg-direct-counterfactual-state-v1", reset_seed=int(reset_seed),
            frozen_protocol_sha256=digest, source_sha=p["sources"]["frozen_source_sha"],
            lerobot_sha=LEROBOT_COMMIT, state_restore_protocol=STATE_RESTORE_PROTOCOL,
            actual_gym_pusht_distribution_version=version("gym-pusht"),
            baseline_pixels_sha256=pixels_hash,
            official_checkpoint_revisions={"diffusion":a.revision,"vqbet":b.revision},
            policy_forward_counts=counts, total_policy_forward_counts=48,
            trusted_global_hard_action_bound=False,
            certified_transfer_authorizations=0,
            outcome="DESCRIPTIVE_NO_TRUSTED_BOUND", observations=observations,
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
        print(json.dumps({"seed":reset_seed,"policy_queries":48,
                          "outcome":result["outcome"]},sort_keys=True))
        return 0
    finally:
        env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.reset_seed, args.output))
