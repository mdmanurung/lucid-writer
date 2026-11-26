# Prose bench: analysis plan for the paper run

Status: approved by the author on 2026-11-26, before any paper run. Every row below is the
author's choice; none is a default left unasked. A change after the first paper run is logged
in the change log at the end, with the date and the reason, and the result is reported as a
deviation.

## Question

Does forcing the Lucid Writer skill to load lower the share of rewrites that state a claim
above its evidence, compared with no skill?

## Design choices

| # | Choice | Value | Source |
|---|---|---|---|
| 1 | Primary endpoint | A run counts when one or more of its gold claims is judged `above` its ceiling (run-level) | user, 2026-11-26 (pilot value, `README.md:212`) |
| 2 | Rewriter models | `claude-sonnet-5`, `claude-haiku-4-5` | user (pilot value, `../config.yaml`) |
| 3 | Judges | Two blinded Claude Opus sessions; judge A primary, judge B reported beside it | user (pilot value) |
| 4 | Items | The same 12 items as the pilot (`tasks.yaml`): 6 tempting, 3 control, 3 immunology | user (pilot value) |
| 5 | Primary test | Two-sided Fisher's exact test on runs, no skill against `v2` forced | user (pilot value) |
| 6 | Multiple-testing family | None named. Only the primary test supports a claim; every other p-value is labelled exploratory and unadjusted | user (pilot value) |
| 7 | Runs with no rewrite | Excluded from the judged endpoint and reported by arm | user (pilot value) |
| 8 | Arms | No skill; skill `v2` forced (`tasks-forced.yaml`). No unforced arm | user (pilot value) |
| 9 | Replicates | 10 per item × model: 240 runs per arm, 480 in all | user, 2026-11-26 |
| 10 | Packet-shuffle seed | `20261102`. Model sampling has no seed; each run's model id and CLI version are recorded from `result.json` | user |
| 11 | Second gold labeller | The author re-labels all 60 claim ceilings blind to the existing labels; Cohen's kappa is reported, and items where labels differ are listed | user, 2026-11-26 |
| 12 | Gold synonym lists | Frozen as they are now. The post-result extension in commit `859f7c9` is disclosed. The sha256 of `gold.yaml`, `tasks.yaml` and `tasks-forced.yaml` is recorded below before the first run | user |
| 13 | Headline figure | Per-item dot plot: each of the 12 items as a pair of points (no skill, forced) joined by a line, over each arm's rate with a Wilson 95% interval | user |
| 14 | Legacy scores (80/80, 13/14) | Cited as development smoke tests with their limits; no claim rests on them | user |
| 15 | External-label validation | Not in the paper; future work | user |
| 16 | Drift and gate experiments | Not in the paper; the paper makes no long-session or gate claim | user |

## Power

Target: a halving of the run-level rate from the pilot's 20.8% (10 / 48) to 10.4%, two-sided
α = 0.05. Exact Fisher power with 240 runs per arm is 0.86 (computed in-session on
2026-11-26 by enumerating both binomial outcomes; 2 replicates gave 0.19, 8 gave 0.77, 12
gave 0.92). This treats runs as independent, as the primary test does. Runs cluster by item
(the pilot's `prose-results` had 7 / 12 runs above, the controls about 1 / 24), so the true
power is lower. That limit is stated in the paper.

## Analysis

1. Run both arms at 10 replicates with the frozen files. Commit the run folder under
   `results/<date>/` as for the second pass (`results/2026-11-13/README.md`).
2. Score with `score_prose.py`; judge with `judge_prompt.md`, two blinded Opus sessions.
3. Primary: run-level counts by arm, judge A, Fisher two-sided. Report the rate difference
   with a 95% interval.
4. Reported beside it, labelled exploratory: judge B; per model; per item; claim-level counts;
   qualifier retention; no-rewrite runs by arm.
5. Judge agreement: claims both judges rated, excluding no-rewrite runs.
6. Gold agreement: Cohen's kappa between the original and the blind second labels.
7. Figures, from a notebook that reads the committed tables: the headline per-item dot plot;
   judge agreement; kappa table fallback only with a stated reason.

## Regression-case runner (M30)

Also in the paper plan: a runner for `evals/cases.jsonl` that runs each case in a clean
session and has an Opus grader score the reply against the case's `expect` list. Results are
committed per release under `evals/results/<version>/` with model ids. The grader is the same
vendor as the model under test; the paper states this.

## Frozen file hashes

Recorded on 2026-11-26, at approval. A file whose hash differs at run time is a deviation.

| File | sha256 |
|---|---|
| `gold.yaml` | `43dc356798224cc0d12c04aea62bf1651de4f4b13e31fa3139d444ce0ffd6ae0` |
| `tasks.yaml` | `c5c61ab4fd7f8e14acfd8049fbc37ee4c875920bb2e1f914e993b4b4793dfdce` |
| `tasks-forced.yaml` | `cfd3380b1f4010ef7cb7df04e5971cfce9e9db0df512540ae7d28cf84045c9a2` |
| `judge_prompt.md` | `bcc9b4aa8e6f819b78679799ecb4dda56c91e65ffa395b2c4aa27aa4c436ff46` |
| `../skills/v2/` (tree) | `7e7dbf32b2484ad04ab96e810d502a3d0b1f249d` (git tree of commit `828456c`) |

## Change log

| Date | Change | Reason |
|---|---|---|
| 2026-11-26 | Plan approved | |
