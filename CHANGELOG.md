# Changelog

## [0.5.1] - 2026-09-18

### Changed

- Refined reviewer boundaries after a second seeded-error empirical evaluation.
- Evidence auditor now stays closer to claim-to-source mismatches.
- Skeptical reviewer now prioritizes hidden assumptions and alternatives over literal numeric/source discrepancies.
- Manuscript preflight now stays focused on release consistency rather than reopening settled interpretation.
- All review subagents explicitly allow `no material findings` to reduce critique-for-critique's-sake.

### Evaluated

- Added a 14-issue synthetic manuscript fixture spanning evidence fidelity, inferential reasoning, and cross-artifact release consistency.
- Added clean negative controls and an unavailable-citation control.
- In the same-session role-conditioned retest, each specialist detected 100% of seeded issues in its target domain with zero clean-control false positives; evidence/skeptical overlap fell from 15.4% to 7.7%.

## [0.5.0] - 2026-09-18

### Added

- Three optional, narrow, read-only research-review subagents: evidence auditor, skeptical reviewer, and manuscript preflight.
- Native Claude Code plugin agent definitions under `agents/`.
- Native Codex custom-agent definitions under `.codex/agents/`.
- `docs/subagents.md` with orchestration rules, activation thresholds, and examples.
- Installer support for subagents, plus a `--skill-only` / `-SkillOnly` option.

### Changed

- Added a small optional-subagent routing section to `SKILL.md`; routine edits remain single-agent.
- Installers now deploy platform-specific reviewer agents without replacing unrelated user agent files.
- Repository validation now checks Claude and Codex subagent definitions.

## [0.4.1] - 2026-09-18

### Changed

- Added an auditable paired baseline-versus-skill output test with eight fixed research-writing cases.
- Added a strict post-hoc audit rather than accepting the initial skill scores at face value.
- Preserved design/method context when it affects interpretation.
- Added measurement/terminology fidelity to prevent compression such as `library size` → `yield`.
- Retested the two detected skill failures after the narrow patch.

All notable changes to Research Writer will be documented here.

## [0.4.0] - 2026-09-18

### Changed

- Reduced `SKILL.md` to a compact invariant/router layer.
- Consolidated argument + section guidance into `structure.md`.
- Consolidated coherence + concise style + generic-model cleanup into `prose.md`.
- Removed duplicated runtime guidance and moved methodological provenance out of the runtime reference set.
- Unified mechanical prose checks into a single `lint.py`.
- Tightened the minimum-intervention rule for everyday edits.

### Added

- Failure-oriented adversarial test suite.
- Explicit evaluation rubric with critical-fail conditions.
- Controlled before/after output review covering causal inflation, generic model-like prose, non-significance, and false coherence bridges.
- Regression cases for non-significance ≠ equivalence, transition-as-claim, and stale-state conflicts.

## [0.3.0] - 2026-09-18

### Added

- Dedicated five-layer coherence workflow inspired by `ericmjl/skills/coherent-writing`, adapted for evidence-bounded research prose.
- `references/coherence.md` with separate whole-draft, within-paragraph, section-boundary, paragraph-boundary, and final-audit checks.
- `references/llm-trace.md` for safe cleanup of generic model-like prose without detector-evasion claims.
- Conservative `style_trace_lint.py` that flags review cues but never classifies authorship.
- Corpus-based provenance for LLM-associated scientific-writing vocabulary and explicit warning against banned-word logic.
- Regression evals for coherence without new claims, safe LLM-trace cleanup, and marker-word false positives.
- `NOTICE.md` documenting the upstream coherent-writing inspiration and license.

### Changed

- Expanded the main audit sequence to separate coherence from style cleanup.
- Added stronger safeguards against synonym spinning, artificial quirks, fake errors, and removal of legitimate scientific hedging.
- README now documents coherence mode, LLM-trace cleanup, the style-trace linter, and its limitations.


## [0.2.0] - 2026-09-18

### Changed

- Rewrote README around an explicit installation, verification, update, uninstall, and security guide.
- Clarified standalone-skill versus plugin installation paths.
- Added explicit implicit-invocation metadata for OpenAI-compatible clients.
- Added source-of-truth precedence for conflicting evidence, state, and manuscript prose.
- Added a minimum-necessary-edit rule for everyday copyediting.
- Expanded manuscript review to cover transparency and reproducibility items where relevant.

### Added

- Optional author/team voice-profile template that cannot override evidence or reporting rules.

## [0.1.0] - 2026-09-18

### Added

- Initial `research-writer` Agent Skill.
- Portable Agent Plugins manifest plus Claude Code and Codex compatibility manifests.
- Micro/meso/macro/review task routing.
- Claim–evidence and inference-ceiling workflow.
- Extended-outline and persistent project-state templates.
- Argument, evidence, section, style, review, and project-state references.
- Project initializer, manuscript lint, and claim-ledger validator.
- Trigger/edge-case eval set.
- GitHub Actions validation workflow.
- Study-design reporting-guideline routing using current authoritative sources.
- Cross-platform convenience installers for Codex and Claude Code.
