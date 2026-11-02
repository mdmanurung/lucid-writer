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
cases, so only the judge counts.

## Skill arm result (2026-11-02)

24 skill-arm runs cost $2.95. A fresh blinded Opus judge rated all 48 runs together; it
rated the baseline 13 / 60, close to the first judge's 14 / 60.

| Arm | Model | above / claims |
|---|---|---|
| no skill | haiku | 8 / 30 (27%) |
| no skill | sonnet | 5 / 30 (17%) |
| skill v1 | haiku | 7 / 30 (23%) |
| skill v1 | sonnet | 2 / 30 (7%) |

Overall, 15% with the skill against 22% without (Fisher p = 0.48, treating claims as
independent, which flatters it). This is no evidence of an effect at this size.

- The skill loaded in 13 / 24 runs. Loaded runs had 4 / 33 above (12%), others 5 / 27 (19%).
- Five haiku runs loaded the skill and then put the rewrite in chat, not in `answer.md`,
  with a change log after it. `score_prose.py` recovers the first paragraph of the final
  message and marks those runs. The skill's report-style output fights "output only".
- The overclaims are the same kind in both arms: dropped "detectably", "exploratory",
  "may" or "computed on the same runs".

Detecting a halving from about 20% needs roughly 10 replicates per cell (about $25 for
both arms). Run that only if the skill first loads reliably on rewrite requests.

## Output-only probe (2026-11-02)

The skill arm's chat answers and change logs led to a rule in `SKILL.md` item 8: deliver
only the requested artifact, with no change log, and reread the original request for form.
Each probe was 12 haiku runs (about $0.90), counting only runs where the skill loaded.

| Skill text | loaded | chat-only, no `answer.md` | change log |
|---|---|---|---|
| v1 (before) | 7 | 5 | 4 |
| rule under Output rules only | 7 | 5 | 4 |
| rule in item 8 (kept) | 5 | 5 | 1 |

Moving the rule to item 8 cut change logs; the counts are small. No wording stopped haiku
from answering in chat after loading the skill: it passes the Skill tool a paraphrase that
drops the harness's "write answer.md". That is a bench artefact, not a user-facing one, so
`score_prose.py` recovers those answers and marks them. The probe copies were deleted so a
default `acumen bench` runs only v1.
