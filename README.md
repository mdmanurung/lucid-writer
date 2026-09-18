# Research Writer

Research Writer remains a lean everyday skill, with **optional isolated subagents** for evidence audit, adversarial review, and final preflight.

**Research Writer** is a focused Agent Skill for everyday research writing: articles, reports, abstracts, reviewer responses, and manuscript review.

> **Make the writing clearer without making the evidence stronger than it is.**

It scales from a two-sentence copyedit to a full manuscript audit. One compact `SKILL.md` holds the invariant rules; detailed guidance loads only when needed.

## Core priorities

1. **Evidence integrity**
2. **Argument**
3. **Reader comprehension**
4. **Concision**
5. **Surface polish**

The central control is:

```text
claim → evidence → scope → uncertainty → inference ceiling → wording
```

This prevents a common failure of generic rewriting: cleaner prose that quietly becomes a stronger scientific claim.

## What it handles

- sentence/paragraph editing with minimum necessary change;
- abstracts, Methods, Results, Discussion, and technical/scientific reports;
- claim–evidence, statistical, causal, and citation checks;
- argument restructuring and paragraph-level outlines when useful;
- coherence across sentences, paragraphs, and sections;
- removal of generic/model-like prose without detector-evasion tricks;
- manuscript and reviewer-response audits;
- cross-checking title, abstract, body, figures/tables, captions, and supplements;
- optional persistent state for long-running manuscripts;
- current study-design reporting-guideline checks.

## Runtime architecture

```text
SKILL.md
  ├─ structure.md       # argument + section logic
  ├─ evidence.md        # claims, stats, causality, citations
  ├─ prose.md           # coherence + concise style + model-like prose cleanup
  ├─ review.md          # critique + preflight
  ├─ reporting.md       # reporting completeness
  └─ project-state.md   # optional long-running state
```

Methodological sources are kept outside the runtime prompt in [`docs/methodology.md`](docs/methodology.md).

---

# Installation

For individual use, install the **skill** directly. Plugin manifests are included for distribution/testing, but the skill is the simplest path.

## Recommended: clone and install

### macOS / Linux

```bash
git clone <YOUR-GITHUB-REPO-URL> research-writer
cd research-writer
bash scripts/install.sh both  # skill + optional review subagents  # skill + optional review subagents
```

### Windows PowerShell

```powershell
git clone <YOUR-GITHUB-REPO-URL> research-writer
cd research-writer
.\scripts\install.ps1 both  # skill + optional review subagents  # skill + optional review subagents
```

Use `codex` or `claude` instead of `both` to install only one target.

The installer copies only `skills/research-writer/`. It has no external dependencies and makes no network requests beyond the `git clone` you run yourself.

## Codex

OpenAI currently documents user skills under:

```text
$HOME/.agents/skills
```

Manual install:

```bash
mkdir -p ~/.agents/skills
cp -R skills/research-writer ~/.agents/skills/research-writer
```

For a repository-scoped skill:

```bash
mkdir -p .agents/skills
cp -R /path/to/research-writer/skills/research-writer .agents/skills/research-writer
```

Codex scans `.agents/skills` from the current working directory up to the repository root and also reads user-level skills from `$HOME/.agents/skills`.

Official documentation: [OpenAI — Build skills](https://developers.openai.com/docs/build-skills)

## Claude Code

For a personal skill:

```bash
mkdir -p ~/.claude/skills
cp -R skills/research-writer ~/.claude/skills/research-writer
```

For plugin development/testing, the repository also includes `.claude-plugin/plugin.json`. Claude Code supports local plugin loading and marketplace-based distribution.

Official examples and skill specification: [Anthropic Agent Skills](https://github.com/anthropics/skills) and [Claude Code](https://github.com/anthropics/claude-code).

## Download without Git

1. On GitHub, choose **Code → Download ZIP**.
2. Extract the repository.
3. Copy `skills/research-writer/` to the appropriate skill directory above.
4. Start a new agent session and run the verification prompt below.

## Verify

```text
Use research-writer to tighten this paragraph without changing claim strength:
[paste a research paragraph]
```

Then test automatic routing:

```text
Review this Discussion for overclaiming, missing alternatives, and unnecessary repetition.
```

## Update

From a Git clone:

```bash
git pull
bash scripts/install.sh both  # skill + optional review subagents
```

Windows:

```powershell
git pull
.\scripts\install.ps1 both  # skill + optional review subagents
```

## Uninstall

Codex:

```bash
rm -rf ~/.agents/skills/research-writer
```

Claude Code:

```bash
rm -rf ~/.claude/skills/research-writer
```

---

## Daily use

No special command is required when the host supports automatic skill selection.

### Tighten prose

```text
Tighten this paragraph by ~20%. Preserve scientific meaning, numbers, citations, and caveats.
```

### Draft Results

```text
Turn Figure 3, this model table, and these notes into a concise Results subsection. Do not add literature or causal interpretation.
```

### Revise Discussion

```text
Restructure this Discussion around the main answer. Separate observation, interpretation, alternatives, limitations, and implications.
```

### Review a full manuscript

```text
Audit the manuscript against the figures, tables, and supplement. Prioritize evidence and argument problems before prose. Do not rewrite yet.
```

### Remove generic/LLM-like prose safely

```text
Remove generic AI/LLM-sounding prose. Preserve technical terminology, claim strength, uncertainty, numbers, and citations. Do not optimize for AI detectors.
```

See [`examples/quick-start.md`](examples/quick-start.md) for more examples.

## Optional review subagents

The core skill handles everyday writing directly. The repository also ships three **read-only** reviewers for high-stakes work:

| Reviewer | Role | Use it when |
|---|---|---|
| **Evidence auditor** | checks material claims against supplied analyses, figures/tables, protocols, and sources | substantial draft or claim audit |
| **Skeptical reviewer** | attacks the central argument, alternatives, scope, and inferential gaps | Discussion, major revision, pre-submission review |
| **Manuscript preflight** | checks stable title/abstract/body/figures/tables/supplement for stale or contradictory content | immediately before release |

Do **not** use subagents for grammar fixes, ordinary paragraph edits, or short sequential tasks. They consume extra tokens and are valuable mainly when independent context reduces anchoring or when many files must be reviewed.

Recommended workflow:

```text
draft / revise with Research Writer
        ↓
evidence auditor ─────┐
                      ├─ parallel, read-only
skeptical reviewer ──┘
        ↓
main agent reconciles + revises
        ↓
stable manuscript
        ↓
manuscript preflight
```

The main agent always owns edits. Reviewers return findings only.

See [`docs/subagents.md`](docs/subagents.md) for architecture, platform locations, and example prompts.

## Optional project state

For a substantial ongoing manuscript/report:

```bash
python skills/research-writer/scripts/init_project.py .
```

This creates:

```text
.research-writer/
├── brief.md
├── claims.csv
├── outline.md
├── decisions.md
└── review.md
```

Optionally copy `skills/research-writer/assets/voice-profile.md` to `.research-writer/voice.md` for stable author/team style preferences. Voice never overrides evidence or reporting requirements.

## Mechanical checks

The Python helpers use only the standard library.

```bash
# conservative release/style cues
python skills/research-writer/scripts/lint.py manuscript.md

# validate a claim ledger
python skills/research-writer/scripts/validate_ledger.py .research-writer/claims.csv

# validate repository structure
python scripts/validate_repo.py
```

The linter is **not an AI detector** and does not decide scientific validity.

## Safeguards

Research Writer explicitly guards against:

- citation, data, method, or statistic fabrication;
- association → causation drift;
- non-significance → equivalence claims;
- coherence transitions that invent scientific relationships;
- deleting valid hedges as “filler”;
- synonym-spinning technical terminology;
- “humanization” by fake errors or quirks;
- stale project notes overriding newer verified analyses;
- local edits leaving the Abstract/Discussion inconsistent with changed results.

## Testing

The repository contains both routine and adversarial evaluation material:

- [`evals/cases.jsonl`](evals/cases.jsonl) — routing and behavioral regression cases;
- [`evals/adversarial.md`](evals/adversarial.md) — failure-oriented stress tests;
- [`evals/rubric.md`](evals/rubric.md) — scoring rubric and critical-fail conditions;
- [`evals/before-after-review.md`](evals/before-after-review.md) — controlled output comparison;
- [`evals/adversarial-results.md`](evals/adversarial-results.md) — in-session safeguard smoke test;
- [`evals/refactor-review.md`](evals/refactor-review.md) — v0.3 → v0.4 bloat/focus review.

Repository validation checks files and scripts; it does **not** substitute for model-level evaluation. Run the behavioral cases on each target host/model before making performance claims.

## Repository layout

```text
research-writer/
├── plugin.json
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── skills/research-writer/
│   ├── SKILL.md
│   ├── references/
│   ├── assets/
│   └── scripts/
├── evals/
├── examples/
├── docs/
└── scripts/
```

## Design provenance

Research Writer is an original synthesis. Its design draws on Gopen & Swan, Mensh & Kording, Swales, Sword, Pinker, Minto, current reporting-guideline ecosystems, and public Agent Skill implementations including `ericmjl/skills/coherent-writing`.

Full references and licensing/provenance notes are in [`docs/methodology.md`](docs/methodology.md) and [`NOTICE.md`](NOTICE.md).

## Security

Audit third-party forks before installing executable skills. The bundled helpers use only the Python standard library, make no network requests, and write project files only when `init_project.py` is explicitly run. See [`SECURITY.md`](SECURITY.md).

## Contributing

Contributions should address demonstrated failure modes rather than add prompt bulk. Add or update an eval case for every material behavior change. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT. See [`LICENSE`](LICENSE).


## Paired output evaluation

The repository includes an auditable same-model A/B smoke test comparing generic academic editing with the skill on eight fixed cases. The strict audit found two minor semantic-compression errors in v0.4.0; both were patched and retested in v0.4.1.

See [`evals/paired-ab-test-2026-09-18.md`](evals/paired-ab-test-2026-09-18.md) for the exact prompts, outputs, scores, limitations, and retests.

This is not presented as an independent benchmark. The next recommended evaluation is fresh-session, multi-model, blinded scoring using the frozen cases.




### What the installer adds

For **Claude Code**:

```text
~/.claude/skills/research-writer/
~/.claude/agents/research-evidence-auditor.md
~/.claude/agents/research-skeptical-reviewer.md
~/.claude/agents/research-manuscript-preflight.md
```

For **Codex**:

```text
~/.agents/skills/research-writer/
~/.codex/agents/research_evidence_auditor.toml
~/.codex/agents/research_skeptical_reviewer.toml
~/.codex/agents/research_manuscript_preflight.toml
```

The custom agents are optional. Current Codex supports project-local `.codex/agents/` and user-level `~/.codex/agents/`; Claude Code supports custom subagents and plugin-bundled agents. The core skill does not depend on them.


## Second empirical evaluation

A second seeded-error evaluation specifically tests whether the optional subagents add useful signal beyond the core skill. The frozen fixture contains 14 known issues across evidence fidelity, inferential reasoning, and cross-artifact release consistency, plus clean negative controls.

In the same-session role-conditioned retest, the evidence auditor, skeptical reviewer, and manuscript preflight each detected **100% of the seeded issues in their intended domain**, with **zero clean-control false positives**. Evidence/skeptical overlap was 7.7%, supporting the current division of labor. The core skill alone had already found 13/14 issues, so subagents remain optional rather than default.

See [`evals/second-pass/second-pass-report.md`](evals/second-pass/second-pass-report.md) for the fixture, exact outputs, scoring, revisions, and limitations. This is a development smoke test, not an independent benchmark.
