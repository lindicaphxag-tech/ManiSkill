from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from research.eprc.external_replication_gate import validate_external_replication


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate one independent, result-bearing DEC/CRG/AMRC replication."
    )
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    audit = validate_external_replication(args.record)
    print(json.dumps(asdict(audit), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
