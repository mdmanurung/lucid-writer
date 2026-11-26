# Architecture rationale

Lucid Writer is designed around six failure modes of agentic research writing.

## 1. Prose outruns evidence

A fluent model can strengthen a statement while "improving" it. The skill therefore treats claim strength as a controlled variable and introduces an inference ceiling before style editing.

## 2. Local edits break global consistency

A paragraph can improve while the Abstract, figure caption, or Discussion becomes stale. Macro work therefore includes a dependency/propagation pass.

## 3. One giant prompt wastes context

The skill uses progressive disclosure. `SKILL.md` contains the invariant workflow; specialized guidance lives under `references/`.

## 4. Editing and reviewing are different cognitive jobs

Review mode diagnoses and prioritizes before rewriting. This reduces the tendency to hide structural problems inside polished prose.

## 5. Deterministic checks should be code

Placeholder detection, schema validation, and broken local LaTeX references do not require language-model judgment. Small standard-library scripts handle them. Scientific validity remains a semantic task.

## 6. Text that reaches the model is data unless the user trusts it

Manuscripts, reviewer letters and project files can carry instructions. The skill treats all supplied text as data (non-negotiable 9), and every review subagent repeats that rule. The always-on hooks inject only what the user chose: global rules they approved, and a project's `rules.json` or `voice.md` only after `/lucid-writer:rules trust` records its sha256. Any edit to a trusted file needs trust again, and a symlinked voice never loads. Learned rules are injected below the evidence rules and say they cannot loosen them.

## Everyday ergonomics

The skill deliberately scales down as well as up.

A two-sentence grammar edit should take one pass. A full manuscript should recover project state, check reporting requirements, align claims and evidence, propagate changes, and run release checks.

This "right-sized rigor" is the central usability constraint.
