"""Materialize an exact, auditable non-overlapping source-episode cohort.

The official ManiSkill replay CLI's --count N selects the first N *input*
episodes. Merely slicing metadata for bookkeeping while copying the complete
input trajectory.h5 is an invalid holdout: it silently replays indices 0..N-1.

This helper physically copies ONLY the frozen source groups and reindexes the
official HDF5 + JSON metadata together so --count N cannot select the wrong
source episodes. Fails closed on ambiguous IDs, absent groups and seeds.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize_cohort(
    source_h5: Path, source_json: Path, dest_h5: Path,
    *, first_index: int, count: int,
) -> dict:
    import h5py

    if first_index < 0 or count <= 0:
        raise ValueError("invalid frozen cohort selection")
    metadata = json.loads(source_json.read_text(encoding="utf-8"))
    episodes = metadata.get("episodes")
    if not isinstance(episodes, list) or first_index + count > len(episodes):
        raise ValueError("frozen cohort missing from original metadata")
    selected = episodes[first_index:first_index+count]
    source_ids = [ep.get("episode_id") for ep in selected]
    source_seeds = [ep.get("episode_seed") for ep in selected]
    if any(type(k) is not int for k in source_ids):
        raise ValueError("invalid original episode_id")
    if any(type(k) is not int for k in source_seeds):
        raise ValueError("original episode_seed is absent or invalid")
    if len(set(source_ids)) != count or len(set(source_seeds)) != count:
        raise ValueError("duplicated source episode ID or seed")
    if any(ep.get("success") is not True for ep in selected):
        raise ValueError("frozen original cohort has unsuccessful source episode")
    if dest_h5.exists() or dest_h5.with_suffix(".json").exists():
        raise FileExistsError("refusing to overwrite frozen cohort source")
    dest_h5.parent.mkdir(parents=True, exist_ok=True)

    # Preflight every group BEFORE constructing the destination. Do not copy
    # from the beginning of source_h5 or trust coincidental episode ordering.
    with h5py.File(source_h5, "r") as source:
        names = [f"traj_{episode_id}" for episode_id in source_ids]
        if any(name not in source or not isinstance(source[name], h5py.Group) for name in names):
            raise ValueError("source HDF5 lacks a frozen metadata episode group")
        with h5py.File(dest_h5, "w") as target:
            for key, value in source.attrs.items():
                target.attrs[key] = value
            for new_id, (original_id, source_key) in enumerate(zip(source_ids, names)):
                source.copy(source_key, target, name=f"traj_{new_id}")

    cohort_meta = copy.deepcopy(metadata)
    cohort_meta["episodes"] = []
    for new_id, episode in enumerate(selected):
        item = copy.deepcopy(episode)
        item["episode_id"] = new_id
        cohort_meta["episodes"].append(item)
    output_meta = dest_h5.with_suffix(".json")
    output_meta.write_text(json.dumps(cohort_meta, indent=2) + "\n", encoding="utf-8")
    # Independent re-open checks are intentionally performed on the generated
    # artifact, not just on the in-memory selected metadata.
    with h5py.File(dest_h5,"r") as h5:
        if set(h5.keys()) != {f"traj_{i}" for i in range(count)}:
            raise AssertionError("raw selected trajectory HDF5 is not exact")
    checked = json.loads(output_meta.read_text(encoding="utf-8"))
    if [e["episode_seed"] for e in checked["episodes"]] != source_seeds:
        raise AssertionError("source seed order changed during cohort materialization")
    result = {
        "original_source_episode_indices": list(range(first_index,first_index+count)),
        "original_source_episode_ids": source_ids,
        "original_source_episode_seeds": source_seeds,
        "selected_h5_sha256": _sha(dest_h5),
        "selected_json_sha256": _sha(output_meta),
        "replay_h5_group_count": count,
        "selection_verified": True,
    }
    result["identity_sha256"] = hashlib.sha256(
        json.dumps({
            "indices":result["original_source_episode_indices"],
            "ids":source_ids,"seeds":source_seeds,
            "h5":result["selected_h5_sha256"],
            "json":result["selected_json_sha256"],
        },sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest()
    return result


def self_test():
    import h5py
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as directory:
        root=Path(directory)
        source=root/"original.h5"
        meta=source.with_suffix(".json")
        episodes=[{"episode_id":i*2,"episode_seed":1000+i,"success":True} for i in range(5)]
        meta.write_text(json.dumps({"episodes":episodes,"env_info":{"env_id":"test"}}))
        with h5py.File(source,"w") as f:
            f.attrs["version"]="test"
            for i in range(5):
                f.create_group(f"traj_{i*2}").create_dataset("actions",data=[i,i+1])
        selected=root/"selection.h5"
        result=materialize_cohort(source,meta,selected,first_index=2,count=2)
        assert result["original_source_episode_indices"] == [2,3]
        assert result["original_source_episode_ids"] == [4,6]
        assert result["original_source_episode_seeds"] == [1002,1003]
        with h5py.File(selected,"r") as f:
            assert list(f["traj_0/actions"][:]) == [2,3]
            assert list(f["traj_1/actions"][:]) == [3,4]
            assert "traj_4" not in f
        for args in ({"first_index":-1,"count":1},{"first_index":4,"count":2}):
            try: materialize_cohort(source,meta,root/"invalid.h5",**args)
            except ValueError: pass
            else: raise AssertionError("out-of-bound cohort was accepted")
        try: materialize_cohort(source,meta,selected,first_index=2,count=2)
        except FileExistsError: pass
        else: raise AssertionError("existing source cohort overwritten")
    print("exact source-HDF5 cohort slicing: self-test pass")


if __name__ == "__main__":
    self_test()
