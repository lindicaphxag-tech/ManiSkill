"""Verify the original CRG #53 six-file archive and frozen replay.

All original bytes are SHA-256 pinned; only floating point *recomputation*
from those originals may differ across NumPy/platform versions.
This program cannot manufacture transfer authorizations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from research.crg_core.prospective.aggregate_direct_counterfactual import evaluate


EXPECTED_SHA256 = {
    "direct_counterfactual_result.json": "57ccb088e82a1bee48b132bf3a8ffe97dcae818e02cf2f133dbd2dd8eddae22e",
    "state-311.json": "928a57807960a49e10968d6ca65dc1d991cef3b3ad1538c977d734922460421d",
    "state-313.json": "54df98e940fe1718e8b2ff3c3135dbb485b87a18060d23753d73f014c99a1b0b",
    "state-317.json": "f7cdeb18271a38ea9df0d41c636eb655fa909fd9832b527763380d0f036c06e2",
    "state-331.json": "346956381c80eda455a65f275c26ead26c9cdc4a5dfc1af05439a4002c0931a5",
    "state-337.json": "fad347bf46a0f2da5bf7010c460c1155377b1fa0f43896e98922f3903f69d047",
}


def compare_replay(expected, actual, path="$"):
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        assert expected == actual and type(expected) is type(actual), path
    elif isinstance(expected, (float, int)):
        assert isinstance(actual, (float, int)) and not isinstance(actual, bool), path
        if isinstance(expected, int):
            assert isinstance(actual, int) and expected == actual, path
        else:
            assert math.isfinite(expected) and math.isfinite(actual), path
            assert math.isclose(expected, actual, rel_tol=1e-10, abs_tol=1e-10), (
                path, expected, actual
            )
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(expected) == len(actual), path
        for index, (a, b) in enumerate(zip(expected, actual)):
            compare_replay(a, b, f"{path}[{index}]")
    elif isinstance(expected, dict):
        assert isinstance(actual, dict) and expected.keys() == actual.keys(), path
        for key in expected:
            compare_replay(expected[key], actual[key], f"{path}.{key}")
    else:
        raise TypeError(f"Unexpected JSON type at {path}: {type(expected)}")


def verify(root: Path):
    discovered = {p.name for p in root.iterdir() if p.is_file()}
    assert discovered == set(EXPECTED_SHA256), (
        "missing/extra original evidence files", discovered
    )
    for name, expected in EXPECTED_SHA256.items():
        found = hashlib.sha256((root / name).read_bytes()).hexdigest()
        assert found == expected, (name, found, expected)

    original = json.loads((root / "direct_counterfactual_result.json").read_text())
    recomputed = evaluate(root)
    compare_replay(original, recomputed)

    assert original["state_clusters_total"] == 5
    assert original["dependent_requests_total"] == 10
    assert original["official_policy_forward_calls"] == 240
    assert original["certified_transfer_authorizations"] == 0
    assert original["missing_controller_hard_bound"] is True
    assert original["outcome"] == "DESCRIPTIVE_NO_TRUSTED_BOUND"
    print("PASS: six original SHA-256 hashes, exact non-numeric fields, "
          "numerical replay within 1e-10, 5 states, 10 requests, "
          "240 calls, 0 certified transfers.")


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--input-dir", required=True, type=Path)
    args = cli.parse_args()
    verify(args.input_dir)
