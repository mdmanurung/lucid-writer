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
    ("style", r"\bnot (?:only|just|merely|simply)\b[^.;]{0,80}?\bbut(?: also)?\b", "contrast against a claim no one made; state the point"),
    ("style", r"\b(?:serves?|serving|stands?) as (?:a|an|the)\b|\bboasts?\b", "inflated verb; try 'is' or 'has'"),
    ("style", r",\s*(?:highlighting|underscoring|emphasi[sz]ing|reflecting|showcasing)\b", "-ing rider; check it does not upgrade the claim"),
    ("review", r"\b(?:(?:previous|prior|recent|several|many|numerous) )?studies (?:have )?(?:shown|demonstrated|suggested)\b(?![^.]{0,60}(?:\[\d|\[@|\(\w[^)]*\d{4}|\\cite))|\bit is (?:well[- ]established|widely accepted|believed) that\b", "unattributed authority; cite or mark [CITATION NEEDED]"),
    ("release", r"\b(?:I hope this helps|let me know if|here is (?:a|the) (?:revised|rewritten|tightened)|as an AI\b|as of my (?:last|knowledge))", "chat residue; remove"),
]

EM_DASH_PER_1000_WORDS = 5  # above this, em dashes are a default connector, not a choice

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
    words = max(len(text.split()), 1)
    dashes = text.count("\u2014")
    if dashes >= 3 and dashes * 1000 / words > EM_DASH_PER_1000_WORDS:
        out.append({"severity":"style","line":0,
                    "message":f"{dashes} em dashes in {words} words; replace those that only connect clauses",
                    "match":"\u2014"})
    if suffix.lower() == ".tex":
        labels = set(re.findall(r"\\label\{([^}]+)\}", text))
        refs = set(re.findall(r"\\(?:ref|eqref|autoref)\{([^}]+)\}", text))
        for missing in sorted(refs - labels):
            out.append({"severity":"release","line":0,
                        "message":f"LaTeX reference has no matching label in this file: {missing}",
                        "match":missing})
    return sorted(out, key=lambda x:(x["line"],x["severity"],x["message"]))

def self_test() -> int:
    s = ("It is important to note that this proves proves X. [CITATION NEEDED] "
         "This is not only a marker but also a target. The cohort serves as a model, "
         "IL-10 rose, highlighting its role. Previous studies have shown that X binds Y. "
         "I hope this helps. A \u2014 B \u2014 C \u2014 D.")
    msgs = {x["message"] for x in lint(s)}
    need = {"stock metadiscourse","strong causal/evidentiary verb; verify support",
            "duplicate consecutive word","unresolved evidence/citation placeholder",
            "contrast against a claim no one made; state the point",
            "inflated verb; try 'is' or 'has'",
            "-ing rider; check it does not upgrade the claim",
            "unattributed authority; cite or mark [CITATION NEEDED]",
            "chat residue; remove"}
    missing = need - msgs
    if not any("em dashes in" in m for m in msgs):
        missing.add("em dash density")
    # A cited study and a numeric range are not flags.
    quiet = lint("Previous studies have shown that X binds Y [12]. Studies have shown "
                 "that Y binds Z [@smith2020]. The CI was 0.55\u20130.95.")
    if quiet:
        missing.add("false positive: " + quiet[0]["message"])
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
    issues = lint(a.file.read_text(encoding="utf-8", errors="replace"), a.file.suffix)
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
