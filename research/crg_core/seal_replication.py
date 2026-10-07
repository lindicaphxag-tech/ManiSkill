from __future__ import annotations

import argparse
import json
from pathlib import Path

from .replication_record import canonical_digest, validate_replication_record


def seal_record(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["evidence_digest"] = canonical_digest(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validate_replication_record(path)
    return data["evidence_digest"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal and schema-check a claimed CRG replication; independence requires external audit."
    )
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    digest = seal_record(args.record)
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
