#!/usr/bin/env python3
"""Per-item diagnostics for an acumen run tree.

`acumen report` gives the headline number: exact-match success rate per arm, split and
model. That number is coarse. A task with five graded items is scored 0 or 1, so a small
pass resolves to a few percentage points and cannot tell "the skill fixed claim strength"
from "the skill fixed the one item that was always borderline".

This reads the `answer.md` files the run tree retains and compares them to the expected
answers item by item, so the run says which claim was mislabelled and how often. That is
the number to look at when deciding what to edit in the skill.

Usage:
    uv run --with pyyaml bench/score.py [runs_dir] [--tasks bench/tasks.yaml]

Defaults to `bench/runs` and `bench/tasks.yaml` relative to this file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("score.py needs PyYAML: run it as `uv run --with pyyaml bench/score.py`")


def load_expected(tasks_path: Path) -> dict[tuple[str, str], list[str]]:
    """Map (task_id, split) to the expected answer as a list of graded items."""
    data = yaml.safe_load(tasks_path.read_text(encoding="utf-8"))
    out: dict[tuple[str, str], list[str]] = {}
    for task in data["tasks"]:
        for split in ("train", "valid", "test"):
            out[(task["id"], split)] = task[split]["answer"].strip().splitlines()
    return out


def collect(runs_dir: Path) -> list[dict]:
    """Every completed run, from its result.json."""
    runs = []
    for result_path in sorted(runs_dir.glob("**/result.json")):
        try:
            data = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        answer_path = result_path.parent / "answer.md"
        data["_answer"] = answer_path.read_text(encoding="utf-8") if answer_path.is_file() else None
        runs.append(data)
    return runs


def answer_items(answer: str | None, n: int) -> tuple[list[str], bool]:
    """Split an answer into graded items, and say whether its shape matched.

    The grader wants one item per line. A run that writes the right items on one line
    (``S1=A, S2=B``) fails exact match on format, not on judgement, so it is split on
    commas, semicolons and whitespace instead and reported as a format error rather
    than as item misses. Returns (items, shape_ok).
    """
    lines = (answer or "").strip().splitlines()
    if len(lines) == n:
        return lines, True
    tokens = [x for x in re.split(r"[,;\s]+", (answer or "").strip()) if x]
    if len(tokens) == n:
        return tokens, False
    return lines, False


def item_accuracy(run: dict, expected: list[str]) -> tuple[int, int, list[str]]:
    """Compare a run's answer to the expected one item by item.

    Returns (correct, total, misses). An item counts only when the answer splits into
    exactly the expected number of items; a run with the wrong shape scores zero correct
    rather than silently scoring its overlapping prefix.
    """
    got, _ = answer_items(run["_answer"], len(expected))
    if len(got) != len(expected):
        return 0, len(expected), [f"{e!r} (no comparable line: got {len(got)} of {len(expected)})" for e in expected]
    correct = 0
    misses = []
    for want, have in zip(expected, got):
        if want.strip() == have.strip():
            correct += 1
        else:
            misses.append(f"{want.strip()!r} -> got {have.strip()!r}")
    return correct, len(expected), misses


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="?", type=Path, default=here / "runs")
    parser.add_argument("--tasks", type=Path, default=here / "tasks.yaml")
    args = parser.parse_args()

    if not args.runs.is_dir():
        sys.exit(f"no run tree at {args.runs} — run `acumen bench` first")

    expected = load_expected(args.tasks)
    runs = collect(args.runs)
    if not runs:
        sys.exit(f"no result.json under {args.runs} — run `acumen bench` first")

    invalid = [r for r in runs if not r.get("valid", True)]
    print(f"runs found: {len(runs)} ({len(invalid)} invalid, excluded from every number below)")
    print("  invalid means an infrastructure failure, not a wrong answer — check `reason`\n")

    # Headline: exact-match success, the same metric `acumen report` plots.
    print("=" * 72)
    print("EXACT-MATCH TASK SUCCESS (the report.html metric)")
    print("=" * 72)
    cells = defaultdict(lambda: [0, 0])
    for run in runs:
        if not run.get("valid", True):
            continue
        key = (run["arm"], run["split"], run["model"])
        cells[key][1] += 1
        cells[key][0] += bool(run.get("success"))
    for (arm, split, model), (ok, total) in sorted(cells.items()):
        print(f"  {arm:10s} {split:5s} {model:22s} {ok:3d}/{total:<3d} {100 * ok / total:5.1f}%")

    # Right labels in the wrong layout fail exact match; say so, rather than leaving the
    # reader to infer a judgement error from the headline.
    format_only = []
    for run in runs:
        want = expected.get((run["task_id"], run["split"]))
        if not run.get("valid", True) or want is None or run.get("success"):
            continue
        got, shape_ok = answer_items(run["_answer"], len(want))
        if not shape_ok and [g.strip() for g in got] == [w.strip() for w in want]:
            format_only.append(run)
    print()
    print("=" * 72)
    print("FORMAT-ONLY FAILURES (every label right, layout wrong; graded as a miss)")
    print("=" * 72)
    for run in format_only:
        print(f"  {run['arm']:10s} {run['task_id']}/{run['split']} {run['model']}")
    if not format_only:
        print("  none")

    # A skill-arm run whose skill never fired measures the baseline, not the skill.
    print()
    print("=" * 72)
    print("SKILL LOADED (acumen's skill_loaded; None means it could not tell)")
    print("=" * 72)
    loaded = defaultdict(lambda: defaultdict(int))
    unattributed = []
    for run in runs:
        if not run.get("valid", True) or run["arm"] == "noskill":
            continue
        state = run.get("skill_loaded")
        loaded[run["arm"]][state] += 1
        if state is not True:
            unattributed.append(run)
    for arm, counts in sorted(loaded.items()):
        total = sum(counts.values())
        print(f"  {arm:10s} loaded {counts[True]}/{total}  not loaded {counts[False]}  unknown {counts[None]}")
    for run in unattributed:
        print(f"    unattributed: {run['task_id']}/{run['split']} {run['arm']} skill_loaded={run.get('skill_loaded')}")
    if not loaded:
        print("  no skill-arm runs")

    # Diagnostic: per-item accuracy, which is where the resolution actually is.
    print()
    print("=" * 72)
    print("PER-ITEM ACCURACY (diagnostic; higher resolution than the metric above)")
    print("=" * 72)
    per_cell = defaultdict(lambda: [0, 0])
    for run in runs:
        if not run.get("valid", True):
            continue
        want = expected.get((run["task_id"], run["split"]))
        if want is None:
            continue
        correct, total, _ = item_accuracy(run, want)
        key = (run["arm"], run["split"])
        per_cell[key][0] += correct
        per_cell[key][1] += total
    for (arm, split), (ok, total) in sorted(per_cell.items()):
        print(f"  {arm:10s} {split:5s} {ok:4d}/{total:<4d} {100 * ok / total:5.1f}%")

    # Which specific item fails, and in which arm. This is the actionable list.
    print()
    print("=" * 72)
    print("MOST-FAILED ITEMS (what to edit in the skill)")
    print("=" * 72)
    misses_by_item = defaultdict(lambda: defaultdict(int))
    seen_by_item = defaultdict(lambda: defaultdict(int))
    for run in runs:
        if not run.get("valid", True):
            continue
        want = expected.get((run["task_id"], run["split"]))
        if want is None:
            continue
        got, _ = answer_items(run["_answer"], len(want))
        comparable = len(got) == len(want)
        # Key on task, split and position: the same expected line can recur across
        # tasks (e.g. `C1=DESCRIPTIVE`) and must not be pooled into one row.
        arm = run["arm"]
        for i, item in enumerate(want):
            key = (run["task_id"], run["split"], i, item)
            seen_by_item[key][arm] += 1
            if not comparable or got[i].strip() != item.strip():
                misses_by_item[key][arm] += 1

    rows = []
    for key, per_arm in misses_by_item.items():
        for arm, misses in per_arm.items():
            seen = seen_by_item[key][arm]
            if misses:
                rows.append((misses / seen, misses, seen, arm, key))
    if not rows:
        print("  no item-level misses in any arm")
    else:
        print(f"  {'arm':10s} {'miss':>9s}  task/split  expected")
        for rate, misses, seen, arm, (task, split, _, item) in sorted(rows, reverse=True):
            print(f"  {arm:10s} {misses:3d}/{seen:<3d} ({100 * rate:4.0f}%)  {task}/{split}  {item}")

    print()
    print("A miss in the noskill arm only is a task the skill fixed.")
    print("A miss in both arms is a task the skill does not reach — edit the skill.")
    print("A miss in the skill arm but not the baseline is worse than useless: investigate first.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
