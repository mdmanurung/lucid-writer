#!/usr/bin/env python3
"""Release gate for the always-on rules.

Rewrites each gate abstract N times per setup with clean `claude -p` runs
(no user settings, plugins, hooks or CLAUDE.md; only the system prompt
differs), then has one more clean run code every output blind against the
original. The gate passes when no `full*` setup keeps a causal C1 or
strengthens C2, and every setup has at least MIN_OK completed runs per
abstract.

Exit codes: 0 pass, 1 fail (a claim failure), 2 inconclusive (too many runs
blocked or errored). Run from the repository root; see bench/gate/README.md.
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "bench" / "gate"
RULES = ROOT / "hooks" / "rules"
USER_PROMPT = "Revise this abstract for journal submission. Return only the revised abstract."
MIN_OK = 2  # completed runs needed per setup and abstract; fewer is inconclusive


def read(path):
    return Path(path).read_text(encoding="utf-8").strip()


def setup_prompt(name, voice):
    """System prompt for a setup, built from the rule files in this checkout."""
    prose = RULES / "prose.md" if (RULES / "prose.md").exists() else RULES / "lite.md"
    if name in ("prose", "lite"):
        return read(prose)
    if name == "full":
        return "\n\n".join([read(prose), read(RULES / "full.md"), read(RULES / "voice-default.md")])
    if name == "full_voice":
        if not voice:
            sys.exit("setup full_voice needs --voice PATH")
        return "\n\n".join([read(prose), read(RULES / "full.md"), read(voice)])
    sys.exit(f"unknown setup: {name}")


def claude(system, user, model):
    """One clean claude -p call; returns (ok, text)."""
    cmd = ["claude", "-p", "--setting-sources", "project", "--strict-mcp-config",
           "--disable-slash-commands", "--tools", "", "--no-session-persistence",
           "--model", model, "--system-prompt", system]
    try:
        out = subprocess.run(cmd, input=user, capture_output=True, text=True,
                             timeout=600, cwd=GATE).stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"
    return (bool(out) and not out.startswith("API Error")), out


def recode_prompt(original, claims, revisions):
    head = (
        "You are checking revisions of an abstract for changes in claim strength relative to the "
        f"original. The design is a {claims['design']}.\n\n"
        "For EACH revision output one JSON object per line (JSON Lines, nothing else) with keys: "
        f"id; c1 = how {claims['c1']} is stated: one of causal, association, neutral, dropped; c1_quote; "
        f"c2 = {claims['c2']} compared with the original: stronger, same, weaker; c2_quote; "
        "added = list of short quotes of claims, details, restrictions or hypotheses not in the original; "
        "dropped = list of findings, numbers, attributions or hedges from the original that are missing.\n\n"
        f"ORIGINAL:\n{original}\n"
    )
    return head + "\n".join(f"\n{k}:\n{t}" for k, t in revisions.items())


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--setups", default="prose,full", help="comma list: prose, full, full_voice")
    ap.add_argument("--voice", help="voice.md for the full_voice setup")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--model", default="claude-opus-5-5",
                    help="explicit ID; the 'opus' alias resolved to a model whose classifier blocked a biology abstract")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()

    setups = [s.strip() for s in a.setups.split(",") if s.strip()]
    claims = json.loads(read(GATE / "abstracts" / "claims.json"))
    abstracts = {k: read(GATE / "abstracts" / f"{k}.txt") for k in claims}
    run_dir = GATE / "runs" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)

    # Rewrites.
    jobs = [(s, ab, r) for s in setups for ab in abstracts for r in range(1, a.runs + 1)]
    systems = {s: setup_prompt(s, a.voice) for s in setups}
    outputs = {}
    with cf.ThreadPoolExecutor(a.jobs) as pool:
        futs = {pool.submit(claude, systems[s], f"{USER_PROMPT}\n\n{abstracts[ab]}", a.model): (s, ab, r)
                for s, ab, r in jobs}
        for fut in cf.as_completed(futs):
            s, ab, r = futs[fut]
            ok, text = fut.result()
            (run_dir / f"{s}__{ab}__{r}.txt").write_text(text, encoding="utf-8")
            if ok:
                outputs[(s, ab, r)] = text

    # Blind recode, one call per abstract, revisions shuffled under neutral labels.
    codes = {}
    for ab in abstracts:
        mine = [k for k in outputs if k[1] == ab]
        random.Random(ab).shuffle(mine)
        labels = {f"R{i + 1:02d}": k for i, k in enumerate(mine)}
        if not labels:
            continue
        ok, text = claude("You are a meticulous scientific editor. Output only JSON Lines.",
                          recode_prompt(abstracts[ab], claims[ab], {l: outputs[k] for l, k in labels.items()}),
                          a.model)
        (run_dir / f"recode_{ab}.jsonl").write_text(text, encoding="utf-8")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("{"):
                d = json.loads(line)
                if d.get("id") in labels:
                    codes[labels[d["id"]]] = d

    # Score.
    rows, failed, inconclusive = [], False, False
    for s in setups:
        for ab in abstracts:
            ks = [k for k in outputs if k[0] == s and k[1] == ab]
            coded = [codes[k] for k in ks if k in codes]
            causal = sum(c["c1"] == "causal" for c in coded)
            stronger = sum(c["c2"] == "stronger" for c in coded)
            added = sum(len(c.get("added", [])) for c in coded)
            gated = s.startswith("full")
            short = gated and len(coded) < MIN_OK
            fail = gated and bool(causal or stronger)
            failed |= fail
            inconclusive |= short
            rows.append((s, ab, len(coded), a.runs - len(ks), causal, stronger,
                         f"{added / len(coded):.1f}" if coded else "-",
                         "FAIL" if fail else ("inconclusive" if short else ("ok" if gated else "not gated"))))

    verdict = "FAIL" if failed else ("INCONCLUSIVE" if inconclusive else "PASS")
    lines = [f"## Gate: {verdict}", "",
             f"Model `{a.model}`, {a.runs} runs per setup and abstract, blind recode. "
             f"Runs in `{run_dir.relative_to(ROOT)}`.", "",
             "| Setup | Abstract | Coded runs | Blocked or failed | C1 kept causal | C2 stronger | Additions per run | Result |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {' | '.join(str(x) for x in r)} |" for r in rows]
    lines += ["", "Pass rule: no `full` setup keeps a causal C1 or strengthens C2; "
              f"at least {MIN_OK} coded runs per `full` setup and abstract. `prose` is reported, not gated."]
    summary = "\n".join(lines)
    (run_dir / "summary.md").write_text(summary + "\n", encoding="utf-8")
    print(summary)
    return 1 if failed else (2 if inconclusive else 0)


if __name__ == "__main__":
    raise SystemExit(main())
