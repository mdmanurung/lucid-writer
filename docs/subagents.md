# Optional subagents

Research Writer remains one everyday skill. Three narrow, read-only subagents are included for high-stakes work where independent context improves review.

| Agent | Use when | Avoid for |
|---|---|---|
| evidence auditor | substantial draft; claim/evidence verification | routine copyediting |
| skeptical reviewer | Discussion; major revision; adversarial review | sentence polishing |
| manuscript preflight | stable manuscript before submission/preprint/circulation | active early drafting |

## Recommended orchestration

Ordinary writing uses the main skill only.

For a substantial draft, the evidence auditor and skeptical reviewer may run independently and in parallel. The main agent waits for both, reconciles evidence-backed findings, and makes the edits.

Run manuscript preflight only after substantive revisions are stable.

## Coordination contract

Subagents are read-only. They report findings rather than rewritten prose, do not create new evidence or citations, and classify unavailable support as unverifiable rather than guessing.

The main agent owns the manuscript, supplies explicit file scope when delegating, resolves reviewer conflicts from source evidence, and makes all edits.

## Claude Code

Canonical plugin agents are under:

```text
agents/
```

Manual user-level installation uses:

```text
~/.claude/agents/
```

Claude Code subagents run in isolated contexts with their own tool sets.

## Codex

Project-local custom agents are shipped under:

```text
.codex/agents/
```

User-level custom agents use:

```text
~/.codex/agents/
```

The included Codex agents use `sandbox_mode = "read-only"` and inherit compatible parent-session configuration.

## Example

```text
Use Research Writer to revise this Discussion. Then delegate an independent
evidence audit and skeptical review. Wait for both and reconcile only
evidence-backed findings before making the final revision.
```

```text
The manuscript is stable. Run the manuscript preflight across the main text,
figures, tables, captions, and supplement. Report blockers; do not rewrite.
```
