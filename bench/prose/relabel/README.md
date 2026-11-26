# Blind second labelling of the gold ceilings

`relabel.html` is the page the author labels in (published as a private claude.ai artifact). It shows `data.json`: the 12 paragraphs and 29 gold claims under opaque ids, with no ceilings, no `tempted_toward` and no item names. `key.json` maps each claim id back to its `gold.yaml` item and claim index; it is not in the page.

Bias controls: a fixed seeded order (20261126) with no two neighbours from one paragraph; three blocks with breaks; 6 hidden repeats of block-1 claims at the end (intra-rater drift); time on screen per answer; a 0.7 s guard against a double press; no tally of answers shown.

Answers are stored with the page; Claude reads them back and computes Cohen's kappa against `gold.yaml` (ANALYSIS_PLAN.md row 11).
