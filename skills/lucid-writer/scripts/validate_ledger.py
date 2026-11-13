#!/usr/bin/env python3
"""Validate the Lucid Writer claim-evidence CSV schema."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

# Long claim or notes cells are legitimate; the stdlib default of 128 KB is not a ledger rule.
csv.field_size_limit(10_000_000)

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

# A ledger written before `qualifiers` existed has the 9-column header and stays valid.
REQUIRED_WITH_QUALIFIERS = [*REQUIRED, "qualifiers"]

CLASSES = {"OBSERVED", "LITERATURE", "INFERENCE", "HYPOTHESIS"}
CEILINGS = {"DESCRIPTIVE", "ASSOCIATIVE", "PREDICTIVE", "CAUSAL", "MECHANISTIC"}
STATUSES = {"supported", "partial", "unresolved", "rejected"}

def validate(path: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). With strict, warnings are moved into errors."""
    try:
        return _validate(path, strict)
    except UnicodeDecodeError as exc:
        return [f"{path.name} is not valid UTF-8 ({exc.reason}); save it as UTF-8"], []
    except OSError as exc:
        return [f"cannot read {path}: {exc.strerror}"], []


def _validate(path: Path, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames not in (REQUIRED, REQUIRED_WITH_QUALIFIERS):
            errors.append(
                "Header must be exactly one of:\n  legacy: " + ",".join(REQUIRED)
                + "\n  current: " + ",".join(REQUIRED_WITH_QUALIFIERS)
            )
            return errors, warnings

        seen = set()
        for row in reader:
            line_no = reader.line_num  # last physical line of the record
            if None in row:
                errors.append(f"line {line_no}: more fields than the header")
            if None in row.values():
                errors.append(f"line {line_no}: fewer fields than the header")
            row = {key: value or "" for key, value in row.items() if key is not None}
            row.setdefault("qualifiers", "")
            cid = row["claim_id"].strip()
            if not cid:
                errors.append(f"line {line_no}: missing claim_id")
            elif cid.upper() in seen:
                errors.append(f"line {line_no}: duplicate claim_id {cid}")
            seen.add(cid.upper())

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

            if (
                status == "supported"
                and klass in {"HYPOTHESIS", "INFERENCE"}
                and not row["qualifiers"].strip()
            ):
                warnings.append(
                    f"line {line_no}: supported {klass} claim {cid} lists no qualifiers; "
                    "name the hedges or design limits it must keep, separated by ';'"
                )

    if strict:
        errors, warnings = errors + warnings, []
    return errors, warnings

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    errors, warnings = validate(args.ledger, strict=args.strict)
    for warning in warnings:
        print(f"warning: {warning}")
    if errors:
        print("Claim ledger validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Claim ledger OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
