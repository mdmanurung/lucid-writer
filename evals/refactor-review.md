# v0.4 refactor review

This review compares v0.4 against the packaged v0.3 release. Word counts are whitespace-token counts used only as a prompt-bloat proxy.

| Runtime surface | v0.3 | v0.4 | Change |
|---|---:|---:|---:|
| `SKILL.md` words | 1,901 | 909 | -52.2% |
| Runtime reference words | 6,767 | 2,088 | -69.1% |
| Skill + runtime references | 8,668 | 2,997 | -65.4% |
| Runtime reference files | 10 | 6 | -4 |
| Skill helper scripts | 4 | 3 | -1 |

## What was removed or merged

- `argument.md` + `sections.md` → `structure.md`
- `style.md` + `coherence.md` + `llm-trace.md` → `prose.md`
- `reporting-guidelines.md` → shorter `reporting.md`
- runtime `sources.md` → non-runtime `docs/methodology.md`
- `manuscript_lint.py` + `style_trace_lint.py` → one conservative `lint.py`

## Adversarial review findings

The stress tests identified four rules worth keeping in the always-loaded skill:

1. **Evidence precedence:** current verified source artifacts override stale manuscript/project state.
2. **Transition-as-claim:** coherence edits cannot invent causal/mechanistic relations.
3. **Non-significance guard:** `p > threshold` does not establish equivalence or no effect.
4. **Minimum intervention:** local editing should remain local unless accuracy requires more.

Most stylistic detail did **not** need to remain in `SKILL.md`; it is now loaded only through `prose.md`.

## Output review

See `before-after-review.md` for controlled examples and `adversarial-results.md` for the in-session smoke test. The key observation is that evidence-safe revisions can sometimes be slightly longer than generic polishing because a necessary caveat carries information. Concision is therefore optimized **subject to scientific fidelity**, not as raw word minimization.

## Remaining limitation

The current adversarial run is not an independent benchmark: the same model/session helped develop and inspect the skill. External validation should run fresh sessions across Claude Code and Codex (and, ideally, multiple models) with blinded human scoring using `rubric.md`.
