# Contributing

Contributions should improve reliability rather than add prompt bulk.

## Principles

1. Preserve the priority order: scientific integrity → argument → reader comprehension → concision → polish.
2. Add instructions only for recurrent failure modes.
3. Prefer a focused reference module over enlarging `SKILL.md`.
4. Use deterministic scripts only for mechanical tasks that code can check reliably.
5. Do not turn heuristic language/style preferences into scientific rules.
6. Do not add citation-generation behavior that can fabricate sources.
7. Add or update eval cases for every material behavior change.

## Pull requests

A pull request should state:

- failure mode addressed;
- representative prompt;
- expected behavior before/after;
- files changed;
- new or updated eval cases.

Run:

```bash
python scripts/validate_repo.py
python skills/lucid-writer/scripts/lint.py --self-test
python skills/lucid-writer/scripts/validate_ledger.py skills/lucid-writer/assets/claim-evidence-ledger.csv
```

before submitting.
