#!/usr/bin/env python3
"""Check that a revision keeps the qualifiers of its source.

A qualifier that carries a design limit or uncertainty ("exploratory", "may",
"computed on the same runs") is part of the claim. This script finds such
phrases in SOURCE and reports each one missing from REVISED. It does not judge
whether the revision is right: an author may drop a hedge when the evidence changed.

Matching is by presence in the whole revision, not per sentence. A "may" kept
anywhere in REVISED satisfies every "may" in SOURCE, so read the report as a
screen, not a verdict.

Exit code: 1 when a ledger qualifier is missing from REVISED, 2 when an input file cannot
be read (so a mistyped path never looks like a blocked release), else 0.
Phrases from the built-in list are review flags only and never change the exit code.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from pathlib import Path

csv.field_size_limit(10_000_000)

# Screening aid, not a rule (see references/patterns.md). A phrase here is a prompt to look,
# not proof that the revision is wrong. Edit the list; the matching code does not change.
QUALIFIERS = [
    # modal and epistemic
    "may", "might", "could", "appears", "appeared", "suggest", "suggests", "suggested",
    "possibly", "likely", "putative", "tentatively",
    # design limit
    "exploratory", "post hoc", "subgroup", "subgroups", "preliminary", "pilot", "in-sample",
    "computed on the same", "cross-sectional", "observational", "ex vivo", "in vitro",
    "in mice", "in this cohort",
    # statistical
    "non-significant", "not statistically significant", "detectably", "nominal", "unadjusted",
]

# Copied from bench/prose/score_prose.py (DASHES, normalise), then extended. Keep the dash
# map in step with that file.
DASHES = str.maketrans({"−": "-", "–": "-", "—": "-", "‐": "-", "‑": "-"})
QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def normalise(text: str) -> str:
    """Lower-case, unify dashes and quotes, and turn hyphens and whitespace into spaces.

    Each character maps to one character, so offsets in the result match the original text.
    """
    text = text.translate(DASHES).translate(QUOTES).replace("-", " ")
    text = "".join(c.lower() if len(c.lower()) == 1 else c for c in text)
    return re.sub(r"[^\S\n]", " ", text)


def phrase_regex(phrase: str) -> re.Pattern[str]:
    words = normalise(phrase).split()
    body = r"\s+".join(re.escape(w) for w in words)
    return re.compile(rf"(?<![a-z0-9]){body}(?![a-z0-9])")


ABBREVIATIONS = ("e.g", "i.e", "fig", "figs", "et al", "vs", "approx", "ca", "cf", "no", "eq")
MARKS = (". ", "? ", "! ", ".\n", "\n\n")


def is_boundary(text: str, i: int) -> bool:
    """A '. ' ends a sentence unless it follows a known abbreviation such as 'Fig' or 'e.g'."""
    if text[i] != ".":
        return True
    word = re.search(r"[A-Za-z.]+$", text[:i])
    return not (word and word.group().lower().strip(".") in ABBREVIATIONS)


def sentence_at(text: str, pos: int) -> str:
    start = 0
    for m in MARKS:
        i = text.rfind(m, 0, pos)
        while i != -1 and not is_boundary(text, i):
            i = text.rfind(m, 0, i)
        if i != -1:
            start = max(start, i + len(m))
    ends = []
    for m in MARKS:
        i = text.find(m, pos)
        while i != -1 and not is_boundary(text, i):
            i = text.find(m, i + 1)
        if i != -1:
            ends.append(i)
    end = min(ends) + 1 if ends else len(text)
    return " ".join(text[start:end].split())


def find_missing_from_list(source: str, revised: str) -> list[dict]:
    norm_source, norm_revised = normalise(source), normalise(revised)
    issues = []
    for phrase in QUALIFIERS:
        rx = phrase_regex(phrase)
        if rx.search(norm_revised):
            continue
        for m in rx.finditer(norm_source):
            issues.append({
                "severity": "review",
                "line": source.count("\n", 0, m.start()) + 1,
                "message": f"qualifier dropped from revision: {sentence_at(source, m.start())}",
                "match": source[m.start():m.end()],
            })
    return sorted(issues, key=lambda i: i["line"])


def ledger_has_qualifiers_column(path: Path) -> bool:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return "qualifiers" in (csv.DictReader(fh).fieldnames or [])


def ledger_qualifiers(path: Path) -> list[tuple[str, int, str]]:
    """Return (claim_id, ledger line, qualifier) for every non-rejected claim."""
    found = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            line_no = reader.line_num  # last physical line of the record
            if (row.get("status") or "").strip().lower() == "rejected":
                continue
            for q in (row.get("qualifiers") or "").split(";"):
                if q.strip():
                    found.append(((row.get("claim_id") or "").strip(), line_no, q.strip()))
    return found


def find_missing_from_ledger(ledger: Path, revised: str) -> list[dict]:
    norm_revised = normalise(revised)
    issues = []
    for claim_id, line_no, qualifier in ledger_qualifiers(ledger):
        if not phrase_regex(qualifier).search(norm_revised):
            issues.append({
                "severity": "error",
                "line": 0,
                "message": f"ledger qualifier missing from revision: claim {claim_id} "
                           f"(ledger line {line_no}) must keep {qualifier!r}",
                "match": qualifier,
            })
    return issues


def check(source: str, revised: str, ledger: Path | None = None) -> list[dict]:
    issues = find_missing_from_list(source, revised)
    if ledger is not None:
        issues = find_missing_from_ledger(ledger, revised) + issues
    return issues


def self_test() -> int:
    failures = []

    def expect(name: str, ok: bool) -> None:
        if not ok:
            failures.append(name)

    src = "The effect was seen in an exploratory subgroup. It may reflect dosing."
    got = check(src, "The effect was seen in a subgroup. It may reflect dosing.")
    expect("exploratory dropped is flagged",
           [i["match"] for i in got] == ["exploratory"] and got[0]["severity"] == "review")
    expect("may kept is not flagged", not any(i["match"] == "may" for i in got))
    expect("flag carries sentence", "exploratory subgroup" in got[0]["message"])

    expect("dismay is not may", check("The dismay was clear.", "The tone was clear.") == [])
    expect("whole word only: mayor", check("The mayor spoke.", "The mayor spoke.") == [])
    expect("en dash matches hyphen and space",
           check("A post–hoc test.", "A post hoc test.") == []
           and check("A post-hoc test.", "A post–hoc test.") == [])
    expect("curly case and line wrap",
           check("Computed on the same\nruns.", "COMPUTED ON THE SAME runs.") == [])

    with tempfile.TemporaryDirectory() as tmp:
        ledger = Path(tmp) / "claims.csv"
        ledger.write_text(
            "claim_id,claim,class,evidence,scope,inference_ceiling,status,location,notes,qualifiers\n"
            "C001,x,INFERENCE,e,s,ASSOCIATIVE,supported,l,,computed on the same runs; may\n"
            "C002,y,INFERENCE,e,s,ASSOCIATIVE,rejected,l,,gone\n",
            encoding="utf-8",
        )
        got = check("R2 was high.", "R2 was high and may generalise.", ledger)
        expect("ledger qualifier dropped is an error",
               len(got) == 1 and got[0]["severity"] == "error" and "C001" in got[0]["message"])
        expect("rejected claim is skipped", not any("C002" in i["message"] for i in got))
        expect("ledger qualifiers kept",
               check("R2.", "R2 computed on the same runs; it may fail.", ledger) == [])

    expect("abbreviation keeps the sentence whole",
           "e.g. foo may bar" in check("Fig. 2 e.g. foo may bar.", "x.")[0]["message"])
    expect("decimal does not split",
           "p = 0.03, it may" in check("p = 0.03, it may help.", "x.")[0]["message"])
    with tempfile.TemporaryDirectory() as tmp:
        multi = Path(tmp) / "claims.csv"
        multi.write_text(
            "claim_id,claim,class,evidence,scope,inference_ceiling,status,location,notes,qualifiers\n"
            'C1,"a\nb",INFERENCE,e,s,ASSOCIATIVE,supported,l,,may\n'
            "C2,y,INFERENCE,e,s,ASSOCIATIVE,supported,l,,exploratory\n", encoding="utf-8")
        got = {i["match"]: i["message"] for i in check("x", "y", multi)}
        expect("ledger line is the physical line", "ledger line 4" in got.get("exploratory", ""))
        expect("column check", ledger_has_qualifiers_column(multi))

    if failures:
        print("Self-test failed:", failures)
        return 1
    print("qualifier_check self-test OK")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("source", nargs="?", type=Path)
    p.add_argument("revised", nargs="?", type=Path)
    p.add_argument("--ledger", type=Path, help="claims.csv with a qualifiers column")
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if a.source is None or a.revised is None:
        p.error("SOURCE and REVISED are required unless --self-test is used")

    read = lambda f: f.read_text(encoding="utf-8", errors="replace")
    try:
        source, revised = read(a.source), read(a.revised)
        issues = check(source, revised, a.ledger)
        no_column = a.ledger is not None and not ledger_has_qualifiers_column(a.ledger)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"qualifier_check: cannot read input: {exc}", file=sys.stderr)
        return 2
    if no_column:
        print(f"note: {a.ledger} has no `qualifiers` column, so no ledger qualifiers were checked.",
              file=sys.stderr)
    if a.json:
        print(json.dumps(issues, indent=2))
    elif not issues:
        print("No dropped qualifiers found.")
    else:
        for x in issues:
            where = f"line {x['line']}" if x["line"] else "ledger"
            print(f"[{x['severity']}] {where}: {x['message']} ({x['match']!r})")
        errors = sum(x["severity"] == "error" for x in issues)
        print(f"\n{len(issues)} flag(s), {errors} error(s). Review each: dropping a hedge is "
              "right only when the evidence changed.")
    return 1 if any(x["severity"] == "error" for x in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
