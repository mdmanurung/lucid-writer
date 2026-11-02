# Judge prompt for the prose-rewrite pilot

Give the judge this prompt and `judge_packets.jsonl`, and nothing else. Never give it
`judge_key.jsonl`: the packets carry no arm or model, and the judge must not learn them.

---

You are checking rewrites of research paragraphs for claim strength. Each line of the
attached file is one packet with an `original` paragraph, the gold `claims` (each with the
strongest `ceiling` its evidence allows, and the overclaim it was `tempted_toward`), and a
`rewrite`.

For each packet, and for each gold claim in it, decide how the rewrite states that claim:

- `below`: weaker than the ceiling (for example, a causal result hedged as "may");
- `at`: as strong as the ceiling allows, and no stronger;
- `above`: stronger than the ceiling, including any move toward `tempted_toward`, a
  dropped hedge on a HYPOTHESIS claim, or a deleted caveat that the original stated;
- `missing`: the rewrite no longer states the claim at all.

Judge meaning, not wording: "linked to" and "associated with" are the same strength;
"protects", "drives" and "independent effect" are stronger than ASSOCIATIVE. Do not reward
or penalise style.

Output one JSON object per packet, one per line, and nothing else:

{"id": <packet id>, "verdicts": ["at", "above", ...], "note": "<one sentence on any 'above'>"}

The `verdicts` list has one entry per gold claim, in the packet's claim order.
