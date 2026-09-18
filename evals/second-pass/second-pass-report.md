# Second empirical evaluation pass — skill + subagents

Date: 2026-09-18

## Question

Do the optional review subagents add useful signal beyond the already-strong core `research-writer` skill, and do they do so without producing noisy or fabricated critiques?

## Design

A frozen synthetic CHMI manuscript package was created with **14 seeded material issues** distributed across three domains:

- **Evidence/source fidelity:** 5
- **Argument/inference:** 4
- **Release/cross-artifact consistency:** 5

The package contains a source-of-truth analysis note, manuscript, figure caption, supplement, reviewer response, and a clean negative-control passage.

Outputs were produced in this session under four instruction conditions:

1. core Research Writer review;
2. evidence auditor;
3. skeptical reviewer;
4. manuscript preflight.

A second negative-control test required all three reviewers to inspect a passage with no seeded defect. An unavailable-citation control tested whether the evidence auditor would say `cannot verify` rather than invent a source.

This is a **same-model, same-session role-conditioned test**, not an independent model benchmark. The fixtures, exact outputs, and gold-standard issue list are saved in this directory for replication.

## v0.5.0 findings

| Condition | Recall on its intended seeded domain | Clean-control false positives |
|---|---:|---:|
| Core skill across all 14 issues | 13/14 (92.9%) | n/a |
| Evidence auditor | 5/5 (100%) | 0 |
| Skeptical reviewer | 4/4 (100%) | 0 |
| Manuscript preflight | 5/5 (100%) | 0 |

The evidence auditor and skeptical reviewer had only **2 overlapping findings across 13 unique findings** (Jaccard overlap 0.154), indicating reasonable specialization. The core skill was already strong enough that subagents provide **incremental assurance rather than a prerequisite for good writing**.

### Failure found

The skeptical reviewer spent one finding on the statement that PC1/PC2 checks do not prove that all batch effects were eliminated. That is correct, but it is primarily a literal evidence-boundary issue and duplicates the evidence auditor's job.

The review prompts also lacked an explicit statement that returning **no material findings is valid**, which can encourage critique agents to search for a flaw merely because they were invoked.

## v0.5.1 revision

The subagent prompts were narrowed:

- **Evidence auditor:** stays close to claim ↔ source mismatches; does not develop broad alternative explanations unless needed to show why a claim exceeds the evidence.
- **Skeptical reviewer:** focuses on hidden assumptions, alternative explanations, and inferential structure; avoids straightforward numeric/source mismatches unless central.
- **Preflight:** focuses on release consistency and does not reopen settled interpretation unless a cross-artifact mismatch or blocker remains.
- **All reviewers:** explicitly permit `no material findings`.

## v0.5.1 retest

| Reviewer | Intended-domain recall | Clean-control false positives |
|---|---:|---:|
| Evidence auditor | 5/5 (100%) | 0 |
| Skeptical reviewer | 4/4 (100%) | 0 |
| Manuscript preflight | 5/5 (100%) | 0 |

Evidence/skeptical overlap fell to **1 finding across 13 unique findings** (Jaccard 0.077). The remaining overlap is the central causal/mechanistic inference, which is appropriate for both an evidence audit and an argument review.

The unavailable-citation control produced **0 fabricated citations** and explicitly returned `cannot verify`.

## Interpretation

1. **Keep subagents optional.** The core skill found 92.9% of seeded issues by itself. The extra model calls are not justified for routine edits.
2. **The strongest value is independent role separation, not raw recall.** Each specialist found all seeded issues in its target domain while the clean control remained quiet.
3. **Parallel evidence + skeptical review is efficient for high-stakes drafts.** Their overlap is low enough that they contribute different information.
4. **Preflight belongs at the end.** It catches stale cross-artifact state that neither writing quality nor argument review is designed to own.
5. **No fourth subagent is justified by these results.** Citation, style, or section-specific subagents would mostly duplicate existing responsibilities.

## Limitations

- Same model/session produced and evaluated the outputs.
- Synthetic fixture, not a complete real manuscript.
- Seeded issues are deliberately crisp and may overestimate recall.
- No latency/token-cost benchmark was possible inside this environment.
- External blinded scoring and fresh-context multi-model replication remain necessary before making general performance claims.

## Recommendation

Retain the architecture:

```text
routine work
    → core skill only

substantial/high-stakes draft
    → core skill
    → evidence auditor + skeptical reviewer in parallel
    → main-agent reconciliation/revision

stable release candidate
    → manuscript preflight
```

Do not add more agents unless a future benchmark demonstrates a distinct failure domain that the existing three miss.
