# Prose bench, second pass (2026-11-13): committed evidence

Every number in "Results of the second pass" in `../../README.md` reruns from this folder.

## Contents

- `runs/`, `runs-forced/`: one folder per run (arm / split / model / item / rep) with acumen's
  `result.json` and the model's `answer.md`. Seven runs put their reply in chat instead;
  for those, `chat_answer.md` holds the first paragraph of the final message, which is what
  `score_prose.py` recovers from a transcript. Transcripts and trajectories are not committed:
  they hold local paths and are about 38 MB.
- `judge_packets.jsonl`: the 120 blinded packets the judges saw (no arm, no model).
- `judge_key.jsonl`: packet id to arm, model, item and rep.
- `judgements.jsonl` (judge A, primary) and `judgements_b.jsonl` (judge B).
- `score_mechanical.txt`: scorer output without verdicts. `score_judge_a.txt` and
  `score_judge_b.txt`: the same with each judge's verdicts joined.

## Rerun

From `bench/prose/`:

```bash
R=results/2026-11-13
T=$(mktemp -d) && cp $R/judgements.jsonl $T/
uv run --quiet --no-project --with pyyaml score_prose.py $R/runs $R/runs-forced --out $T > $T/out.txt
cmp $T/judge_packets.jsonl $R/judge_packets.jsonl && diff <(head -n -1 $T/out.txt) $R/score_judge_a.txt
```

The packets come out byte-identical because the shuffle is seeded (20261102).

## Counting rules

- Run-level counts (10 / 48 no skill, 6 / 46 forced) exclude the three runs with no rewrite,
  whose packets are `missing` for every claim.
- Judge agreement (276 of 280 claims) uses the same exclusion. Counting the 8 `missing`
  claims of those runs, on which both judges agree trivially, gives 284 of 288.
- The first pilot (2026-11-02; 15% against 22%) kept no runs, so its numbers cannot be rerun.
