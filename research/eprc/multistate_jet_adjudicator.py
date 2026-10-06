from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


FROZEN_SEEDS=(101,211,307,401,503)


@dataclass(frozen=True)
class MultiStateJetResult:
    frozen_seeds: tuple[int, ...]
    first_order_contracting_count: int
    jet_upgrade_count: int
    jet_rescue_count: int
    both_rejected_count: int
    all_dec_stable: bool
    promotion_decision: str
    reason: str


def adjudicate_records(records: list[dict]) -> MultiStateJetResult:
    by_seed={int(r["environment_reset_seed"]):r for r in records}
    if tuple(sorted(by_seed)) != tuple(sorted(FROZEN_SEEDS)):
        raise ValueError(
            f"seed set mismatch: got {sorted(by_seed)}, expected {list(FROZEN_SEEDS)}"
        )

    protocols={r["protocol_id"] for r in records}
    if len(protocols)!=1:
        raise ValueError("protocol drift across prospective states")

    contracting=0
    jet_upgrade=0
    rescue=0
    rejected=0
    stable=True

    for seed in FROZEN_SEEDS:
        r=by_seed[seed]
        loc=r.get("locality_refinement")
        if not loc or loc.get("status")!="executed_prospective_protocol":
            raise ValueError(f"seed {seed}: missing locality refinement")
        jet=loc.get("response_jet_diagnostic")
        if not jet:
            raise ValueError(f"seed {seed}: missing response jet diagnostic")

        first=bool(loc["contracting"])
        richer=bool(jet["supports_model_order_upgrade"])
        stable=stable and bool(r["dec"]["replicate_stability_certified"])

        contracting += int(first)
        jet_upgrade += int(richer)
        rescue += int((not first) and richer)
        rejected += int((not first) and (not richer))

    if rescue == 0:
        decision="DROP_JET_FROM_FLAGSHIP"
        reason=(
            "none of the frozen disjoint states required and passed a held-out "
            "model-order upgrade"
        )
    elif rescue >= 3:
        decision="PROMOTE_TO_BROADER_PROSPECTIVE_TEST"
        reason=(
            "at least three frozen states reject first order but pass the "
            "held-out richer-model gate"
        )
    else:
        decision="KEEP_AS_SECONDARY_MECHANISM"
        reason=(
            "some frozen states support model-order escalation, but prevalence "
            "is insufficient for a flagship claim"
        )

    return MultiStateJetResult(
        frozen_seeds=FROZEN_SEEDS,
        first_order_contracting_count=contracting,
        jet_upgrade_count=jet_upgrade,
        jet_rescue_count=rescue,
        both_rejected_count=rejected,
        all_dec_stable=stable,
        promotion_decision=decision,
        reason=reason,
    )


def load_directory(root: str | Path) -> list[dict]:
    root=Path(root)
    records=[]
    for p in sorted(root.rglob("*.json")):
        data=json.loads(p.read_text(encoding="utf-8"))
        if "environment_reset_seed" in data and "locality_refinement" in data:
            records.append(data)
    return records


def main() -> int:
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("artifact_root",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()

    result=adjudicate_records(load_directory(args.artifact_root))
    payload=asdict(result)
    text=json.dumps(payload,indent=2,sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text+"\n",encoding="utf-8")
    print(text)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
