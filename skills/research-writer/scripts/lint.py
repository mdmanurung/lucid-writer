#!/usr/bin/env python3
"""Conservative mechanical lint for research prose.

Flags release risks and low-information patterns. It does not judge scientific
validity or infer AI authorship.
"""

from __future__ import annotations
import argparse, json, re
from pathlib import Path

RULES = [
    ("release", r"\bTODO\b|\bTBD\b|\bFIXME\b", "unresolved placeholder"),
    ("release", r"\[(?:CITATION|EVIDENCE) NEEDED\]", "unresolved evidence/citation placeholder"),
    ("review", r"\b(?:proves?|causes?|drives?|determines?)\b", "strong causal/evidentiary verb; verify support"),
    ("style", r"\bit (?:is important|is worth|should be) (?:to )?note(?:d)? that\b", "stock metadiscourse"),
    ("style", r"\b(?:sheds? light on|underscor(?:e|es|ed|ing) (?:the )?(?:importance|role)|highlights? the need for|paves? the way)\b", "generic significance phrase"),
    ("style", r"\b(?:Interestingly|Notably|Importantly|Taken together)\b", "stock emphasis/signposting; verify it adds information"),
    ("style", r"\bdue to the fact that\b|\bin order to\b", "wordy construction"),
]

def lineno(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1

def lint(text: str, suffix: str = "") -> list[dict]:
    out = []
    for severity, pattern, message in RULES:
        for m in re.finditer(pattern, text, flags=re.I):
            out.append({"severity": severity, "line": lineno(text, m.start()),
                        "message": message, "match": m.group(0)})
    for m in re.finditer(r"\b([A-Za-z]{2,})\s+\1\b", text, flags=re.I):
        out.append({"severity":"mechanical","line":lineno(text,m.start()),
                    "message":"duplicate consecutive word","match":m.group(0)})
    if suffix.lower() == ".tex":
        labels = set(re.findall(r"\\label\{([^}]+)\}", text))
        refs = set(re.findall(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", text))
        for missing in sorted(refs - labels):
            out.append({"severity":"release","line":0,
                        "message":f"LaTeX reference has no matching label in this file: {missing}",
                        "match":missing})
    return sorted(out, key=lambda x:(x["line"],x["severity"],x["message"]))

def self_test() -> int:
    s = "It is important to note that this proves proves X. [CITATION NEEDED]"
    msgs = {x["message"] for x in lint(s)}
    need = {"stock metadiscourse","strong causal/evidentiary verb; verify support",
            "duplicate consecutive word","unresolved evidence/citation placeholder"}
    missing = need - msgs
    if missing:
        print("Self-test failed:", sorted(missing)); return 1
    print("lint self-test OK"); return 0

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("file", nargs="?", type=Path)
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test: return self_test()
    if a.file is None: p.error("file is required unless --self-test is used")
    issues = lint(a.file.read_text(encoding="utf-8"), a.file.suffix)
    if a.json:
        print(json.dumps(issues, indent=2))
    elif not issues:
        print("No mechanical/style flags found.")
    else:
        for x in issues:
            where = f"line {x['line']}" if x["line"] else "document"
            print(f"[{x['severity']}] {where}: {x['message']} ({x['match']!r})")
        print(f"\n{len(issues)} flag(s). Review; do not auto-fix blindly.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
