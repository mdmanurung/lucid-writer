# Benchmark harness

An [acumen](https://github.com/scverse/acumen) pass over this repository's skill, so that
"does the skill help?" becomes a number with a held-out split behind it instead of an
eyeball comparison.

This exists because the evals already in `evals/` say so themselves. `README.md` calls the
paired A/B "not presented as an independent benchmark", calls the second-pass fixture a
"development smoke test", and every result in the repository was produced in-session, by one
model, with no held-out split and no baseline arm held in isolation. Those are honest
caveats and they are also the exact gaps a benchmark closes.

## What it measures, and what it does not

Acumen grades a run by **exact string match** on `answer.md` after `strip()`
(`acumen.grade.grade_answer`). Nothing is normalised. So a task whose answer is a paragraph
of prose cannot be graded: no two runs produce byte-identical prose, and every run would
score `wrong_answer` regardless of quality.

Every task in [`tasks.yaml`](tasks.yaml) is therefore a **closed-vocabulary judgement** —
which epistemic class a statement belongs to, which inference ceiling its evidence permits,
which repair preserves claim strength. Those have defensible answers, and they are the
skill's actual invariants (`SKILL.md:70`, `references/evidence.md`).

**Not measured: concision, readability, flow, voice, or whether a paragraph reads better.**
Those need a rubric judge, which acumen does not have. Do not quote a score from this
directory as evidence about prose quality. If that is the question, it needs a different
harness.

The task set is deliberately small (4 task types, 12 train/valid/test splits). It is a smoke pass
that proves the plumbing and produces a first delta — not a benchmark to publish.

## Which tasks can show a skill effect

`ceiling-defined` hands both arms the five ceiling definitions. It is the **control**: it
measures prompt-following, so a skill delta there is noise or a harness artifact.

`ceiling-open`, `claim-class` and `minimal-repair` give only labels or options. The rules
that decide them (ceiling boundaries, the O/L/I/H classes, the evidence-first repair
priority) live in the skill, not the prompt, so these three are where a real effect can
appear. If the skill arm scores well below on `ceiling-open` than on `ceiling-defined`, the
skill's ceiling vocabulary is under-specified.

## Setup

Requires Python 3.12+ and [`uv`](https://github.com/astral/uv). Acumen is not vendored:

```bash
uv tool install --force 'acumen[claude] @ git+https://github.com/scverse/acumen@c6acb9f9553aea41251cf9f0b3d6e0a93aecd94f'
```

Install from git rather than PyPI. The published `acumen` is `0.0.1.dev0` and its CLI has
no `check` and no `prices`. The pin (`c6acb9f9`, 2026-10-26) is the commit this task set
was checked with; CI uses the same one. Older commits fail here: before `8c8a81ccd` acumen
cannot parse OpenAI's pricing page and `acumen bench` refuses to run, and before `beae7bf6d`
it rejects the `valid` split. Bump the pin deliberately, after `acumen check --no-review`
passes on the new commit.

Acumen benchmarks the committed `ref:` in `config.yaml` (`main`), not the working tree.
Commit the skill and packaging changes before a pass, or it measures the last commit.

Claude is an optional dependency and the Codex CLI is external, so install only the backend
you run. Both a `~/.claude/.credentials.json` subscription login and `~/.codex/auth.json`
exist on this host, so `--auth auto` will bill subscription quota and record the API-rate
equivalent rather than metered dollars.

## Commands

```bash
cd bench

# Free. Prepares the target venv, parses tasks.yaml, confirms every split is well formed.
# This is the gate to run before any pass that spends anything.
acumen check --no-review

# Costs money. The same, plus one agent per split that reads prompt, answer and script
# together and flags a prompt that does not ask for the answer recorded beside it.
# It checks that prompt and answer agree, not that the answer is scientifically right:
# review new items by hand too. Run it once per task-set change before trusting results.
acumen check

acumen bench --no-skill       # baseline arm, train + valid
acumen bench --skill v1       # skill arm, train + valid
acumen bench                  # both arms
acumen improve                # v1 -> v2, from TRAIN results only
acumen bench --split test     # final comparison; bench skips test by default
acumen report                 # report.html
```

## Workflow

```text
skills/v1  = frozen copy of skills/lucid-writer/
     |
     +-- acumen bench --no-skill      arm: noskill   (control)
     +-- acumen bench --skill v1      arm: skill_v1
     |
     +-- acumen improve               reads TRAIN results only -> skills/v2
     +-- acumen bench --skill v2      arm: skill_v2
     |
     +-- acumen bench --split test    v1 vs v2 on held-out TEST
     +-- v2 beats v1 on TEST -> copy skills/v2 over skills/lucid-writer/
```

A skill arm differs from the baseline in exactly one way: `skills/v{n}/` is copied into the
sandbox's `.claude/skills/lucid-writer/`, where the agent's own discovery finds it. Same
prompt, same tools, same caps, same scrubbed environment (`acumen.sandbox`).

`skills/v1/` is a **frozen copy**. Edit `skills/lucid-writer/`, re-copy to `v1`, and
re-run — never edit `v1` in place, or a later `improve` has no fixed baseline to beat.
`improve` writes `v2` and never mutates `v1`.

Only copy a winning version back over the real skill once it wins on the **test** split. A
version that only wins on train has learned the task set.

## Cost

A pass is `models x tasks x replicates x splits x arms`. The committed config is
1 model x 4 tasks x 2 replicates x 2 splits (train, valid) x 2 arms = **32 runs**, which is a
smoke pass; `--split test` adds 16 more.
Check `acumen prices` for current rates before scaling up; every run's cost is derived from
its own token counts and frozen into `result.json`, so a pass stays individually
attributable even after provider prices move.

Before quoting any number as a result, raise `n_replicates` to 3 or more and add a second
model. The informative axis is a quality spread — a skill that helps only the weak model is
a different product from one that helps the strong model, and both are plausible — so add
`claude-haiku-4-5-20251001` next to `claude-sonnet-5` rather than reaching for opus.

## Reading the results

`acumen report` gives success rate per arm and split, coloured by model. Two things to
check before believing it:

- **A widening train/test gap means the skill is overfitting the task set**, not that it
  works. This is the failure mode a same-session eval cannot show.
- **The committed config cannot detect a modest effect.** Each task is scored 0 or 1, so
  4 tasks x 2 replicates is 8 binary outcomes per arm per split. At 8 vs 8, only about 8/8
  vs 3/8 or wider is a two-sided p < 0.05 (Fisher). The `ceiling-open` vs `ceiling-defined`
  comparison is one task each, so 2 vs 2 outcomes: unreadable until `n_replicates` is 5 or
  more. Replicates of one prompt on one model are not independent draws, so the real
  sample size is closer to the task count.
- **Check `skill_loaded` before reading an arm delta.** `score.py` lists skill-arm runs where
  acumen saw no sign the skill fired; those runs measure the baseline. The skill triggers on
  manuscript work, and a five-line labelling quiz may not trigger it.
- **The baseline is not sealed from the skill.** For a local target acumen blocks no
  repository, and this repo is public: a baseline agent with web access could fetch
  `SKILL.md` from GitHub. Search the noskill transcripts for `lucid-writer` before trusting
  a small baseline-to-skill gap.
- For per-item diagnostics, run `score.py`, or read the retained `answer.md` files under
  `runs/` against `tasks.yaml`.

Runs land in `runs/{arm}/{split}/{model}/{task_id}/rep_{n}/`, each with `answer.md`, the
transcript, and a `result.json` carrying tokens, cost, grade reason and skill hash. The run
tree is not committed.

## Why this repository has a `pyproject.toml` and a `lucid_writer/`

Neither is for the skill's users. Both exist because `acumen` cannot target a repository with
no importable Python package:

- `acumen.env.prepare_target` refuses a checkout without a `pyproject.toml` declaring
  `[project].name`, and requires that name to resolve via `importlib.metadata` in the venv.
- `acumen.check._PROBE_CODE` then imports the module and requires `__version__`.

So the repository gains one trivial module and nothing else, and `__version__` there is the
single source of the version number — `pyproject.toml` reads it, and
`scripts/validate_repo.py` asserts all three plugin manifests agree.
