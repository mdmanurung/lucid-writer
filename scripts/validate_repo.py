#!/usr/bin/env python3
"""Repository integrity checks for Research Writer."""

from __future__ import annotations

import ast
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "research-writer" / "SKILL.md"

def fail(message: str) -> None:
    raise AssertionError(message)

def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML-like frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter is not closed")
    body = text[4:end]
    data = {}
    for line in body.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"Invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

def main() -> int:
    portable = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    if portable["name"] != "research-writer":
        fail("portable plugin name mismatch")
    if claude["name"] != portable["name"] or codex["name"] != portable["name"]:
        fail("plugin manifests must use the same name")
    if claude.get("version") != portable.get("version") or codex.get("version") != portable.get("version"):
        fail("plugin manifest versions must match")

    skill_text = SKILL.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)
    if fm.get("name") != "research-writer":
        fail("SKILL.md name mismatch")
    if len(fm.get("description", "")) < 80:
        fail("SKILL.md description is too vague")

    openai_meta = (SKILL.parent / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "allow_implicit_invocation: true" not in openai_meta:
        fail("OpenAI skill metadata should allow implicit invocation for everyday use")

    required_refs = [
        "structure.md", "evidence.md", "prose.md",
        "review.md", "reporting.md", "project-state.md"
    ]
    ref_dir = SKILL.parent / "references"
    for name in required_refs:
        if not (ref_dir / name).is_file():
            fail(f"missing reference: {name}")

    required_assets = [
        "project-brief.md", "extended-outline.md",
        "claim-evidence-ledger.csv", "decisions.md", "review-log.md", "voice-profile.md"
    ]
    asset_dir = SKILL.parent / "assets"
    for name in required_assets:
        if not (asset_dir / name).is_file():
            fail(f"missing asset: {name}")

    # Ensure every explicit reference path mentioned in SKILL.md exists.
    for rel in re.findall(r"`(references/[^`]+)`", skill_text):
        if not (SKILL.parent / rel).exists():
            fail(f"SKILL.md references missing file: {rel}")

    # Parse shipped Python scripts.
    py_files = list((SKILL.parent / "scripts").glob("*.py")) + list((ROOT / "scripts").glob("*.py"))
    for path in py_files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    if not (ROOT / "evals" / "README.md").is_file():
        fail("missing evals/README.md")
    if not (ROOT / "NOTICE.md").is_file():
        fail("missing NOTICE.md attribution/provenance file")


    # Validate optional review subagents.
    claude_agents = ROOT / "agents"
    expected_claude_agents = {
        "research-evidence-auditor.md",
        "research-skeptical-reviewer.md",
        "research-manuscript-preflight.md",
    }
    actual_claude_agents = {p.name for p in claude_agents.glob("*.md")}
    if expected_claude_agents - actual_claude_agents:
        fail("missing Claude review subagent(s): " + ", ".join(sorted(expected_claude_agents - actual_claude_agents)))
    for path in [claude_agents / name for name in sorted(expected_claude_agents)]:
        text = path.read_text(encoding="utf-8")
        fm_agent = parse_frontmatter(text)
        if not fm_agent.get("name") or not fm_agent.get("description"):
            fail(f"invalid Claude subagent frontmatter: {path.name}")
        if "edit files" not in text.lower() and "do not rewrite" not in text.lower():
            fail(f"Claude review subagent should be explicitly non-editing: {path.name}")

    codex_agents = ROOT / ".codex" / "agents"
    expected_codex_agents = {
        "research_evidence_auditor.toml",
        "research_skeptical_reviewer.toml",
        "research_manuscript_preflight.toml",
    }
    actual_codex_agents = {p.name for p in codex_agents.glob("*.toml")}
    if expected_codex_agents - actual_codex_agents:
        fail("missing Codex review subagent(s): " + ", ".join(sorted(expected_codex_agents - actual_codex_agents)))
    for path in [codex_agents / name for name in sorted(expected_codex_agents)]:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        for key in ("name", "description", "developer_instructions"):
            if not data.get(key):
                fail(f"Codex subagent {path.name} missing {key}")
        if data.get("sandbox_mode") != "read-only":
            fail(f"Codex review subagent must use read-only sandbox: {path.name}")

    if not (ROOT / "docs" / "subagents.md").is_file():
        fail("missing docs/subagents.md")

    # Validate JSONL evals.
    eval_path = ROOT / "evals" / "cases.jsonl"
    count = 0
    with eval_path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            item = json.loads(line)
            for key in ("id", "prompt", "should_trigger", "expect"):
                if key not in item:
                    fail(f"eval line {line_no} missing {key}")
            count += 1
    if count < 8:
        fail("eval set is too small")

    print(f"Repository OK: {count} eval cases; {len(py_files)} Python scripts parsed.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
