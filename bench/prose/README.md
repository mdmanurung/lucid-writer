# Prose-rewrite pilot

The closed-vocabulary bench in `../` found both models at ceiling on claim-strength
quizzes (see `../README.md`, "First results"). This pilot tests what the skill is for:
whether an everyday rewrite ("tighten this paragraph by about 20%") ends up claiming more
than its evidence allows.

| File | Holds |
|---|---|
| `tasks.yaml` | six paragraphs, each written to tempt a rewrite into overclaiming (2 tasks x 3 splits, because acumen requires three splits) |
| `gold.yaml` | per paragraph: tokens that must survive, each claim's ceiling and its tempted overclaim, screening cues |
| `score_prose.py` | the mechanical layer, and blinded packets for the judge |
| `judge_prompt.md` | the judge's instructions |

acumen's exact-match grade is meaningless here: every run reads `wrong_answer`. acumen is
used only to generate outputs in its sandbox and to record `skill_loaded`.

## Before any spend

Have a second person label every claim's ceiling in `gold.yaml` without looking at the
existing labels. Drop any item where the two labels differ.

## Pilot steps

Run from `bench/`. Each step's cost is an estimate at about $0.08 a run.

```bash
# 1. Baseline only: 6 items x 2 models x 2 replicates = 24 runs, about $2
acumen bench --no-skill --tasks prose/tasks.yaml --runs prose/runs --split train
acumen bench --no-skill --tasks prose/tasks.yaml --runs prose/runs --split valid
acumen bench --no-skill --tasks prose/tasks.yaml --runs prose/runs --split test

# 2. Mechanical scores and blinded judge packets
uv run --quiet --no-project --with pyyaml prose/score_prose.py prose/runs
```

3. Judge: give a fresh `claude-opus-5` session `judge_prompt.md` and `judge_packets.jsonl`,
   and save its output as `judgements.jsonl`.
4. **Gate:** if under about 10% of claims are judged `above` in the baseline, the
   paragraphs are not tempting enough. Rewrite them before running the skill arm.
5. Otherwise, run the skill arm on four runs and check `skill_loaded`:
   `acumen bench --skill v1 --tasks prose/tasks.yaml --runs prose/runs --task prose-results --split train`.

`runs/`, the packets, the key and the judgements are gitignored: they are regenerable output.

## Baseline result (2026-11-02)

24 no-skill runs cost $2.48. One blinded Opus judge rated 14 of 60 claims (23%) `above`
their ceiling, so the paragraphs pass the gate. The gold labels have not yet had a second
labeller.

| Model | above / claims |
|---|---|
| claude-haiku-4-5 | 9 / 30 |
| claude-sonnet-5 | 5 / 30 |

Almost every overclaim drops a qualifier rather than adding a causal verb:

- "detectably" was dropped from the viability claim (4 runs);
- "exploratory" or "appeared" was dropped from the subgroup claim (4 runs);
- "computed on the same runs" was dropped from the in-sample R² claim (2 runs);
- "may", the "not measured" caveat and the not-significant statement were each dropped once;
- "associated with" became "predicted" once.

The spaced-practice item drew no overclaim (0 / 8). The cue list caught none of the 14
cases, so only the judge counts. Next: run the skill arm on the same items and compare
`above` rates.
