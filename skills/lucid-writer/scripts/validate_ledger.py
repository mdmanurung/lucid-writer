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

# Optional columns are appended, never inserted, so an older ledger stays valid.
# 9 columns (legacy), 10 with `qualifiers`, 11 with `qualifiers` and `warrant`.
REQUIRED_WITH_QUALIFIERS = [*REQUIRED, "qualifiers"]
REQUIRED_WITH_WARRANT = [*REQUIRED_WITH_QUALIFIERS, "warrant"]
HEADERS = [REQUIRED, REQUIRED_WITH_QUALIFIERS, REQUIRED_WITH_WARRANT]

# Optional .lucid-writer/evidence.csv, next to the ledger. One row per piece of evidence.
EVIDENCE_COLUMNS = ["claim_id", "evidence_id", "locator", "kind", "verdict", "notes"]
KINDS = {"passage", "table_cell", "figure_panel", "analysis_output", "citation"}
# Citation rows use the four-level scale in references/evidence.md; other rows use STATUSES.
CITATION_VERDICTS = {"supports", "partially supports", "does not support", "cannot determine"}
SUPPORTING = {"supported", "supports"}

CLASSES = {"OBSERVED", "LITERATURE", "INFERENCE", "HYPOTHESIS"}
CEILINGS = {"DESCRIPTIVE", "ASSOCIATIVE", "PREDICTIVE", "CAUSAL", "MECHANISTIC"}
STATUSES = {"supported", "partial", "unresolved", "rejected"}

def validate_evidence(
    path: Path, claims: dict[str, str]
) -> tuple[list[str], list[str], set[str] | None]:
    """Check evidence.csv against the ledger's claims (id -> status).

    Returns (errors, warnings, ids of claims with at least one valid supporting row), or None
    for the ids when the header is wrong and the rows were not read.
    """
    errors: list[str] = []
    warnings: list[str] = []
    supported_ids: set[str] = set()
    seen: set[tuple[str, str]] = set()
    try:
        return _validate_evidence(path, claims, errors, warnings, supported_ids, seen)
    except UnicodeDecodeError as exc:
        return [f"{path.name} is not valid UTF-8 ({exc.reason}); save it as UTF-8"], [], None
    except OSError as exc:
        return [f"cannot read {path}: {exc.strerror}"], [], None


def _validate_evidence(path, claims, errors, warnings, supported_ids, seen):
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != EVIDENCE_COLUMNS:
            return [f"{path.name}: header must be exactly: " + ",".join(EVIDENCE_COLUMNS)], [], None
        for row in reader:
            line_no = reader.line_num  # last physical line of the record
            if None in row or None in row.values():
                errors.append(f"{path.name} line {line_no}: wrong number of fields")
            row = {k: v or "" for k, v in row.items() if k is not None}
            cid = row["claim_id"].strip().upper()
            eid = row["evidence_id"].strip()
            kind = row["kind"].strip().lower()
            verdict = row["verdict"].strip().lower()
            if cid not in claims:
                errors.append(f"{path.name} line {line_no}: claim_id {row['claim_id']!r} is not in the ledger")
            if not eid:
                errors.append(f"{path.name} line {line_no}: missing evidence_id")
            elif (cid, eid) in seen:
                errors.append(f"{path.name} line {line_no}: duplicate evidence_id {eid} for claim {cid}")
            seen.add((cid, eid))
            if kind not in KINDS:
                errors.append(f"{path.name} line {line_no}: invalid kind {row['kind']!r}")
            allowed = CITATION_VERDICTS if kind == "citation" else STATUSES
            if verdict not in allowed:
                errors.append(
                    f"{path.name} line {line_no}: invalid verdict {row['verdict']!r} for kind "
                    f"{kind!r}; use " + "|".join(sorted(allowed))
                )
            metadata_only = (
                kind == "citation" and verdict == "supports"
                and "metadata only" in row["notes"].lower()
            )
            if metadata_only:
                errors.append(
                    f"{path.name} line {line_no}: a citation checked on metadata only cannot be "
                    "`supports`; use `partially supports` (references/evidence.md)"
                )
            elif verdict in SUPPORTING and kind in KINDS and verdict in allowed:
                supported_ids.add(cid)
                if not row["locator"].strip():
                    errors.append(f"{path.name} line {line_no}: a {verdict} row needs a locator")
            elif not row["locator"].strip():
                warnings.append(f"{path.name} line {line_no}: no locator for {cid}/{eid}")
    return errors, warnings, supported_ids


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
    evidence_path = path.with_name("evidence.csv")
    use_evidence_file = evidence_path.is_file()
    claim_status: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames not in HEADERS:
            errors.append(
                "Header must be exactly one of:\n  legacy: " + ",".join(REQUIRED)
                + "\n  with qualifiers: " + ",".join(REQUIRED_WITH_QUALIFIERS)
                + "\n  with qualifiers and warrant: " + ",".join(REQUIRED_WITH_WARRANT)
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
            row.setdefault("warrant", "")
            cid = row["claim_id"].strip()
            if not cid:
                errors.append(f"line {line_no}: missing claim_id")
            elif cid.upper() in seen:
                errors.append(f"line {line_no}: duplicate claim_id {cid}")
            seen.add(cid.upper())
            claim_status[cid.upper()] = row["status"].strip().lower()

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

            # When evidence.csv exists it takes precedence over the `evidence` column.
            if status == "supported" and not use_evidence_file and not row["evidence"].strip():
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

            if (
                status == "supported"
                and klass == "INFERENCE"
                and ceiling in {"CAUSAL", "MECHANISTIC"}
                and not row["warrant"].strip()
            ):
                warnings.append(
                    f"line {line_no}: supported INFERENCE claim {cid} with ceiling {ceiling} "
                    "has no warrant; state why the evidence licenses it and what would defeat it"
                )

    if use_evidence_file:
        ev_errors, ev_warnings, supported_ids = validate_evidence(evidence_path, claim_status)
        errors += ev_errors
        warnings += ev_warnings
        for cid, status in claim_status.items():
            if supported_ids is not None and status == "supported" and cid not in supported_ids:
                errors.append(f"claim {cid} is supported but evidence.csv has no supported row for it")

    if strict:
        errors, warnings = errors + warnings, []
    return errors, warnings


def self_test() -> int:
    import tempfile

    head9 = ",".join(REQUIRED)
    head10 = ",".join(REQUIRED_WITH_QUALIFIERS)
    head11 = ",".join(REQUIRED_WITH_WARRANT)
    ev_head = ",".join(EVIDENCE_COLUMNS)
    failures: list[str] = []

    def run(name, ledger, evidence=None, strict=False, errors=0, warnings=0, text=""):
        with tempfile.TemporaryDirectory() as tmp:
            claims = Path(tmp) / "claims.csv"
            claims.write_text(ledger, encoding="utf-8")
            if evidence is not None:
                (Path(tmp) / "evidence.csv").write_text(evidence, encoding="utf-8")
            e, w = validate(claims, strict=strict)
        got = (len(e), len(w))
        if got != (errors, warnings) or text not in " ".join(e + w):
            failures.append(f"{name}: expected {(errors, warnings)} with {text!r}, got {got} {e + w}")

    causal = f"{head11}\nC1,x,INFERENCE,e,s,CAUSAL,supported,l,,exploratory,\n"
    run("legacy ledger stays valid", f"{head9}\nC1,x,OBSERVED,e,s,DESCRIPTIVE,supported,l,\n")
    run("10-column ledger valid", f"{head10}\nC1,x,OBSERVED,e,s,DESCRIPTIVE,supported,l,,\n")
    run("warrant missing is a warning", causal, warnings=1, text="no warrant")
    run("warrant missing fails under strict", causal, strict=True, errors=1, text="no warrant")
    run("warrant given", f"{head11}\nC1,x,INFERENCE,e,s,CAUSAL,supported,l,,exploratory,assumes no confounding\n")
    run("warrant not required for associative",
        f"{head11}\nC1,x,INFERENCE,e,s,ASSOCIATIVE,supported,l,,may,\n")

    ledger = f"{head10}\nC1,x,OBSERVED,,s,DESCRIPTIVE,supported,l,,\n"
    good = f"{ev_head}\nC1,E1,Table 2 row 3,table_cell,supported,\n"
    run("evidence.csv replaces the evidence column", ledger, good)
    run("supported claim without evidence.csv or column", ledger, errors=1, text="no evidence")
    run("citation verdict scale",
        ledger, f"{ev_head}\nC1,E1,Smith 2020 p4,citation,supports,checked against full text\n")
    run("metadata-only citation cannot be supports",
        ledger, f"{ev_head}\nC1,E1,Smith 2020 p4,citation,supports,metadata only\n",
        errors=2, text="metadata only")
    run("metadata-only citation as partially supports",
        f"{head10}\nC1,x,LITERATURE,,s,DESCRIPTIVE,partial,l,,\n",
        f"{ev_head}\nC1,E1,Smith 2020 p4,citation,partially supports,metadata only\n")
    run("citation row with a status verdict",
        ledger, f"{ev_head}\nC1,E1,Smith 2020 p4,citation,supported,\n", errors=2, text="invalid verdict")
    run("passage row with a citation verdict",
        ledger, f"{ev_head}\nC1,E1,p4,passage,supports,\n", errors=2, text="invalid verdict")
    run("unknown claim id", ledger, f"{ev_head}\nC9,E1,p4,passage,supported,\n", errors=2, text="not in the ledger")
    run("bad kind", ledger, f"{ev_head}\nC1,E1,p4,table,supported,\n", errors=2, text="invalid kind")
    run("supported claim needs a supported row",
        ledger, f"{ev_head}\nC1,E1,p4,passage,partial,\n", errors=1, text="no supported row")
    run("supporting row needs a locator", ledger, f"{ev_head}\nC1,E1,,passage,supported,\n",
        errors=1, text="needs a locator")
    run("duplicate evidence id",
        ledger, f"{ev_head}\nC1,E1,p4,passage,supported,\nC1,E1,p5,passage,partial,\n",
        errors=1, text="duplicate evidence_id")
    run("bad header", f"a,b\n1,2\n", errors=1, text="Header must be exactly one of")
    run("bad evidence header", ledger, "a,b\n", errors=1, text="header must be exactly")

    with tempfile.TemporaryDirectory() as tmp:
        latin = Path(tmp) / "claims.csv"
        latin.write_bytes(f"{head9}\nC1,caf\xe9,OBSERVED,e,s,DESCRIPTIVE,supported,l,\n".encode("latin-1"))
        e, _ = validate(latin)
        if not (len(e) == 1 and "not valid UTF-8" in e[0]):
            failures.append(f"non-UTF-8 file: got {e}")
        e, _ = validate(Path(tmp) / "missing.csv")
        if not (len(e) == 1 and "cannot read" in e[0]):
            failures.append(f"missing file: got {e}")
        multi = Path(tmp) / "multi.csv"
        multi.write_text(f'{head9}\nC1,"two\nlines",OBSERVED,e,s,DESCRIPTIVE,supported,l,\nC2,y,BAD,e,s,DESCRIPTIVE,supported,l,\n', encoding="utf-8")
        e, _ = validate(multi)
        if not (len(e) == 1 and e[0].startswith("line 4:")):
            failures.append(f"physical line numbers: got {e}")

    if failures:
        print("Self-test failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("validate_ledger self-test OK")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.ledger is None:
        parser.error("ledger is required unless --self-test is used")

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
