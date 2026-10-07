#!/usr/bin/env python3
"""Build the single-file Kaggle kernel with its native test harness embedded."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
MARKER = 'HARNESS_BASE64 = "__NATIVE_TEST_HARNESS_B64__"'


def build(output: Path) -> None:
    template = (HERE / "run_assay.py").read_text(encoding="utf-8")
    harness = (HERE / "test_pr1495_native_assay.py").read_bytes()
    encoded = base64.b64encode(harness).decode("ascii")
    if template.count(MARKER) != 1:
        raise ValueError("Runner template must contain exactly one harness marker")
    script = template.replace(MARKER, f"HARNESS_BASE64 = {json.dumps(encoded)}")
    metadata = json.loads((HERE / "kernel-metadata.json").read_text(encoding="utf-8"))

    output.mkdir(parents=True, exist_ok=True)
    (output / "run_assay.py").write_text(script, encoding="utf-8")
    (output / "kernel-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
