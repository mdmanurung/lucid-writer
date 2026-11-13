# Prose-rewrite pilot

The closed-vocabulary bench in `../` found both models at ceiling on claim-strength
quizzes (see `../README.md`, "First results"). This pilot tests what the skill is for:
whether an everyday rewrite ("tighten this paragraph by about 20%") ends up claiming more
than its evidence allows.

| File | Holds |
|---|---|
| `tasks.yaml` | twelve paragraphs (4 tasks x 3 splits, because acumen requires three splits): six written to tempt a rewrite into overclaiming, three `prose-control` paragraphs that are already correctly hedged, and three `prose-immuno-exvivo` paragraphs |
| `tasks-forced.yaml` | generated from `tasks.yaml` by `make_forced.py`: every prompt starts "Use lucid-writer to", which forces the skill to load |
| `gold.yaml` | per paragraph: tokens that must survive, qualifiers that must survive, each claim's ceiling and its tempted overclaim, screening cues |
| `score_prose.py` | the mechanical layer, summaries, and blinded packets for the judge |
| `make_forced.py` | writes `tasks-forced.yaml`; `--check` fails if it is stale (`validate_repo.py` runs it) |
| `judge_prompt.md` | the judge's instructions; rates each claim `below`, `at`, `above` or `missing` |

acumen's exact-match grade is meaningless here: every run reads `wrong_answer`. acumen is
used only to generate outputs in its sandbox and to record `skill_loaded`.

## Before any spend

Have a second person label every claim's ceiling in `gold.yaml` without looking at the
existing labels. Drop any item where the two labels differ.

## Pilot steps

Run from `bench/`. Each step's cost is an estimate at about $0.08 a run.

```bash
# 1. Baseline only: 6 items x 2 models x 2 replicates = 24 runs, about $2
# (--task is repeatable; without it acumen also runs the control and immuno tasks)
for s in train valid test; do
  acumen bench --no-skill --tasks prose/tasks.yaml --runs prose/runs --task prose-results --task prose-discussion --split $s
done

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

## Separating activation from quality (added 2026-11-13)

The pilot could not tell whether the skill failed to load or loaded and did not help. These
additions separate the two. All of them are free to run on existing outputs.

**Qualifier retention.** `gold.yaml` lists `must_keep_qualifiers` per item: the hedges and
design limits the source states. `score_prose.py` prints per run which ones the rewrite
dropped, and then the mean fraction kept per arm, split by `skill_loaded` (true, false,
unknown). The match is mechanical and uses `qualifier_check.py`'s phrase matching, so it
does not need the judge. An entry may list interchangeable phrases ("may" or "might").

**Items, not runs.** Repeated runs of one prompt are not independent. The summary counts
per item (paragraph x split), pooling models and replicates, and gives the fraction of runs
with at least one dropped qualifier. With `judgements.jsonl` present it also gives the
fraction with at least one claim `above` and at least one `below`. The per-arm line then
takes the mean over items. The claim-level counts stay for comparison with the earlier
tables above.

**Forced arm.** `tasks-forced.yaml` prefixes each prompt with "Use lucid-writer to". Run it
into its own tree, `prose/runs-forced`. Pass both trees to the scorer; the forced arm shows
as `v1+forced`. If forced runs retain more qualifiers than unforced skill runs, the gap is
loading. If they do not, the skill text is the problem.

**Controls and needless weakening.** The three `prose-control` paragraphs already sit at
their ceiling. A good rewrite changes no claim's strength. `over_hedge_cues` flags phrases
such as "may be associated" as a screen, and the judge rates a weakened claim `below`. The
summary reports `below` next to `above`. Controls carry synthetic numbers.

**Not yet done.** The second labeller pass on the gold ceilings (see "Before any spend")
now covers twelve items, six of them new (three controls, three immuno).

## Paid commands for this phase

Run from `bench/`. Costs are estimates at about $0.08 a run. Two models x two replicates
make four runs per item, so one arm over all twelve items is 48 runs, about $3.84.

```bash
# A. Controls, no-skill and skill v1: 3 items x 4 runs x 2 arms = 24 runs, about $1.90
for s in train valid test; do
  acumen bench --no-skill   --tasks prose/tasks.yaml --runs prose/runs --task prose-control --split $s
  acumen bench --skill v1   --tasks prose/tasks.yaml --runs prose/runs --task prose-control --split $s
done

# B. Forced-activation arm on all twelve items: 48 runs, about $3.84
for s in train valid test; do
  acumen bench --skill v1 --tasks prose/tasks-forced.yaml --runs prose/runs-forced --split $s
done

# C. Score both trees (free), then judge as before
uv run --quiet --no-project --with pyyaml prose/score_prose.py prose/runs prose/runs-forced
```

Total for A and B: 72 runs, about $5.76, plus one Opus judge pass over the new packets. The
immuno item adds 4 runs per arm and split on top, about $0.30 each, once its probe shows the
baseline errs. These counts were checked with `acumen bench --dry-run`.
Ids in `judge_packets.jsonl` change whenever runs are added, so judge after the last run
and save `judgements.jsonl` against that packet file.

`bench/skills/v1/` is frozen and now older than `skills/lucid-writer/`. A pass that tests
the qualifier work needs a new skill copy first; the maintainer decides its name.

## Immunology fixture (added 2026-11-13)

`prose-immuno-exvivo` has three variants of a paired ex vivo cytokine result followed by a
Discussion hint at protection. All numbers are synthetic, labelled in `tasks.yaml`. The
measured response is OBSERVED and DESCRIPTIVE under its stated conditions; the link to
protection is at most a HYPOTHESIS. The source paragraphs pass their own gold sheets.

The probe scores into its own directory (`--out`) so it never overwrites the pilot's judge
packets. Probe the baseline before keeping it, as `../README.md` requires. Each probe is 4 runs
(2 models x 2 replicates), about $0.30. Run from `bench/`:

```bash
acumen bench --no-skill --tasks prose/tasks.yaml --runs prose/runs-probe --task prose-immuno-exvivo --split train
uv run --quiet --no-project --with pyyaml prose/score_prose.py prose/runs-probe --out prose/runs-probe
```

Keep the task only if the baseline errs: a rewrite drops "ex vivo", the stimulation
condition or the hedge on protection, or the judge rates a claim `above`. If the baseline
does not err, delete the task from `tasks.yaml` and `gold.yaml` and rerun `make_forced.py`;
`valid` and `test` stay unrun. Note that acumen needs all three splits to parse the file,
so the variants are written already, but nothing is spent on them.

`bench/skills/v2/` is a copy of the skill taken after the qualifier-survival work. Run the skill arm with `--skill v2` in the commands above to test it. `v1` is the older baseline copy.

## Results of the second pass (2026-11-13)

Skill version `v2` (a copy of the skill after the qualifier, evidence and warrant work), two
models, two replicates, all 12 items. The no-skill arm and the forced arm cover all 12 items;
the unforced `v2` arm covers only the control and immunology items. The runs cost $12.83 at
API rates (the runs were session-billed, so that is not metered spend), against my estimate of
about $9. Two blinded Opus judges rated every claim in 117 rewrites; they agree on 276 of 280
claims (98.6%). Judge A is the primary result below; judge B is in brackets.

`table fallback:` counts of runs per arm are a small contingency table that a table states
exactly. No figure was made, and making one needs a grill plan. Every conclusion here is
therefore a table reading, not a figure reading.

Runs with at least one claim judged `above` its ceiling. Three runs with no rewrite are
excluded (see below). Fisher's exact test, two-sided, treating runs as independent.

| Items | no skill | `v2` forced | p |
|---|---|---|---|
| all 12 | 10 / 48 (20.8%) | 6 / 46 (13.0%) [5 / 46] | 0.41 [0.26] |
| the 6 original-task items | 9 / 24 (37.5%) | 6 / 24 (25.0%) [5 / 24] | 0.53 [0.34] |
| the 6 control and immunology items | 1 / 24 (4.2%) | 0 / 22 | 1.00 |

By model, on all 12 items: sonnet 4 / 24 without the skill and 0 / 24 forced; haiku 6 / 24
without and 6 / 22 forced. The unforced `v2` arm, on the 6 control and immunology items only,
had 2 / 23 [1 / 23] against 1 / 24 for no skill, which says nothing because those items rarely
draw an overclaim.

What the tables show:

- The skill points the right way when forced to load, but no difference reaches significance,
  and the 12-item sample is too small to detect one. The effect sits in sonnet; haiku shows
  none. Earlier I estimated about 10 replicates per cell to detect a halving from 20%.
- The overclaims are on the original items. `prose-results` has 7 / 12 runs above without the
  skill and 5 / 12 forced; `prose-discussion` has 2 / 12 and 1 / 12 [0 / 12].
- The skill loaded in 18 of 24 unforced `v2` runs (`v1` loaded in 13 of 24 in the first pilot,
  on different items) and in 48 of 48 forced runs.
- The mechanical qualifier retention is close across arms: 0.68 for no skill, 0.72 to 0.75 for
  unforced `v2` (by `skill_loaded`) and 0.73 forced. Per item, the share of runs with a dropped
  qualifier is 0.62 without the skill and 0.50 forced.
- No needless weakening: the controls drew 0 `above` and 0 `below` without the skill, and
  `below` in 1 of 22 forced runs [2 of 22].

Immunology gate. The baseline had 1 / 12 runs above (1 of 24 claims, 4%), both judges, under
the 10% gate in step 4 of the pilot. The probe showed one real hedge drop (haiku wrote
"suggesting a protective mechanism") and one false positive ("a potential protective
mechanism", now an accepted synonym). The paragraphs are not tempting enough. Rewrite them to
be harder or drop the task; I did not decide.

Output form. Three haiku runs loaded the skill and then answered in chat with only a
preamble, so no rewrite exists (one unforced, two forced; two of the preambles name the
skill). They were left out of judging so they could not unblind it, and are recorded as
`missing` for every claim. Counting them as ordinary runs gives 6 / 48 forced and 2 / 24
unforced. Four more runs were recovered from chat as real rewrites.

Not done: a second labeller for the gold ceilings, and a judge that did not know the item
labels beyond what is in the packets.

