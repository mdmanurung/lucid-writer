# Project state

Use `.lucid-writer/` only for substantial ongoing work.

```text
.lucid-writer/
├── brief.md
├── claims.csv
├── outline.md
├── decisions.md
├── review.md
└── voice.md        # optional
```

## Files

**brief.md** — the fields of `assets/project-brief.md`: question, current answer, contribution, evidence and its boundaries, nonclaims, known weaknesses, terminology, fixed decisions, source artifacts, priority.

**claims.csv** — material claim ↔ evidence ↔ scope ↔ inference ceiling ↔ status ↔ location ↔ qualifiers to keep (optional; `;`-separated) ↔ warrant (optional; central causal or mechanistic claims).

**evidence.csv** — optional. One row per piece of evidence with a locator a reviewer can open; takes precedence over the `evidence` column of `claims.csv`. Format and checks: `references/evidence.md`.

**outline.md** — paragraph contracts only where useful.

**decisions.md** — durable analysis/writing decisions and affected artifacts.

**review.md** — unresolved issues, severity, location, repair, verification.

**voice.md** — observed author/team preferences. Never overrides evidence or reporting rules.

To draft it from your own papers, run `python3 skills/lucid-writer/scripts/voice_profile.py paper1.md paper2.md --author "Name" --author-position first --out .lucid-writer/voice.md`. The script measures sentence length, punctuation and word rates, and copies verbatim sample sentences. Prefer, Avoid and terminology stay as prompts for the author. Use `--author-position other` when you are not first or sole author; the profile then warns that the text may reflect co-authors. A voice sets rhythm and wording only; it never adds claims, removes hedges or overrides evidence.

## Resume order

For macro work:

1. brief;
2. relevant claims;
3. affected outline region;
4. recent material decisions;
5. open review issues;
6. manuscript/source files needed for the task.

## Update rule

Store only information likely to matter again. Do not log transient wording alternatives or routine copyedits.

If project state conflicts with current verified evidence, the evidence wins; mark state stale and propagate the correction.
