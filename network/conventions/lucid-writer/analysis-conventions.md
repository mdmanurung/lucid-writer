# Lucid Writer conventions

Write a Markdown manuscript, manuscript section or reviewer response from completed analyses with the lucid-writer skill. The skill owns the writing rules; this file only routes to it and fixes the order of checks. It duplicates no rule.

Boundary: `/mycelium-extra:analysis-report` owns Quarto analysis reports (`reports/<name>.qmd`); `/mycelium:report` with `report-generator` owns LaTeX PDF reports. This pack covers manuscripts written for journals or collaborators.

## 0. Check the skill is installed

Look for `~/.claude/skills/lucid-writer/SKILL.md`, `~/.agents/skills/lucid-writer/SKILL.md`, or the `lucid-writer` plugin. If none is present, stop and tell the user:

```bash
git clone https://github.com/mdmanurung/lucid-writer && bash lucid-writer/scripts/install.sh claude
```

## 1. Establish the source of truth

Follow the skill's `SKILL.md` step 1. In this repository the order is: `<analysis>/provenance/` (`verify-<hash>.md` claims verdicts, `outputs-<hash>.tsv` producers), then `<analysis>/outputs/numbers.json` and `<!-- claims -->` blocks, then `.living/findings/`, then existing prose.

## 2. Draft

Run lucid-writer in Build mode on `analysis/<name>/reports/<name>-manuscript.md`, or on the file the user names. Keep a claim ledger in `.lucid-writer/claims.csv` only for a long-running manuscript.

## 3. Bind evidence

- Every reported number is a `<value> | <file> <column> [<row>]` line in the document's `<!-- claims -->` block. Each cited file must be an output of the plan whose hash you will verify.
- Every figure cited as evidence has a producer in `outputs-<hash>.tsv` and follows plot-first's conclusion format, tag at line end.
- Gaps stay marked `[EVIDENCE NEEDED]` or `[CITATION NEEDED]`; never fill them to pass a check.

## 4. Release

1. `/mycelium-extra:verify` with `report <hash> --claims <document>`, once per plan hash the document cites. Add `--resolve-citations` when the bibliography has DOIs, PMIDs or arXiv IDs. Needs the mycelium-extra gate.
2. `/mycelium-extra:manuscript-audit` when `config/manuscript_checks.json` exists. Its checker needs `--config`; let that skill run it.
3. The lucid-writer manuscript preflight subagent, given the two results above.

Work through `qc-checklist.md` before calling the document ready.

## 5. Post-action

Update the analysis entry in `analysis/ANALYSIS_MANIFEST.md` with the document path and the preflight verdict. Log writing decisions to `.living/decisions.md` per the core post-action protocol.
