# Quick-start examples

These examples show the intended daily ergonomics.

## 1. One paragraph

```text
Use lucid-writer. Tighten this paragraph by about 25%.
Do not change the scientific meaning, statistical interpretation, or citations.

[paste paragraph]
```

Expected behavior: direct revision. No project scaffold.

## 2. Results from outputs

```text
Use lucid-writer to draft a Results subsection from the attached Figure 3,
model table, and analysis notes. Keep interpretation narrow and report effect
size/uncertainty where available. Do not add literature.
```

Expected behavior: evidence-first drafting and explicit flags for missing inputs.

## 3. Discussion

```text
Use lucid-writer to restructure this Discussion around the central answer.
Separate observation, interpretation, alternative explanations, limitations,
and implications. Do not strengthen causal language.
```

## 4. Extended outline

```text
Before drafting, build an extended outline. For every planned paragraph give:
function, claim, authorized evidence, inference ceiling, and bridge.
```

## 5. Full-manuscript review

```text
Review only; do not edit yet. Run five passes in order:
evidence, argument, interpretation/scope, reader/prose, and delivery.
Prioritize issues by scientific consequence.
```

## 6. Technical report

```text
Rewrite this report for a busy technical reader. Put the answer and key
findings first, then evidence, uncertainty, and methods. Keep the tone
plain and non-promotional.
```

## 7. Citation-safe revision

```text
Revise this literature paragraph. Verify any citation you add.
If you cannot verify a source, mark [CITATION NEEDED] instead of inventing one.
```

## 8. Project mode

```bash
python skills/lucid-writer/scripts/init_project.py .
```

Then:

```text
Use the .lucid-writer state to continue the manuscript.
Update the claim ledger only for material changes.
```


## 9. Coherence-only repair

```text
Use lucid-writer to make this section coherent. Diagnose whole-section conflicts,
within-paragraph logic, and paragraph/section boundaries separately. Do not add new
scientific claims, examples, or citations.
```

## 10. Generic LLM-trace cleanup

```text
Use lucid-writer to remove generic LLM-like phrasing from this Discussion while
preserving facts, statistics, citations, claim strength, uncertainty, and my voice.
Do not optimize for AI detectors or add artificial quirks.
```
