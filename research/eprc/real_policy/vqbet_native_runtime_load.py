from __future__ import annotations

import json
from pathlib import Path

import torch

from lerobot.common.policies.vqbet.modeling_vqbet import VQBeTPolicy


MODEL_ID = "lerobot/vqbet_pusht"
LEROBOT_RUNTIME = "a1809ad3de96c6989acd33c0650849bf4f631929"


def main(output: Path) -> int:
    policy = VQBeTPolicy.from_pretrained(MODEL_ID, map_location="cpu")
    cfg = policy.config
    report = {
        "schema": "eprc-vqbet-native-runtime-load-v1",
        "model_id": MODEL_ID,
        "lerobot_runtime_commit": LEROBOT_RUNTIME,
        "runtime_native_mlp_hidden_dim": getattr(cfg, "mlp_hidden_dim", None),
        "n_obs_steps": int(cfg.n_obs_steps),
        "action_chunk_size": int(cfg.action_chunk_size),
        "n_action_pred_token": int(cfg.n_action_pred_token),
        "image_features": sorted(cfg.image_features.keys()),
        "state_shape": list(cfg.robot_state_feature.shape),
        "action_shape": list(cfg.action_feature.shape),
        "parameter_count": int(sum(p.numel() for p in policy.parameters())),
        "vq_discretized": bool(
            policy.vqbet.action_head.vqvae_model.discretized.detach().cpu().item()
        ),
        "all_parameters_finite": bool(
            all(torch.isfinite(p).all().item() for p in policy.parameters())
        ),
        "claim_boundary": (
            "Checkpoint-native runtime load gate only. "
            "No physical intervention or DEC claim is made."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))

    if report["runtime_native_mlp_hidden_dim"] is None:
        raise RuntimeError("checkpoint-native runtime did not expose mlp_hidden_dim")
    if not report["all_parameters_finite"]:
        raise RuntimeError("loaded checkpoint contains non-finite parameters")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("/tmp/eprc/vqbet_native_load.json"))
    args = parser.parse_args()
    raise SystemExit(main(args.output))
