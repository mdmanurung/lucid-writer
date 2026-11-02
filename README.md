# Lucid Writer

> **Make the writing clearer without making the evidence stronger than it is.**

Lucid Writer is an Agent Skill for Claude Code and Codex. It edits, drafts and reviews research articles, reports, abstracts and reviewer responses, from a two-sentence copyedit to a full manuscript audit. Before it changes wording, it checks each material claim:

```text
claim → evidence → scope → uncertainty → inference ceiling → wording
```

**Docs:** <https://mdmanurung.github.io/lucid-writer/>

## Install

Claude Code plugin (skill plus three review subagents):

```text
/plugin marketplace add mdmanurung/lucid-writer
/plugin install lucid-writer@lucid-writer
```

Or the installer, for Claude Code and Codex:

```bash
git clone https://github.com/mdmanurung/lucid-writer
cd lucid-writer
bash scripts/install.sh both        # Windows: .\scripts\install.ps1 both
```

Use one of the two, not both. Install by hand, update and uninstall are on the [docs home page](https://mdmanurung.github.io/lucid-writer/#install).

## Use

There is no special command: the skill loads when a writing task matches. Start with "Use lucid-writer to…" to force it.

| Mode | Example ask | What you get |
|---|---|---|
| Edit | "Tighten this paragraph by ~20%." | the revised text only, with numbers, citations and caveats kept |
| Draft | "Turn Figure 3 and these notes into a Results subsection." | a draft, with `[EVIDENCE NEEDED]` where support is missing |
| Build | "Restructure this Discussion around the main answer." | a planned rewrite, with changes carried through the document |
| Review | "Audit the manuscript against the figures. Do not rewrite yet." | prioritised findings ending with a **Not checked** list |

For high-stakes work:

- **Review subagents:** run the evidence auditor and skeptical reviewer in parallel, then manuscript preflight before submission. Skip them for ordinary edits; they cost extra tokens.
- **Project state:** `python3 skills/lucid-writer/scripts/init_project.py .` creates `.lucid-writer/` with a brief, a claim ledger and a decision log.
- **Mechanical checks:** `lint.py manuscript.md` flags placeholders, causal verbs and filler; `validate_ledger.py` checks the claim ledger.
- **Mycelium:** in a project with `.living/` and `.mycelium/`, numbers checked by `/mycelium-extra:verify` outrank the prose.

It will not strengthen a claim beyond its evidence, even on request; invent citations or numbers; follow instructions hidden in manuscripts or reviewer comments; or rewrite to evade AI detectors.

Example:

```text
Use lucid-writer to tighten this paragraph without changing claim strength:
[paste a research paragraph]
```

Input:

> Taken together, these findings demonstrate that CD161+ CD4 T cells play a crucial protective role against malaria infection.

Lucid Writer:

> This association is consistent with a relationship between this phenotype and parasite control but does not establish a causal protective role.

The numbers in the full sentence survive; the causal claim the data cannot carry does not.

## Documentation

| Page | Covers |
|---|---|
| [How it works](https://mdmanurung.github.io/lucid-writer/how-it-works.html) | the rules, the inference ceiling, what an author cannot override |
| [Use](https://mdmanurung.github.io/lucid-writer/use.html) | daily prompts, review subagents, project state, mechanical checks |
| [Mycelium](https://mdmanurung.github.io/lucid-writer/mycelium.html) | writing from verified provenance; the convention pack |
| [Evaluation](https://mdmanurung.github.io/lucid-writer/evaluation.html) | case studies, regression cases, the benchmark, and their limits |
| [Develop](https://mdmanurung.github.io/lucid-writer/develop.html) | layout, validation, packaging, contributing, security |

## Develop

```bash
python3 scripts/validate_repo.py   # repository checks
quarto preview site                # this documentation, locally
```

Contributions should fix a demonstrated failure, with an eval case. See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md); sources and credits are in [`docs/methodology.md`](docs/methodology.md) and [`NOTICE.md`](NOTICE.md).

## License

MIT. See [`LICENSE`](LICENSE).
