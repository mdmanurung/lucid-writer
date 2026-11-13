#!/usr/bin/env python3
"""Sample labelled sentence pairs from two public corpora at run time.

Neither corpus has a clear data licence (see README.md), so this repository holds the
sampler and never the data. Output goes to bench/external/sample/, which is gitignored.

    python3 bench/external/sample_pairs.py exaggeration [--n 20] [--seed 20261113] [--split test]
    python3 bench/external/sample_pairs.py causal       [--n 20] [--seed 20261113]
    python3 bench/external/sample_pairs.py --self-test

Python standard library only. Needs network access for the two sampling commands.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "sample"

# copenlu/scientific-exaggeration-detection: one row is a pair (abstract conclusion, press
# release conclusion). Both strength labels use the same scheme (dataset card, "Dataset Structure").
HF_ROWS = "https://datasets-server.huggingface.co/rows"
HF_DATASET = "copenlu/scientific-exaggeration-detection"
# Yu, Li and Wang (2019): one CSV with columns "sentence,label".
YU_CSV = ("https://raw.githubusercontent.com/junwang4/causal-language-use-in-science/"
          "refs/heads/master/data/pubmed_causal_language_use.csv")

# Label -> lucid-writer ceiling vocabulary. A label measures the strength of a sentence's
# language; a ceiling measures what evidence allows. The mapping gives the lowest ceiling
# the wording would need. Label 0 in both corpora holds sentences that claim no relation
# (null findings, plain descriptions, projections, background), so it maps to DESCRIPTIVE,
# the floor of the vocabulary. `sure` is False where the mapping is a judgement. See
# README.md for the sources and for what the label-0 rows contain.
#
# A causal verb under a hedge still needs a CAUSAL ceiling (references/evidence.md,
# "Common unsafe upgrades"), so the conditional classes map to CAUSAL.
EXAGGERATION_MAP = {
    0: ("DESCRIPTIVE", True),   # "Statement of no relationship": 185 rows read; null findings and descriptions
    1: ("ASSOCIATIVE", True),   # "Statement of correlation"
    2: ("CAUSAL", True),        # "Conditional statement of causation"
    3: ("CAUSAL", True),        # "Statement of causation"
}
# Yu et al. number the same four classes in a different order (label order from the repo
# README; the paper gives names and definitions, not numbers). Definitions: Table 1 of the
# paper, quoted in README.md.
YU_MAP = {
    0: ("DESCRIPTIVE", True),   # "No correlation or causation relationship is mentioned"
    1: ("CAUSAL", True),        # Direct causal: the independent variable directly alters the dependent
    2: ("CAUSAL", True),        # Conditional causal: directly changes it, with doubt via hedges
    3: ("ASSOCIATIVE", True),   # Correlational: association, causation cannot be explicitly stated
}


def fetch(url: str, attempts: int = 4) -> bytes:
    """GET with a short backoff on server errors; exits with one line if the download fails."""
    request = urllib.request.Request(url, headers={"User-Agent": "lucid-writer-bench"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            failure = exc
            if exc.code < 500:
                break
        except urllib.error.URLError as exc:
            failure = exc
        if attempt < attempts:
            time.sleep(2 * attempt)
    sys.exit(f"download failed for {url}: {failure}")


def hf_rows(split: str) -> list[dict]:
    """All rows of one split. split "all" reads train and test."""
    if split == "all":
        return hf_rows("train") + hf_rows("test")
    rows, offset = [], 0
    while True:
        query = urllib.parse.urlencode({
            "dataset": HF_DATASET, "config": "default", "split": split,
            "offset": offset, "length": 100,
        })
        page = json.loads(fetch(f"{HF_ROWS}?{query}"))
        rows += [r["row"] for r in page["rows"]]
        offset += len(page["rows"])
        if not page["rows"] or offset >= page["num_rows_total"]:
            return rows


def stratified(rows: list[dict], key: str, n: int, seed: int) -> list[dict]:
    """n rows (fewer only if the data has fewer), spread evenly over the values of `key`.

    Rounds hand out one row per stratum in turn, starting at a stratum chosen by the seed, so
    a small stratum never shrinks the sample and no label is always the short one."""
    if n < 0:
        raise ValueError("n must not be negative")
    rng = random.Random(seed)
    groups: dict = {}
    for row in rows:
        groups.setdefault(row[key], []).append(row)
    values = sorted(groups, key=str)
    for v in values:
        rng.shuffle(groups[v])
    start = rng.randrange(len(values)) if values else 0
    order = values[start:] + values[:start]
    picked: list[dict] = []
    taken = {v: 0 for v in values}
    while len(picked) < min(n, len(rows)):
        for v in order:
            if len(picked) < n and taken[v] < len(groups[v]):
                picked.append(groups[v][taken[v]])
                taken[v] += 1
    return picked


def derived_exaggeration(abstract: int, press: int) -> str:
    return "same" if abstract == press else "exaggerates" if press > abstract else "downplays"


def exaggeration_pairs(rows: list[dict], n: int, seed: int) -> list[dict]:
    out = []
    for r in stratified(rows, "exaggeration_label", n, seed):
        a, p = r["abstract_strength"], r["press_release_strength"]
        out.append({
            "source": r["abstract_conclusion"], "derived": r["press_release_conclusion"],
            "source_label": a, "derived_label": p,
            "source_ceiling": EXAGGERATION_MAP[a][0], "derived_ceiling": EXAGGERATION_MAP[p][0],
            "mapping_sure": EXAGGERATION_MAP[a][1] and EXAGGERATION_MAP[p][1],
            "dataset_exaggeration_label": r["exaggeration_label"],
            # The card does not say how exaggeration_label follows from the two strengths.
            # This column is a check on that, not a replacement for it.
            "label_from_strengths": derived_exaggeration(a, p),
            "original_file_id": r.get("original_file_id"),
        })
    return out


def causal_sentences(rows: list[dict], n: int, seed: int) -> list[dict]:
    return [{
        "sentence": r["sentence"], "label": int(r["label"]),
        "ceiling": YU_MAP[int(r["label"])][0], "mapping_sure": YU_MAP[int(r["label"])][1],
    } for r in stratified(rows, "label", n, seed)]


def write(name: str, items: list[dict], wanted: int) -> None:
    if len(items) < wanted:
        print(f"warning: wrote {len(items)} items, fewer than the {wanted} asked for; "
              "the data has no more rows", file=sys.stderr)
    OUT.mkdir(exist_ok=True)
    path = OUT / name
    path.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8")
    print(f"wrote {len(items)} items -> {path}")


def self_test() -> int:
    rows = [{"exaggeration_label": lab, "abstract_strength": a, "press_release_strength": p,
             "abstract_conclusion": f"a{i}", "press_release_conclusion": f"p{i}", "original_file_id": str(i)}
            for i, (lab, a, p) in enumerate(
                [("same", 1, 1)] * 6 + [("exaggerates", 1, 3)] * 6 + [("downplays", 3, 1)] * 6)]
    pairs = exaggeration_pairs(rows, 6, seed=1)
    assert len(pairs) == 6 and pairs == exaggeration_pairs(rows, 6, seed=1)
    assert sorted(p["dataset_exaggeration_label"] for p in pairs) == ["downplays"] * 2 + ["exaggerates"] * 2 + ["same"] * 2
    small = [{"k": "a"}] * 3 + [{"k": "b"}] * 50
    assert len(stratified(small, "k", 20, 1)) == 20, "a small stratum must not shrink the sample"
    assert len(stratified(small, "k", 100, 1)) == 53 and stratified(small, "k", 0, 1) == []
    # The remainder rotates with the seed: over many seeds each label is sometimes the short one.
    short_label = {min("abc", key=lambda c: sum(r["k"] == c for r in stratified([{"k": x} for x in "abc" for _ in range(9)], "k", 5, seed)))
                   for seed in range(30)}
    assert len(short_label) > 1, short_label
    counts = {c: sum(r["k"] == c for r in stratified([{"k": c} for c in "abc" for _ in range(9)], "k", 5, 7)) for c in "abc"}
    assert sorted(counts.values()) == [1, 2, 2], counts
    assert all(p["dataset_exaggeration_label"] == p["label_from_strengths"] for p in pairs)
    assert pairs[0]["source_ceiling"] in {"ASSOCIATIVE", "CAUSAL"}
    text = "sentence,label\nIt rose.,0\nX causes Y.,1\nX may cause Y.,2\nX tracks Y.,3\n" * 3
    sents = causal_sentences(list(csv.DictReader(io.StringIO(text))), 4, seed=1)
    assert sorted(s["label"] for s in sents) == [0, 1, 2, 3]
    assert {s["label"]: s["ceiling"] for s in sents}[3] == "ASSOCIATIVE"
    assert {s["label"]: s["ceiling"] for s in sents}[0] == "DESCRIPTIVE"
    assert derived_exaggeration(1, 3) == "exaggerates" and derived_exaggeration(3, 1) == "downplays"
    print("sample_pairs self-test OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("corpus", nargs="?", choices=["exaggeration", "causal"])
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20261113)
    parser.add_argument("--split", choices=["test", "train", "all"], default="test",
                        help="exaggeration corpus only; the paper tests on `test` (default)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.corpus is None:
        parser.error("corpus is required unless --self-test is used")
    if args.n < 0:
        parser.error("--n must not be negative")
    if args.corpus == "exaggeration":
        write("exaggeration_pairs.jsonl", exaggeration_pairs(hf_rows(args.split), args.n, args.seed), args.n)
    else:
        rows = list(csv.DictReader(io.StringIO(fetch(YU_CSV).decode("utf-8"))))
        write("causal_sentences.jsonl", causal_sentences(rows, args.n, args.seed), args.n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
