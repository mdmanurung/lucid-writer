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

The task set is deliberately small (4 task types, 8 train/test splits). It is a smoke pass
that proves the plumbing and produces a first delta — not a benchmark to publish.

## The one task family that probes a real gap

`ceiling-open` hands over the five inference-ceiling labels but not their definitions.
`ceiling-defined` hands over both. `references/evidence.md:20-24` lists the ceilings without
saying where the boundaries lie, so if the skill arm scores materially lower on
`ceiling-open` than on `ceiling-defined`, the finding is that **the skill's ceiling
vocabulary is under-specified** — a real, cheap fix to the skill that no same-session
eyeball check would surface.

By contrast `claim-class` tests the epistemic classes, for which the skill *does* supply
operational definitions (`references/evidence.md:9-12`). That is the family where the skill
should show its largest gain, and it is the control for whether the harness detects gain at
all.

## Setup

Requires Python 3.12+ and [`uv`](https://github.com/astral/uv). Acumen is not vendored:

```bash
uv tool install --force 'acumen[claude] @ git+https://github.com/scverse/acumen@dfedfe05dc6a2da64155ce87597e0cbb60457f10'
```

Install from git rather than PyPI. The published `acumen` is `0.0.1.dev0` and its CLI has
no `check` and no `prices`. Pin commit `dfedfe05d` (2026-09-04): it is the last one that
accepts this file's train/test splits. From `beae7bf6d` on, acumen requires a `valid` split
in every task; unpin after adding one. CI uses the same pin.

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
# This is the safeguard on hand-written ground truth: run it once before trusting results.
acumen check

acumen bench --no-skill       # baseline arm
acumen bench --skill v1       # skill arm
acumen bench                  # both
acumen improve                # v1 -> v2, from TRAIN results only
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
1 model x 4 tasks x 2 replicates x 2 splits x 2 arms = **32 runs**, which is a smoke pass.
Check `acumen prices` for current rates before scaling up; every run's cost is derived from
its own token counts and frozen into `result.json`, so a pass stays individually
attributable even after provider prices move.

Before quoting any number as a result, raise `n_replicates` to 3 or more and add a second
model. The informative axis is a quality spread — a skill that helps only the weak model is
a different product from one that helps the strong model, and both are plausible — so add
`claude-haiku-4-5-20251001` next to `claude-sonnet-5` rather than reaching for opus.

## Reading the results

`acumen report` gives success rate per arm, train and test, coloured by model. Two things to
check before believing it:

- **A widening train/test gap means the skill is overfitting the task set**, not that it
  works. This is the failure mode a same-session eval cannot show.
- **All-or-nothing per task is coarse.** A 5-item task scored exact-match is 0 or 1, so
  8 splits x 2 replicates gives 16 binary outcomes per arm — about 6 percentage points of
  resolution. For per-item diagnostics, read the retained `answer.md` files under `runs/`
  and compare them line by line against `tasks.yaml`.

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
