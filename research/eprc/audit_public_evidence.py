from __future__ import annotations

import json
from pathlib import Path


def audit(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text())
    rows = data["rows"]

    assert data["model_id"] == "lerobot/diffusion_pusht"
    assert data["n_states"] == len(rows) == 4
    assert data["raw_harm_rate"] == 1.0
    assert data["acceptance_rate"] == 0.0
    assert data["false_accept_rate"] == 0.0
    assert data["rejected_harm_protection_rate"] == 1.0
    assert data["fresh_exact_fallback_rate_on_rejection"] == 1.0

    assert all(row["raw_harm"] for row in rows)
    assert not any(row["accepted"] for row in rows)
    assert all(row["fallback_exactly_matches_fresh"] for row in rows)

    return {
        "states": len(rows),
        "harmful_raw_repairs": sum(row["raw_harm"] for row in rows),
        "accepted_repairs": sum(row["accepted"] for row in rows),
        "exact_fallbacks": sum(row["fallback_exactly_matches_fresh"] for row in rows),
    }


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    result = audit(here / "evidence" / "diffusion_pusht_refusal.json")
    print(json.dumps(result, sort_keys=True))
