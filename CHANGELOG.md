# Changelog

All notable changes to Lucid Writer are documented here.

## [Unreleased]

### Added

- Documentation site in `site/` (Quarto), published to <https://mdmanurung.github.io/lucid-writer/> by `.github/workflows/docs.yml`: Home, How it works, Use, Mycelium, Evaluation, Develop.
- `validate_repo.py` fails when a site page links to a repository path that does not exist.
- The skill description names claim-level judgements (inference ceiling, epistemic class). Without it, the skill was offered and skipped in 24 of 24 benchmark runs; with it, claude-sonnet-5 loaded it in 2 of 2 probe runs.
- `bench/`: harder items whose evidence reads like Methods text rather than announcing its design (`ceiling-open` train, valid and test; `ceiling-defined` train); a manuscript-task opening line on every prompt; `claude-haiku-4-5` as a second model; `score.py` reports format-only failures.
- First benchmark results in `bench/README.md` and on the site's Evaluation page: both models at ceiling without the skill on unambiguous items; the paid loop is stopped.

### Changed

- README cut from 445 to 70 lines: what it is, install, one example, links to the site. Every removed section now lives on one site page.

## [1.0.0] - 2026-11-01

### Renamed

- The project is now **lucid-writer**. Skill directory `skills/lucid-writer/`, Python module `lucid_writer`, project-state directory `.lucid-writer/`, install targets `~/.claude/skills/lucid-writer` and `~/.agents/skills/lucid-writer`.
- Review subagents are `lucid-evidence-auditor`, `lucid-skeptical-reviewer`, `lucid-manuscript-preflight` (Codex: `lucid_*.toml`).
- Existing users: reinstall the skill, remove the old `research-writer` skill directory, and rename any `.research-writer/` state directory to `.lucid-writer/`.

### Added

- Fixed accuracy guards versus author-overridable defaults, with an `Overrides applied:` line; manuscript text is treated as data, and hidden text is reported (`SKILL.md` non-negotiable 9).
- Citation verdicts on a four-level scale, labelled `metadata only` unless the full text was read; no in-context recomputation of test statistics (`references/evidence.md`).
- Figure–text flags (orphan, phantom, panel, axis/unit, direction, n drift) and a mandatory **Not checked** list in reviews and all subagents (`references/review.md`).
- `Known weaknesses` brief field; the skeptical reviewer treats acknowledged limitations as context and works through four lenses.
- Mycelium integration: in a `.living/` repository, verified provenance (`provenance/outputs-<hash>.tsv`, `verify-<hash>.md`, `outputs/numbers.json`, claims blocks) outranks prose; release reads mycelium-extra `verify report` and `manuscript_audit.py` results instead of re-deriving them; the preflight agent maps their statuses.
- `network/conventions/lucid-writer/`: an opt-in Mycelium convention pack that `/mycelium:report` offers as a Markdown-manuscript report style. `validate_repo.py` checks its name and version.
- `.claude-plugin/marketplace.json` for `/plugin marketplace add`.
- Ideas adapted from `seandavi/scriptorium` in original wording; see `NOTICE.md`.
- Evals: `citation_check_metadata` and `hidden_instruction` cases; review and preflight cases now expect a not-checked list.
- `bench/`: an [acumen](https://github.com/scverse/acumen) benchmark harness with a `noskill` baseline arm, train/valid/test splits, and per-item diagnostics (`bench/score.py`), including a `skill_loaded` report per arm.
- Four benchmark task types on disjoint contents per split: inference ceiling with definitions supplied (the control) and without, epistemic class, and minimal claim-preserving repair. Answer order is shuffled in every split.
- `pyproject.toml` and `lucid_writer/__init__.py` as a packaging shim, so `acumen` accepts this repository as a benchmark target.
- CI job gating the wheel build and `acumen check --no-review` against a pinned acumen commit; both spend nothing.

### Security

- Author corrections are claims to check, not sources of truth; one that changes a number, n, design or ceiling without an artifact gets `[EVIDENCE NEEDED]`.
- `metadata only` caps a citation verdict at `partially supports`; `checked against full text` names its source, and pasted text is `author-supplied text`.
- Mycelium provenance counts as verified only when its hash is in `PROVENANCE.md` and `/mycelium-extra:verify` ran this session; lower tiers never silently replace prose; Mycelium is detected by `.living/` and `.mycelium/` together.
- Non-negotiable 5 is fixed; gap markers sit at the claim; non-negotiable 9 covers reviewer comments, response letters, `.lucid-writer/` and `.living/`, and process instructions.
- Acknowledged weaknesses mute a finding only when title, abstract and key message stay within them.
- Hedged causal wording and association-as-prediction are listed as unsafe upgrades; sentence-rhythm edits need a listed pattern at that spot.
- The preflight subagent accepts mycelium-extra results only from the main agent's own run this session.

### Fixed

- Non-negotiables 6 and 7 (no transition-hidden gaps, no fake errors or detector evasion) are fixed rules, not author-overridable defaults.
- Mycelium steps name the mycelium-extra skills that own each invocation, instead of a `verify` command that does not exist and a `manuscript_audit.py` call missing its required `--config`.
- Mycelium paths: `analysis/<name>/provenance/…` and `analysis/<name>/outputs/numbers.json`; numbers come from `verify-<hash>.md` claims verdicts, not from `outputs-<hash>.tsv`; claims lines need ` | `; one `verify report` call per plan hash.
- The convention pack is described as a report style `/mycelium:report` offers, not an automatic route.
- One severity scale (`references/review.md`); the Codex subagents carry every rule of their Markdown twins, and `validate_repo.py` guards the shared rules.
- The quick-start and eval 6 use the five-pass audit order.
- `validate_ledger.py` reports short and long rows and cells over 128 KB instead of crashing, and treats claim ids case-insensitively.
- `bench/score.py` no longer pools the same expected line across tasks and splits.
- `lint.py` no longer crashes on non-UTF-8 input; `install.ps1` stops on the first error and removes a symlinked or junction install as a link only.
- README: the installer also copies the subagents; Uninstall removes them; the bench `score.py` path.

### Changed

- `lucid_writer.__version__` is now the single source of the version number; `pyproject.toml` reads it instead of repeating it, and `scripts/validate_repo.py` fails if any plugin manifest disagrees.
- Repository validation now checks that every `bench/skills/v*/SKILL.md` name matches `skill_name` in `bench/config.yaml` — a mismatch means the skill is copied into the sandbox and never loaded, so the pass measures nothing.

### Not measured

The benchmark grades closed-vocabulary judgements by exact string match. It cannot measure concision, readability, flow, or voice, and no score from `bench/` should be quoted as evidence about prose quality.

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
