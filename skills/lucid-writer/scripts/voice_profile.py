#!/usr/bin/env python3
"""Draft .lucid-writer/voice.md from sample texts. Fills measured fields only."""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

MAX_CHARS = 4000          # hooks/lib.js truncates voice.md at this length
SAMPLE_MAX_CHARS = 300    # longer sentences make poor samples
SAMPLE_MIN_WORDS = 8
DOTTED = ("et al.", "e.g.", "i.e.", "vs.", "Fig.", "Figs.", "Eq.", "Ref.", "cf.", "approx.")

WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")
HEDGES = "hedges (may/might/likely/perhaps/suggest*)"
SIGNPOSTS = "signposts (notably/interestingly/importantly/furthermore/moreover/collectively/taken together)"
TERMS = {
    "we": r"we",
    HEDGES: r"may|might|likely|perhaps|suggest\w*",
    SIGNPOSTS: r"notably|interestingly|importantly|furthermore|moreover|collectively|taken together",
    "however": r"however",
    "therefore": r"therefore",
    "thus": r"thus",
    "also": r"also",
}
REF_HEAD = r"(?im)^\s*(?:#+\s*)?(?:references|bibliography|works cited|literature cited)\s*:?\s*$"


def clean(text):
    """Drop code, reference lists, headings, bracketed and author-year citations."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.split(REF_HEAD, text)[0]
    text = re.sub(r"(?m)^\s*#+\s.*$", " ", text)
    text = re.sub(r"\[@[^\]]*\]|\[\d+(?:\s*[-,–]\s*\d+)*\]", "", text)
    text = re.sub(r"\([^()]*?[A-Z][a-z]+(?: et al\.)?,? \(?(?:19|20)\d\d[a-z]?[^()]*\)", "", text)
    return re.sub(r"[ \t]+", " ", text)


def split_sentences(text):
    for i, d in enumerate(DOTTED):
        text = text.replace(d, d.replace(".", f"@{i}@"))
    text = re.sub(r"\s*\n\s*", " ", text)
    parts = re.split(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]?[A-Z])", text)
    out = []
    for p in parts:
        p = re.sub(r"@\d+@", ".", p).strip()
        if len(WORD.findall(p)) >= 3:
            out.append(p)
    return out


def percentile(sorted_vals, q):
    k = (len(sorted_vals) - 1) * q
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def rate(count, words):
    return round(1000.0 * count / words, 1) if words else 0.0


def measure(text):
    sents = split_sentences(clean(text))
    body = " ".join(sents)
    words = len(WORD.findall(body))
    lens = sorted(len(WORD.findall(s)) for s in sents)
    m = {"sentences": len(sents), "words": words}
    if not sents:
        return m, sents
    m["len"] = tuple(round(percentile(lens, q), 1) for q in (0.5, 0.1, 0.9))
    m["rates"] = {
        "semicolons": rate(body.count(";"), words),
        "parentheses": rate(body.count("("), words),
        "em dashes": rate(body.count("—"), words),
        "questions": rate(sum(s.endswith("?") for s in sents), words),
    }
    for name, pat in TERMS.items():
        m["rates"][name] = rate(len(re.findall(rf"\b(?:{pat})\b", body, flags=re.I)), words)
    openers = Counter(WORD.findall(s)[0].lower() for s in sents)
    m["openers"] = sorted(openers.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
    return m, sents


def pick_samples(sents, median, n=6):
    """Closest to the median length; ties break alphabetically. Shown in text order."""
    ok = [
        s for s in dict.fromkeys(sents)
        if len(s) <= SAMPLE_MAX_CHARS and len(WORD.findall(s)) >= SAMPLE_MIN_WORDS
    ]
    ranked = sorted(ok, key=lambda s: (abs(len(WORD.findall(s)) - median), s))[:n]
    return [s for s in dict.fromkeys(sents) if s in ranked]


def render(m, samples, author, position, sources):
    who = author or "unnamed author"
    where = f"; author position: {position}" if position else ""
    out = [f"# Voice profile: {who}", "",
           "Measured from the sample texts. Evidence and genre rules override voice.", ""]
    if position == "other":
        out += [f"WARNING: {who} is not first or sole author of these texts. "
                "They may reflect co-authors' voice.", ""]
    out += [f"Sources: {', '.join(sources)} ({m['sentences']} sentences, {m['words']} words{where})", ""]
    med, p10, p90 = m["len"]
    out += ["## Desired register",
            f"- Sentence length (words): median {med:g}, 10th percentile {p10:g}, 90th percentile {p90:g}",
            "- Rates per 1,000 words:"]
    out += [f"  - {k}: {v:g}" for k, v in m["rates"].items()]
    out += ["- Top sentence openers: " + ", ".join(f"{w} ({c})" for w, c in m["openers"]),
            "- Tone, formality, paragraph length: [author to fill]", "",
            "## Prefer", "- [author to fill: habits to keep]", "",
            "## Avoid", "- [author to fill: habits to drop]", "",
            "## Terminology conventions", "- [author to fill]", "",
            "## Representative writing samples",
            "Verbatim sentences of near-median length, chosen by rule.", ""]
    for i, s in enumerate(samples, 1):
        out += [f"### Sample {i}", s, ""]
    return "\n".join(out)


def build(texts, author, position, sources):
    m, sents = measure("\n\n".join(texts))
    if not sents:
        raise ValueError("no sentences found after stripping references and citations")
    samples = pick_samples(sents, m["len"][0])
    doc = render(m, samples, author, position, sources)
    while len(doc) > MAX_CHARS and len(samples) > 4:
        samples.pop()
        doc = render(m, samples, author, position, sources)
    return doc.rstrip() + "\n"


def self_test():
    text = (
        "We measured growth in three lines. We may see a change; it is small (n = 3). "
        "However, the effect is likely real [1]. Taken together, we suggest a link (Smith et al., 2020). "
        "Is the result robust to the choice of filter? Also, the result holds in Fig. 2 and in the second batch.\n\n"
        "References\n\n1. Smith J. A long entry that must be ignored. We may not count.\n"
    )
    m, sents = measure(text)
    # Hand count: 6 sentences of 6, 9, 6, 6, 9, 11 words = 47 words.
    assert m["sentences"] == 6 and m["words"] == 47, (m, sents)
    assert m["len"] == (7.5, 6.0, 10.0), m["len"]
    r = m["rates"]
    assert r["semicolons"] == r["parentheses"] == r["questions"] == rate(1, 47), r
    assert r["we"] == r[HEDGES] == rate(3, 47), r
    assert r[SIGNPOSTS] == r["however"] == r["also"] == rate(1, 47), r
    assert r["em dashes"] == r["thus"] == 0.0, r
    assert m["openers"][0] == ("we", 2), m["openers"]
    doc = build([text], "A. Author", "other", ["demo.md"])
    assert "WARNING" in doc and "Voice profile: A. Author" in doc and len(doc) < MAX_CHARS
    assert doc == build([text], "A. Author", "other", ["demo.md"])
    assert all(s in text for s in re.findall(r"### Sample \d+\n(.+)", doc)), "samples must be verbatim"
    print("voice_profile self-test OK")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("files", nargs="*", help="text or markdown files")
    p.add_argument("--author", help="author name for the profile title")
    p.add_argument("--author-position", choices=["sole", "first", "other"],
                   help="author position in the sample papers; 'other' adds a warning")
    p.add_argument("--out", help="write to this file (default: stdout)")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.files:
        p.error("give at least one file, or use --self-test")
    texts = [Path(f).read_text(encoding="utf-8", errors="replace") for f in a.files]
    doc = build(texts, a.author, a.author_position, [Path(f).name for f in a.files])
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(doc, encoding="utf-8")
        print(f"Wrote {a.out} ({len(doc)} characters). Fill the [author to fill] fields.", file=sys.stderr)
    else:
        sys.stdout.write(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
