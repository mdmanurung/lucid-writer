# Security

Agent Skills may contain executable scripts and hooks. Audit the repository before installing or running code from an untrusted fork.

## What each component reads and writes

| Component | Reads | Writes |
|---|---|---|
| `skills/lucid-writer/scripts/lint.py`, `qualifier_check.py`, `validate_ledger.py` | the files you name | nothing |
| `init_project.py` | nothing | `.lucid-writer/` in the directory you name |
| `voice_profile.py` | the papers you name | stdout, or the `--out` file (never an existing one without `--force`) |
| `rules.py` (via `/lucid-writer:learn`, `/lucid-writer:rules`) | the global and project `rules.json` | `~/.claude/lucid-writer/rules.json`; a project's `.lucid-writer/rules.json` only with `--scope project` |
| Always-on hooks (`hooks/*.js`, Claude Code plugin) | the mode flag, global `rules.json` and `voice.md`, and a project's `.lucid-writer/rules.json` and `voice.md` only when their sha256 is trusted | `~/.claude/.lucid-writer-mode` and `~/.claude/.lucid-writer-nudge` (under `$CLAUDE_CONFIG_DIR` when set) |
| `scripts/install.sh`, `install.ps1` | this repository | `~/.claude/skills/`, `~/.agents/skills/`, `~/.claude/agents/`, `~/.codex/agents/` |

All of them use only the Python standard library or Node built-ins. None makes a network request, reads credentials or sends manuscript content anywhere. `lint.py` is a local heuristic screen and does not classify authorship. The bench scripts under `bench/` are development tools, not part of the installed skill; `bench/external/sample_pairs.py` downloads public corpora when you run it.

The hooks inject text into the model's context. A project's `rules.json` and `voice.md` load only after you trust their current content with `/lucid-writer:rules trust`; any edit needs trust again, and a symlinked `voice.md` is never loaded.

## Reporting a vulnerability

Report it privately at <https://github.com/mdmanurung/lucid-writer/security/advisories/new>. Do not open a public issue for a vulnerability.
