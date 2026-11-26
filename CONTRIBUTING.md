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

Run, with Python 3.11 or newer and Node on `PATH`:

```bash
node hooks/test.js
python skills/lucid-writer/scripts/rules.py --self-test
python skills/lucid-writer/scripts/voice_profile.py --self-test
python scripts/validate_repo.py
python skills/lucid-writer/scripts/lint.py --self-test
python skills/lucid-writer/scripts/validate_ledger.py skills/lucid-writer/assets/claim-evidence-ledger.csv
python skills/lucid-writer/scripts/validate_ledger.py --self-test
python skills/lucid-writer/scripts/qualifier_check.py --self-test
python bench/gate/gate.py --self-test
```

before submitting. CI runs the same steps on Python 3.11 and 3.12.

Never edit or overwrite a snapshot under `bench/skills/`. To benchmark a changed skill, copy it to a new `bench/skills/v<n+1>/` and record its source commit in `bench/skills/SNAPSHOTS.tsv`; `validate_repo.py` fails otherwise.
