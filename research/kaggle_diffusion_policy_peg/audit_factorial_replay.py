#!/usr/bin/env python3
"""Independent integrity audit for official PegInsertionSide 2x2 replay matrix.

No ManiSkill imports, training data, or private experiment material required.
The auditor verifies *every frozen source-seed outcome*, pairwise intersection
and recorded digest. It is independent code, but still author-operated.

Example:
    python audit_factorial.py --search downloaded-artifact --expected-size 100
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory

ARMS = (
    "upstream_baseline",
    "converter_only_pr1495",
    "controller_only_pr1472",
    "combined_pr1495_pr1472",
)
FROZEN_DATASET_SHA256 = "7d61e4319a0395b220574f1e26ea65bd4ad1406387fb3debfbea96a2ddbb6a9c"
FROZEN_BASE = "62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3"
FROZEN_CONVERTER = "69facfaafaa0ef233d36ef19e6cd9a0f03532ee0"
FROZEN_CONTROLLER = "eed9be164797d41540421bda8adb3840377d7087"
FROZEN_ARTIFACT_RUN = 37719545972


def hash_seed_order(seeds: list[int]) -> str:
    return hashlib.sha256(
        json.dumps(seeds, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def verify(doc: dict, *, expected_size: int, source_offset: int = 0, origin_run_id: int = FROZEN_ARTIFACT_RUN) -> dict:
    if doc.get("schema_version") != 1:
        raise ValueError("unexpected factorial evidence schema")
    for field, expected in (
        ("source_dataset_sha256", FROZEN_DATASET_SHA256),
        ("baseline_code_sha", FROZEN_BASE),
        ("converter_code_sha", FROZEN_CONVERTER),
        ("controller_code_sha", FROZEN_CONTROLLER),
        ("sample_size", expected_size),
    ):
        if doc.get(field) != expected:
            raise ValueError(f"frozen identity mismatch: {field}")
    if source_offset != 0:
        if doc.get("original_source_episode_offset") != source_offset:
            raise ValueError("wrong precommitted source episode offset")
        if doc.get("original_source_episode_indices") != list(range(source_offset,source_offset+expected_size)):
            raise ValueError("post-hoc source episode substitution detected")
    rows = doc.get("source_seed_matrix")
    if not isinstance(rows, list) or len(rows) != expected_size:
        raise ValueError("missing or incomplete source-seed matrix")
    if doc.get("status") != "factorial_replay_completed_not_policy_training":
        raise ValueError("incorrect empirical result type")
    if doc.get("trainable_four_way_factorial") is not False:
        raise ValueError("four-arm training claim must be false for this evidence")

    seed_order: list[int] = []
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != set(ARMS) | {"source_seed"}:
            raise ValueError(f"row {i}: missing or extra factorial arm")
        seed = row["source_seed"]
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError(f"row {i}: invalid source seed type")
        seed_order.append(seed)
        for arm in ARMS:
            if type(row[arm]) is not bool:
                raise ValueError(f"row {i}: non-Boolean actual replay result")
    if len(set(seed_order)) != expected_size:
        raise ValueError("source-seed duplication")

    results = {a: [r["source_seed"] for r in rows if r[a]] for a in ARMS}
    observed = {a: len(s) for a, s in results.items()}
    if observed != doc.get("per_arm_success_count"):
        raise ValueError("claimed success count differs from source-seed matrix")

    pairwise = doc.get("pairwise", {})
    if set(pairwise) != {f"{a}|{b}" for a,b in combinations(ARMS,2)}:
        raise ValueError("pairwise edge set incomplete")
    for a,b in combinations(ARMS,2):
        key=f"{a}|{b}"
        seeds=[r["source_seed"] for r in rows if r[a] and r[b]]
        entry=pairwise[key]
        if entry.get("intersection_count") != len(seeds):
            raise ValueError(f"{key}: mismatched pairwise intersection")
        if entry.get("source_seed_sha256") != hash_seed_order(seeds):
            raise ValueError(f"{key}: corrupted pairwise source-seed digest")

    fourway = [r["source_seed"] for r in rows if all(r[a] for a in ARMS)]
    if doc.get("four_way_intersection_count") != len(fourway):
        raise ValueError("wrong four-way intersection count")
    if doc.get("four_way_intersection_source_seed_sha256") != hash_seed_order(fourway):
        raise ValueError("wrong four-way seed digest")

    discordance={}
    for a,b in combinations(ARMS,2):
        only_a=sum(1 for row in rows if row[a] and not row[b])
        only_b=sum(1 for row in rows if row[b] and not row[a])
        discordance[f"{a}|{b}"]={"a_only":only_a,"b_only":only_b,"discordant_total":only_a+only_b}
    # Four-arm percentage-point interaction is only descriptive for frozen replay,
    # not a controlled causal effect on learned-policy task performance.
    n=expected_size
    interaction=(
        observed["combined_pr1495_pr1472"]
        - observed["converter_only_pr1495"]
        - observed["controller_only_pr1472"]
        + observed["upstream_baseline"]
    )
    return {
        "audit_status":"passed",
        "replay_not_policy_success":True,
        "origin_run_id":origin_run_id,
        "independent_source_offset":source_offset,
        "source_seeds_audited":n,
        "per_arm_success_count":observed,
        "pairwise_discordance":discordance,
        "four_way_common_sources":len(fourway),
        "factorial_interaction_count":interaction,
        "factorial_interaction_fraction":f"{interaction}/{n}",
        "frozen_code_identity_verified":True,
        "all_pairwise_source_digest_verified":True,
        "four_way_source_digest_verified":True,
        "claim_boundary":"Replay conversion of fixed official demonstrations, not learned-policy superiority or upstream maintainer approval."
    }



def verify_execution_binding(doc: dict, execution: dict, *, offset: int, count: int) -> dict:
    """Refuse ledger claims unsupported by *physical* sliced input HDF5 groups."""
    if execution.get("status") != "passed":
        raise ValueError("source execution did not complete")
    if execution.get("source_episode_offset") != offset:
        raise ValueError("source execution offset differs from frozen cohort")
    indices=list(range(offset,offset+count))
    if execution.get("source_episode_indices") != indices:
        raise ValueError("physical source episode indices do not match frozen cohort")
    if execution.get("factorial_replay") != doc:
        raise ValueError("experiment-log factorial record differs from supplied ledger")
    proof=execution.get("source_materialization")
    if not isinstance(proof,dict) or set(proof)!=set(ARMS):
        raise ValueError("missing arm-specific physical HDF5 cohort proof")
    expected_seeds=[row["source_seed"] for row in doc["source_seed_matrix"]]
    identity_hashes={}
    for arm in ARMS:
        evidence=proof[arm]
        if evidence.get("selection_verified") is not True:
            raise ValueError(f"{arm}: original-source selection not verified")
        if evidence.get("original_source_episode_indices") != indices:
            raise ValueError(f"{arm}: physical HDF5 source indices mismatch")
        if evidence.get("original_source_episode_seeds") != expected_seeds:
            raise ValueError(f"{arm}: physical HDF5 source seeds mismatch")
        ids=evidence.get("original_source_episode_ids")
        if not isinstance(ids,list) or len(ids)!=count or len(set(ids))!=count:
            raise ValueError(f"{arm}: ambiguous original source IDs")
        if evidence.get("replay_h5_group_count") != count:
            raise ValueError(f"{arm}: HDF5 subset cardinality mismatch")
        h5=evidence.get("selected_h5_sha256")
        meta=evidence.get("selected_json_sha256")
        if not isinstance(h5,str) or not isinstance(meta,str) or any(
            len(x)!=64 or any(c not in "0123456789abcdef" for c in x) for x in (h5,meta)
        ):
            raise ValueError(f"{arm}: missing physical source file identity digests")
        canonical={
            "indices":indices, "ids":ids,"seeds":expected_seeds,
            "h5":h5,"json":meta,
        }
        digest=hashlib.sha256(json.dumps(
            canonical,sort_keys=True,separators=(",",":")
        ).encode("utf-8")).hexdigest()
        if evidence.get("identity_sha256")!=digest:
            raise ValueError(f"{arm}: tampered HDF5 slice proof")
        identity_hashes[arm]=digest
    if len(set(identity_hashes.values()))!=1:
        raise ValueError("four factor arms trained/replayed from non-identical source datasets")
    return {
        "physical_hdf5_cohort_verified":True,
        "source_episode_offset":offset,
        "original_source_id_count":count,
        "physical_source_identity_sha256":next(iter(identity_hashes.values())),
        "all_four_arms_bound_to_same_original_episode_seeds":True,
    }


def self_test() -> None:
    import copy
    arms=list(ARMS)
    rows=[dict(source_seed=i, **{arm:(i%3!=j%3) for j,arm in enumerate(arms)}) for i in range(4)]
    d={
        "schema_version":1,"status":"factorial_replay_completed_not_policy_training",
        "source_dataset_sha256":FROZEN_DATASET_SHA256,
        "baseline_code_sha":FROZEN_BASE,
        "converter_code_sha":FROZEN_CONVERTER,
        "controller_code_sha":FROZEN_CONTROLLER,
        "sample_size":4,
        "source_seed_matrix":rows,
        "per_arm_success_count":{arm:sum(row[arm] for row in rows) for arm in arms},
        "pairwise":{},
        "four_way_intersection_count":sum(all(row[a] for a in arms) for row in rows),
        "trainable_four_way_factorial":False,
    }
    for a,b in combinations(arms,2):
        seeds=[r["source_seed"] for r in rows if r[a] and r[b]]
        d["pairwise"][f"{a}|{b}"]={"intersection_count":len(seeds),"source_seed_sha256":hash_seed_order(seeds)}
    seeds=[r["source_seed"] for r in rows if all(r[a] for a in arms)]
    d["four_way_intersection_source_seed_sha256"]=hash_seed_order(seeds)
    assert verify(d,expected_size=4)["audit_status"]=="passed"
    mutations=[
        ("count",lambda x:x["per_arm_success_count"].__setitem__(arms[0],99)),
        ("seed",lambda x:x["source_seed_matrix"][1].__setitem__("source_seed",0)),
        ("matrix",lambda x:x["source_seed_matrix"][0].__setitem__(arms[0],not x["source_seed_matrix"][0][arms[0]])),
        ("digest",lambda x:x["pairwise"][f"{arms[0]}|{arms[1]}"].__setitem__("source_seed_sha256","0"*64)),
        ("causal",lambda x:x.__setitem__("trainable_four_way_factorial",True)),
        ("identity",lambda x:x.__setitem__("converter_code_sha","0"*40)),
    ]
    for name,mutate in mutations:
        x=copy.deepcopy(d)
        mutate(x)
        try:
            verify(x,expected_size=4)
        except ValueError:
            continue
        raise AssertionError(f"tamper accepted: {name}")
    print("audit self-test: 6 tampering cases rejected")


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--search",type=Path,help="Root extracted from the exact Actions artifact")
    p.add_argument("--expected-size",type=int,default=100)
    p.add_argument("--source-offset",type=int,default=0)
    p.add_argument("--origin-run-id",type=int,default=FROZEN_ARTIFACT_RUN)
    p.add_argument("--verify-physical-slices",action="store_true",help="Also bind every actual HDF5 input cohort to frozen seed identities")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--output",type=Path,help="Write independently derived JSON report")
    args=p.parse_args()
    if args.self_test:
        self_test()
        return
    if args.search is None:
        p.error("--search is required without --self-test")
    matches=list(args.search.rglob("factorial_replay.json"))
    if len(matches)!=1:
        raise ValueError(f"exactly one factorial_replay.json expected, got {matches}")
    result=verify(
        json.loads(matches[0].read_text(encoding="utf-8")),
        expected_size=args.expected_size,
        source_offset=args.source_offset,
        origin_run_id=args.origin_run_id,
    )
    if args.verify_physical_slices:
        logs=list(args.search.rglob("experiment_log.json"))
        if len(logs)!=1:
            raise ValueError(f"expected one original execution log, found {logs}")
        doc=json.loads(matches[0].read_text(encoding="utf-8"))
        proof=verify_execution_binding(
            doc,json.loads(logs[0].read_text(encoding="utf-8")),
            offset=args.source_offset,count=args.expected_size
        )
        result.update(proof)
    out=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.write_text(out,encoding="utf-8")
    print(out)


if __name__=="__main__":
    main()
