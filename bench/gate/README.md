# Release gate

Run before opening a pull request that changes `hooks/rules/` or the skill. The gate result goes in the PR description.

```bash
bench/gate/run.sh                                  # prose and full, 3 runs × 2 abstracts
bench/gate/run.sh --setups full,full_voice --voice ~/.claude/lucid-writer/voice.md
```

It rewrites `abstracts/helminth.txt` and `abstracts/education.txt` with clean `claude -p` runs: no user settings, plugins, hooks or CLAUDE.md, and only the system prompt differs between setups. The system prompts are built from the rule files in this checkout. One more clean run codes every output blind against the original, using the claims in `abstracts/claims.json`.

| Exit | Meaning |
|---|---|
| 0 | pass: no `full` setup kept a causal C1 or strengthened C2 |
| 1 | fail: at least one `full` run did |
| 2 | inconclusive: fewer than 2 coded runs for some setup and abstract |

`prose` is reported, not gated: it has no evidence rules. Runs blocked by a safety classifier are counted, not retried. The biology abstract may be blocked as biology content; the education abstract keeps the gate decidable. Outputs land in `bench/gate/runs/<timestamp>/`, which git ignores. Each run is about 50 `claude -p` calls and takes about 10 minutes.

Both abstracts are generated for this gate. `helminth.txt` copies the claim structure of a real immunology abstract (an observed difference stated as "This affected the … axis", a conclusion that "shapes"); `education.txt` has a causal link from self-report and a policy conclusion from a non-randomised comparison.
