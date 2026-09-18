#!/usr/bin/env python3
"""Validate the Research Writer claim-evidence CSV schema."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

REQUIRED = [
    "claim_id",
    "claim",
    "class",
    "evidence",
    "scope",
    "inference_ceiling",
    "status",
    "location",
    "notes",
]

CLASSES = {"OBSERVED", "LITERATURE", "INFERENCE", "HYPOTHESIS"}
CEILINGS = {"DESCRIPTIVE", "ASSOCIATIVE", "PREDICTIVE", "CAUSAL", "MECHANISTIC"}
STATUSES = {"supported", "partial", "unresolved", "rejected"}

def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != REQUIRED:
            errors.append(
                "Header must be exactly: " + ",".join(REQUIRED)
            )
            return errors

        seen = set()
        for line_no, row in enumerate(reader, start=2):
            cid = row["claim_id"].strip()
            if not cid:
                errors.append(f"line {line_no}: missing claim_id")
            elif cid in seen:
                errors.append(f"line {line_no}: duplicate claim_id {cid}")
            seen.add(cid)

            klass = row["class"].strip().upper()
            if klass and klass not in CLASSES:
                errors.append(f"line {line_no}: invalid class {row['class']!r}")

            ceiling = row["inference_ceiling"].strip().upper()
            if ceiling and ceiling not in CEILINGS:
                errors.append(
                    f"line {line_no}: invalid inference_ceiling "
                    f"{row['inference_ceiling']!r}"
                )

            status = row["status"].strip().lower()
            if status and status not in STATUSES:
                errors.append(f"line {line_no}: invalid status {row['status']!r}")

            if status == "supported" and not row["evidence"].strip():
                errors.append(f"line {line_no}: supported claim has no evidence")

    return errors

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()

    errors = validate(args.ledger)
    if errors:
        print("Claim ledger validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Claim ledger OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
