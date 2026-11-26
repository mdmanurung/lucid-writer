# AI usage disclosure

Lucid Writer is a set of instructions for AI coding agents, and AI agents helped build it. This page states which tools did what, as far as the repository records it.

## Code, rules and documentation

Of the 53 commits up to `69ffff9` (2026-09-18 to 2026-11-26), 40 carry a `Co-Authored-By` trailer for an Anthropic Claude model: Claude Opus 5.5 or Claude Sonnet 5.5, run in Claude Code. Commits without a trailer may also have had AI help; the trailers are a lower bound. [AUTHOR CHECK: state which parts you designed, wrote or rewrote by hand, for example the inference ladder, the non-negotiables and the eval fixtures.]

## Evaluation

- Prose bench rewrites: `claude-sonnet-5` and `claude-haiku-4-5` (`bench/prose/README.md`).
- Prose bench judges: two blinded Claude Opus sessions; judge A was `claude-opus-5` (`bench/prose/README.md`). Both judges come from the same vendor as the rewriters.
- Release gate: `claude-opus-5-5` rewrites and codes the abstracts (`bench/gate/gate.py`).
- Case studies and the second-pass review test in `evals/`: the same model produced and scored the outputs, as each report states.
- Gold claim ceilings in `bench/prose/gold.yaml`: one labeller. [AUTHOR CHECK: say whether you labelled them yourself, or a model proposed them and you checked them.]

## Release review

The 2.0.0 release review ran eight Claude Opus 5.5 reviewer agents and one Claude Fable 5.2 synthesis agent. Their findings were checked against the cited files before any fix was made. [AUTHOR CHECK: state what you reviewed by hand before release.]

## What the author is responsible for

[AUTHOR CHECK: one or two sentences on who made the design decisions and who reviewed each change before merge.]
