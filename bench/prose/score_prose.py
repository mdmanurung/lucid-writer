#!/usr/bin/env python3
"""Score the prose-rewrite pilot: the mechanical layer, plus packets for a blinded judge.

For every run under the run tree this checks, against gold.yaml:
  - kept: every must_keep token (number, unit, citation key) still present;
  - reduction: words cut relative to the original paragraph (the prompt asked for ~20%);
  - cues: phrases that usually signal the tempted overclaim (a screen, not the verdict);
  - qualifiers: the fraction of gold must_keep_qualifiers still present (mechanical);
  - over-hedge cues: phrases that signal needless weakening (a screen, not the verdict);
  - skill_loaded: from acumen's result.json.

After the per-run table it prints summaries by arm and skill_loaded, and per item
(paragraph x split) so repeated runs of one prompt count once. With judgements.jsonl
beside the packets it adds the judge's `above` and `below` counts.

It also writes judge_packets.jsonl (original, gold claims, rewrite; no arm, no model) and
judge_key.jsonl (packet id -> arm, model, run). Give the judge only the packets.

Usage:
    uv run --quiet --no-project --with pyyaml bench/prose/score_prose.py [RUNS ...] [--out DIR]

A RUNS directory whose name ends in "-forced" (prose/runs-forced) is labelled "<arm>+forced".
    uv run --quiet --no-project --with pyyaml bench/prose/score_prose.py --self-test
"""

from __future__ import annotations

import argparse
import importlib.util
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
QUALIFIER_CHECK = HERE.parents[1] / "skills" / "lucid-writer" / "scripts" / "qualifier_check.py"
DASHES = str.maketrans({"−": "-", "–": "-", "—": "-", "‐": "-", "‑": "-"})


def normalise(text: str) -> str:
    return text.translate(DASHES)


def has_token(text: str, token: str) -> bool:
    """A number matches only as a whole number: "6" is in "n = 6" but not in "16" or "0.6"."""
    text, token = normalise(text), normalise(token)
    if re.fullmatch(r"[\d.]+", token):
        text = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", text)  # 1,180 matches the token 1180
        return re.search(rf"(?<![\d.]){re.escape(token)}(?![\d]|\.\d)", text) is not None
    return token in text


def _phrase_regex():
    """Reuse qualifier_check's whole-phrase matching so both tools treat dashes and case alike."""
    spec = importlib.util.spec_from_file_location("qualifier_check", QUALIFIER_CHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.normalise, module.phrase_regex


def qualifiers_kept(answer: str, entries: list) -> tuple[int, list]:
    """Count gold qualifier entries present in the answer. An entry is a phrase or a list of
    interchangeable phrases; one match keeps it. Returns (kept, dropped entries)."""
    normalise_q, phrase_regex = _phrase_regex()
    text = normalise_q(answer)
    dropped = []
    for entry in entries:
        options = [entry] if isinstance(entry, str) else entry
        if not any(phrase_regex(o).search(text) for o in options):
            dropped.append(entry if isinstance(entry, str) else entry[0])
    return len(entries) - len(dropped), dropped


def original_paragraph(prompt: str) -> str:
    """The paragraph to rewrite is the prompt's last block, after the instruction."""
    return prompt.strip().split("\n\n")[-1].strip()


def score_run(answer: str, original: str, gold: dict) -> dict:
    words_in, words_out = len(original.split()), len(answer.split())
    low = normalise(answer).lower()
    entries = gold.get("must_keep_qualifiers", [])
    kept, dropped = qualifiers_kept(answer, entries) if entries else (0, [])
    return {
        "missing": [t for t in gold["must_keep"] if not has_token(answer, t)],
        "reduction_pct": round(100 * (1 - words_out / words_in)) if words_in else 0,
        "cue_hits": [c for c in gold.get("cues", []) if c in low],
        "q_total": len(entries),
        "q_kept": kept,
        "q_dropped": dropped,
        "over_hedge_hits": [c for c in gold.get("over_hedge_cues", []) if c in low],
    }


VERDICTS = {"below", "at", "above", "missing"}


def parse_judgements(text: str, claims_per_packet: dict[int, int]) -> dict[int, list[str]]:
    """Read judgements.jsonl and check it against the packets. Raises ValueError on a wrong
    verdict, wrong list length, unknown or duplicate id, or a packet nobody judged."""
    verdicts: dict[int, list[str]] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            pid, vs = row["id"], row["verdicts"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ValueError(f"judgements.jsonl line {line_no}: not a JSON object with id and verdicts ({exc})")
        if pid not in claims_per_packet:
            raise ValueError(f"judgements.jsonl line {line_no}: id {pid} is not a packet id")
        if pid in verdicts:
            raise ValueError(f"judgements.jsonl line {line_no}: duplicate id {pid}")
        if len(vs) != claims_per_packet[pid]:
            raise ValueError(f"judgements.jsonl line {line_no}: packet {pid} has "
                             f"{claims_per_packet[pid]} claims but {len(vs)} verdicts")
        bad = [v for v in vs if v not in VERDICTS]
        if bad:
            raise ValueError(f"judgements.jsonl line {line_no}: invalid verdicts {bad}; use {sorted(VERDICTS)}")
        verdicts[pid] = vs
    missing = sorted(set(claims_per_packet) - set(verdicts))
    if missing:
        raise ValueError(f"judgements.jsonl has no verdict for packet ids {missing}; judge every packet "
                         "(judge_packets.jsonl is rebuilt on every run, so judge after the last run)")
    return verdicts


def pct(num: int, den: int) -> str:
    return f"{100 * num / den:.0f}%" if den else "n/a"


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def fmt(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "n/a"


def summarise(rows: list[dict]) -> list[str]:
    """Summary lines from scored runs. Each row has arm, model, item, loaded, q_total,
    q_dropped and, when judged, verdicts (a list of below/at/above/missing)."""
    lines = ["", "qualifier retention by arm and skill_loaded (mean fraction kept, runs)"]
    groups: dict[tuple, list[dict]] = {}
    for r in rows:
        if r["q_total"]:
            loaded = {True: "true", False: "false"}.get(r["loaded"], "unknown")
            groups.setdefault((r["arm"], loaded), []).append(r)
    for (arm, loaded), rs in sorted(groups.items()):
        kept = mean([1 - len(r["q_dropped"]) / r["q_total"] for r in rs])
        lines.append(f"  {arm:14s} skill_loaded={loaded:8s} {fmt(kept)}  ({len(rs)} runs)")

    judged = any("verdicts" in r for r in rows)
    lines += ["", "per item (paragraph x split): runs pooled over models and replicates; "
              "fraction of runs with at least one dropped qualifier"
              + (", one claim `above`, one claim `below`" if judged else "")]
    by_item: dict[tuple, list[dict]] = {}
    for r in rows:
        by_item.setdefault((r["arm"], r["item"]), []).append(r)
    arm_items: dict[str, list[dict]] = {}
    for (arm, item), rs in sorted(by_item.items()):
        n = len(rs)
        entry = {"drop": sum(bool(r["q_dropped"]) for r in rs) / n}
        text = f"  {arm:14s} {item:24s} n={n:<3d} dropped {fmt(entry['drop'])}"
        if judged:
            js = [r for r in rs if "verdicts" in r]
            if js:
                entry["above"] = sum("above" in r["verdicts"] for r in js) / len(js)
                entry["below"] = sum("below" in r["verdicts"] for r in js) / len(js)
                text += f"  above {fmt(entry['above'])}  below {fmt(entry['below'])}  (judged {len(js)})"
        lines.append(text)
        arm_items.setdefault(arm, []).append(entry)

    lines += ["", "per arm, items as the unit (mean of the item fractions)"]
    for arm, items in sorted(arm_items.items()):
        text = f"  {arm:14s} {len(items)} items  dropped {fmt(mean([i['drop'] for i in items]))}"
        for key in ("above", "below"):
            vals = [i[key] for i in items if key in i]
            if vals:
                text += f"  {key} {fmt(mean(vals))}"
        lines.append(text)

    if judged:
        lines += ["", "claim level, for comparison with earlier reports (claims are not independent)"]
        for arm in sorted({r["arm"] for r in rows}):
            vs = [v for r in rows if r["arm"] == arm and "verdicts" in r for v in r["verdicts"]]
            lines.append(f"  {arm:14s} above {sum(v == 'above' for v in vs)}/{len(vs)}  "
                         f"below {sum(v == 'below' for v in vs)}/{len(vs)}")
    return lines


def chat_answer(transcript: Path) -> str | None:
    """A run that put its rewrite in chat instead of answer.md: the final message's first paragraph."""
    if not transcript.is_file():
        return None
    last = None
    for line in transcript.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "assistant":
            content = msg["message"]["content"]
            if isinstance(content, str):
                texts = [content]
            else:
                texts = [c["text"] for c in content if c.get("type") == "text"]
            last = texts[-1] if texts else last
    return last.strip().split("\n\n")[0].strip() if last else None


def collect(runs: Path) -> list[dict]:
    suffix = "+forced" if runs.name.endswith("-forced") else ""
    out = []
    for result_path in sorted(runs.glob("*/*/*/*/rep_*/result.json")):
        arm, split, model, task, rep = result_path.parts[-6:-1]
        answer = result_path.with_name("answer.md")
        data = json.loads(result_path.read_text(encoding="utf-8"))
        text = (answer.read_text(encoding="utf-8").strip() or None) if answer.is_file() else None
        recovered = text is None and (text := chat_answer(result_path.with_name("transcript.jsonl"))) is not None
        out.append({
            "arm": arm + suffix, "split": split, "model": model, "task": task, "rep": rep,
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
    assert has_token("Of 1,180 households", "1180") and not has_token("1,1800 households", "1180")
    assert has_token("n = 1,180", "180") is False                   # thousands comma is not a decimal point
    assert has_token("p = 0.17.", "0.17")                   # sentence-final period
    assert has_token("(Lindqvist et al., 2020)", "Lindqvist et al., 2020")
    gold = {"must_keep": ["38", "9"], "cues": ["no effect"]}
    s = score_run("GENE2 had no effect; GENE1 cut colonies by 38%.", "a b c d e f g h i j", gold)
    assert s["missing"] == ["9"] and s["cue_hits"] == ["no effect"], s
    assert original_paragraph("Tighten this.\n\nPara one.") == "Para one."
    q = {"must_keep": [], "must_keep_qualifiers": [["may", "might"], "exploratory", "post hoc"],
         "over_hedge_cues": ["may be associated"]}
    s = score_run("This post-hoc result might hold; it may be associated.", "a b", q)
    assert s["q_total"] == 3 and s["q_kept"] == 2 and s["q_dropped"] == ["exploratory"], s
    assert s["over_hedge_hits"] == ["may be associated"], s
    rows = [
        {"arm": "v1", "item": "a/train", "loaded": True, "q_total": 2, "q_dropped": [], "verdicts": ["at"]},
        {"arm": "v1", "item": "a/train", "loaded": True, "q_total": 2, "q_dropped": ["x"], "verdicts": ["above"]},
        {"arm": "v1", "item": "b/train", "loaded": None, "q_total": 2, "q_dropped": ["x"], "verdicts": ["below"]},
    ]
    out = "\n".join(summarise(rows))
    assert "skill_loaded=true     0.75  (2 runs)" in out and "skill_loaded=unknown  0.50" in out, out
    assert "a/train" in out and "n=2" in out and "dropped 0.50  above 0.50  below 0.00" in out, out
    assert "v1             2 items  dropped 0.75  above 0.25  below 0.50" in out, out
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        tr = Path(d) / "transcript.jsonl"
        msg = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Rewrite.\n\n**Changes:** x"}]}}
        tr.write_text(json.dumps(msg) + "\n", encoding="utf-8")
        assert chat_answer(tr) == "Rewrite.", chat_answer(tr)
    ok = parse_judgements('{"id": 1, "verdicts": ["at", "above"]}\n\n{"id": 2, "verdicts": ["below"]}\n', {1: 2, 2: 1})
    assert ok == {1: ["at", "above"], 2: ["below"]}
    for bad, why in [
        ('{"id": 1, "verdicts": ["at"]}\n{"id": 2, "verdicts": ["at"]}', "length"),
        ('{"id": 1, "verdicts": ["ABOVE", "at"]}\n{"id": 2, "verdicts": ["at"]}', "verdict"),
        ('{"id": 3, "verdicts": ["at"]}', "unknown id"),
        ('{"id": 1, "verdicts": ["at", "at"]}\n{"id": 1, "verdicts": ["at", "at"]}', "duplicate"),
        ('{"id": 1, "verdicts": ["at", "at"]}', "unjudged packet"),
    ]:
        try:
            parse_judgements(bad, {1: 2, 2: 1})
        except ValueError:
            continue
        raise AssertionError(f"parse_judgements accepted {why}")
    with tempfile.TemporaryDirectory() as d:
        tr = Path(d) / "transcript.jsonl"
        tr.write_text('\n{"type": "assistant", "message": {"content": "plain string"}}\nnot json\n', encoding="utf-8")
        assert chat_answer(tr) == "plain string", chat_answer(tr)
    print("score_prose self-test OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="*", type=Path, default=[HERE / "runs"])
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

    runs = [r for root in args.runs for r in collect(root)]
    if not runs:
        sys.exit(f"no runs under {args.runs}: run acumen bench with --tasks prose/tasks.yaml --runs prose/runs")

    print(f"{'arm':9s} {'model':18s} {'item':24s} {'rep':5s} {'loaded':6s} {'cut%':>4s}  missing / cues")
    packets, key, scored = [], [], []
    for run in runs:
        item = f"{run['task']}/{run['split']}"
        if run["answer"] is None:
            print(f"{run['arm']:9s} {run['model']:18s} {item:24s} {run['rep']:5s} no answer file")
            continue
        s = score_run(run["answer"], originals[item], gold[item])
        flags = ((f"missing {s['missing']}" if s["missing"] else "")
                 + (f" cues {s['cue_hits']}" if s["cue_hits"] else "")
                 + (f" qual {s['q_kept']}/{s['q_total']} dropped {s['q_dropped']}" if s["q_dropped"] else "")
                 + (f" over-hedge {s['over_hedge_hits']}" if s["over_hedge_hits"] else ""))
        print(f"{run['arm']:9s} {run['model']:18s} {item:24s} {run['rep']:5s} {str(run['skill_loaded']):6s} {s['reduction_pct']:>4d}  {flags or 'ok'}{' (recovered from chat)' if run['recovered'] else ''}")
        packets.append({"item": item, "original": originals[item], "claims": gold[item]["claims"], "rewrite": run["answer"]})
        key.append({k: run[k] for k in ("arm", "model", "task", "split", "rep")})
        scored.append({"arm": run["arm"], "model": run["model"], "item": item, "rep": run["rep"],
                       "loaded": run["skill_loaded"], "q_total": s["q_total"], "q_dropped": s["q_dropped"]})

    args.out.mkdir(parents=True, exist_ok=True)
    # Blinding: shuffle packets and number them; the key maps numbers back to arms.
    order = list(range(len(packets)))
    random.Random(20261102).shuffle(order)
    with (args.out / "judge_packets.jsonl").open("w", encoding="utf-8") as fp, \
         (args.out / "judge_key.jsonl").open("w", encoding="utf-8") as fk:
        for pid, i in enumerate(order, start=1):
            fp.write(json.dumps({"id": pid, **packets[i]}, ensure_ascii=False) + "\n")
            fk.write(json.dumps({"id": pid, **key[i]}) + "\n")
    # Judge verdicts, when present, are joined to runs through the key (packet id -> run).
    judgements = args.out / "judgements.jsonl"
    if judgements.is_file():
        try:
            verdicts = parse_judgements(
                judgements.read_text(encoding="utf-8"),
                {pid: len(packets[i]["claims"]) for pid, i in enumerate(order, start=1)},
            )
        except ValueError as exc:
            sys.exit(str(exc))
        for pid, i in enumerate(order, start=1):
            if pid in verdicts:
                scored[i]["verdicts"] = verdicts[pid]
    print("\n".join(summarise(scored)))
    print(f"\n{len(packets)} judge packets -> {args.out / 'judge_packets.jsonl'} (key: judge_key.jsonl)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
