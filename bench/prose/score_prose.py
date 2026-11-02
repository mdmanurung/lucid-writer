#!/usr/bin/env python3
"""Score the prose-rewrite pilot: the mechanical layer, plus packets for a blinded judge.

For every run under the run tree this checks, against gold.yaml:
  - kept: every must_keep token (number, unit, citation key) still present;
  - reduction: words cut relative to the original paragraph (the prompt asked for ~20%);
  - cues: phrases that usually signal the tempted overclaim (a screen, not the verdict);
  - skill_loaded: from acumen's result.json.

It also writes judge_packets.jsonl (original, gold claims, rewrite; no arm, no model) and
judge_key.jsonl (packet id -> arm, model, run). Give the judge only the packets.

Usage:
    uv run --quiet --no-project --with pyyaml bench/prose/score_prose.py [RUNS] [--out DIR]
    uv run --quiet --no-project --with pyyaml bench/prose/score_prose.py --self-test
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("score_prose.py needs PyYAML: uv run --with pyyaml bench/prose/score_prose.py")

HERE = Path(__file__).resolve().parent
DASHES = str.maketrans({"−": "-", "–": "-", "—": "-", "‐": "-", "‑": "-"})


def normalise(text: str) -> str:
    return text.translate(DASHES)


def has_token(text: str, token: str) -> bool:
    """A number matches only as a whole number: "6" is in "n = 6" but not in "16" or "0.6"."""
    text, token = normalise(text), normalise(token)
    if re.fullmatch(r"[\d.]+", token):
        return re.search(rf"(?<![\d.]){re.escape(token)}(?![\d]|\.\d)", text) is not None
    return token in text


def original_paragraph(prompt: str) -> str:
    """The paragraph to rewrite is the prompt's last block, after the instruction."""
    return prompt.strip().split("\n\n")[-1].strip()


def score_run(answer: str, original: str, gold: dict) -> dict:
    words_in, words_out = len(original.split()), len(answer.split())
    low = normalise(answer).lower()
    return {
        "missing": [t for t in gold["must_keep"] if not has_token(answer, t)],
        "reduction_pct": round(100 * (1 - words_out / words_in)) if words_in else 0,
        "cue_hits": [c for c in gold.get("cues", []) if c in low],
    }


def chat_answer(transcript: Path) -> str | None:
    """A run that put its rewrite in chat instead of answer.md: the final message's first paragraph."""
    if not transcript.is_file():
        return None
    last = None
    for line in transcript.read_text(encoding="utf-8").splitlines():
        msg = json.loads(line)
        if msg.get("type") == "assistant":
            texts = [c["text"] for c in msg["message"]["content"] if c.get("type") == "text"]
            last = texts[-1] if texts else last
    return last.strip().split("\n\n")[0].strip() if last else None


def collect(runs: Path) -> list[dict]:
    out = []
    for result_path in sorted(runs.glob("*/*/*/*/rep_*/result.json")):
        arm, split, model, task, rep = result_path.parts[-6:-1]
        answer = result_path.with_name("answer.md")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        text = answer.read_text(encoding="utf-8").strip() if answer.is_file() else None
        recovered = text is None and (text := chat_answer(result_path.with_name("transcript.jsonl"))) is not None
        out.append({
            "arm": arm, "split": split, "model": model, "task": task, "rep": rep,
            "answer": text, "recovered": recovered,
            "skill_loaded": data.get("skill_loaded"),
        })
    return out


def self_test() -> int:
    assert has_token("n = 6 replicates", "6")
    assert not has_token("16 replicates", "6") and not has_token("0.6 points", "6")
    assert has_token("95% CI −4 to 21%", "4")          # Unicode minus
    assert has_token("CI 2–12", "2") and has_token("CI 2–12", "12")  # en dash
    assert not has_token("2006", "2")
    assert has_token("p = 0.17.", "0.17")                   # sentence-final period
    assert has_token("(Lindqvist et al., 2020)", "Lindqvist et al., 2020")
    gold = {"must_keep": ["38", "9"], "cues": ["no effect"]}
    s = score_run("GENE2 had no effect; GENE1 cut colonies by 38%.", "a b c d e f g h i j", gold)
    assert s["missing"] == ["9"] and s["cue_hits"] == ["no effect"], s
    assert original_paragraph("Tighten this.\n\nPara one.") == "Para one."
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tr = Path(d) / "transcript.jsonl"
        msg = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Rewrite.\n\n**Changes:** x"}]}}
        tr.write_text(json.dumps(msg) + "\n", encoding="utf-8")
        assert chat_answer(tr) == "Rewrite.", chat_answer(tr)
    print("score_prose self-test OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="?", type=Path, default=HERE / "runs")
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    tasks = yaml.safe_load((HERE / "tasks.yaml").read_text(encoding="utf-8"))["tasks"]
    originals = {f"{t['id']}/{s}": original_paragraph(t[s]["prompt"]) for t in tasks for s in ("train", "valid", "test")}
    gold = yaml.safe_load((HERE / "gold.yaml").read_text(encoding="utf-8"))["items"]
    if set(gold) != set(originals):
        sys.exit(f"gold.yaml items {sorted(gold)} do not match tasks.yaml {sorted(originals)}")

    runs = collect(args.runs)
    if not runs:
        sys.exit(f"no runs under {args.runs}: run acumen bench with --tasks prose/tasks.yaml --runs prose/runs")

    print(f"{'arm':9s} {'model':18s} {'item':24s} {'rep':5s} {'loaded':6s} {'cut%':>4s}  missing / cues")
    packets, key = [], []
    for run in runs:
        item = f"{run['task']}/{run['split']}"
        if run["answer"] is None:
            print(f"{run['arm']:9s} {run['model']:18s} {item:24s} {run['rep']:5s} no answer file")
            continue
        s = score_run(run["answer"], originals[item], gold[item])
        flags = (f"missing {s['missing']}" if s["missing"] else "") + (f" cues {s['cue_hits']}" if s["cue_hits"] else "")
        print(f"{run['arm']:9s} {run['model']:18s} {item:24s} {run['rep']:5s} {str(run['skill_loaded']):6s} {s['reduction_pct']:>4d}  {flags or 'ok'}{' (recovered from chat)' if run['recovered'] else ''}")
        packets.append({"item": item, "original": originals[item], "claims": gold[item]["claims"], "rewrite": run["answer"]})
        key.append({k: run[k] for k in ("arm", "model", "task", "split", "rep")})

    # Blinding: shuffle packets and number them; the key maps numbers back to arms.
    order = list(range(len(packets)))
    random.Random(20261102).shuffle(order)
    with (args.out / "judge_packets.jsonl").open("w", encoding="utf-8") as fp, \
         (args.out / "judge_key.jsonl").open("w", encoding="utf-8") as fk:
        for pid, i in enumerate(order, start=1):
            fp.write(json.dumps({"id": pid, **packets[i]}, ensure_ascii=False) + "\n")
            fk.write(json.dumps({"id": pid, **key[i]}) + "\n")
    print(f"\n{len(packets)} judge packets -> {args.out / 'judge_packets.jsonl'} (key: judge_key.jsonl)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
