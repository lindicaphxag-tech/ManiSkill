from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.eprc.replication_record import canonical_evidence_digest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal an EPRC/DEC replication JSON with a canonical SHA-256 digest."
    )
    parser.add_argument("record_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    data = json.loads(args.record_json.read_text(encoding="utf-8"))
    data["evidence_digest"] = canonical_evidence_digest(data)
    output = args.output or args.record_json
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(data["evidence_digest"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
