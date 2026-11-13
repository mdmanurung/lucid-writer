#!/usr/bin/env python3
"""Repository integrity checks for Lucid Writer."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "lucid-writer" / "SKILL.md"

def fail(message: str) -> None:
    raise AssertionError(message)

def _declared_version(path: Path) -> str:
    """Read ``__version__`` out of a module without importing it."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                value = ast.literal_eval(node.value)
                if not isinstance(value, str) or not value:
                    fail(f"{path} must assign a non-empty string to __version__")
                return value
    fail(f"{path} does not assign __version__")

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

    if portable["name"] != "lucid-writer":
        fail("portable plugin name mismatch")
    if claude["name"] != portable["name"] or codex["name"] != portable["name"]:
        fail("plugin manifests must use the same name")
    if claude.get("version") != portable.get("version") or codex.get("version") != portable.get("version"):
        fail("plugin manifest versions must match")

    # The version now lives in exactly one place, lucid_writer/__init__.py, because
    # pyproject.toml reads it from there. Every other manifest must agree with it, so the
    # number cannot drift as files are added. Parsed with ast, not imported, to keep this
    # script dependency-free and safe to run on an unconfigured checkout.
    version = _declared_version(ROOT / "lucid_writer" / "__init__.py")
    for label, manifest in (("plugin.json", portable), (".claude-plugin", claude), (".codex-plugin", codex)):
        if manifest.get("version") != version:
            fail(
                f"{label} version {manifest.get('version')!r} does not match "
                f"lucid_writer.__version__ {version!r}"
            )

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if pyproject.get("project", {}).get("name") != portable["name"]:
        fail("pyproject.toml [project].name must match the plugin name")
    if "version" not in pyproject.get("project", {}).get("dynamic", []):
        fail("pyproject.toml must take its version from lucid_writer/__init__.py, not repeat it")

    # The Mycelium convention pack is installed by copy into users' `.living/`, and
    # mycelium:report compares its `version:` to spot stale installs, so it must track ours.
    pack = (ROOT / "network" / "conventions" / "lucid-writer" / "CONVENTION_PACK.yaml").read_text(encoding="utf-8")
    for key, want in (("name", portable["name"]), ("version", version)):
        found = re.search(rf"^{key}:\s*(\S+)\s*(?:#.*)?$", pack, flags=re.M)
        if not found or found.group(1).strip("\"'") != want:
            fail(f"CONVENTION_PACK.yaml {key} must be {want!r}")

    skill_text = SKILL.read_text(encoding="utf-8")
    fm = parse_frontmatter(skill_text)
    if fm.get("name") != "lucid-writer":
        fail("SKILL.md name mismatch")
    if len(fm.get("description", "")) < 80:
        fail("SKILL.md description is too vague")

    openai_meta = (SKILL.parent / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "allow_implicit_invocation: true" not in openai_meta:
        fail("OpenAI skill metadata should allow implicit invocation for everyday use")

    required_refs = [
        "structure.md", "evidence.md", "prose.md", "patterns.md",
        "review.md", "reporting.md", "project-state.md"
    ]
    ref_dir = SKILL.parent / "references"
    for name in required_refs:
        if not (ref_dir / name).is_file():
            fail(f"missing reference: {name}")

    required_assets = [
        "project-brief.md", "extended-outline.md",
        "claim-evidence-ledger.csv", "decisions.md", "review-log.md", "voice-profile.md",
        "reporting-preflight.csv",
    ]
    asset_dir = SKILL.parent / "assets"
    for name in required_assets:
        if not (asset_dir / name).is_file():
            fail(f"missing asset: {name}")

    preflight_header = (SKILL.parent / "assets" / "reporting-preflight.csv").read_text(encoding="utf-8").splitlines()[0]
    if preflight_header != "guideline,version,item_id,item,manuscript_location,status":
        fail("assets/reporting-preflight.csv header does not match references/reporting.md")

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
        "lucid-evidence-auditor.md",
        "lucid-skeptical-reviewer.md",
        "lucid-manuscript-preflight.md",
    }
    actual_claude_agents = {p.name for p in claude_agents.glob("*.md")}
    if expected_claude_agents - actual_claude_agents:
        fail("missing Claude review subagent(s): " + ", ".join(sorted(expected_claude_agents - actual_claude_agents)))
    for path in [claude_agents / name for name in sorted(expected_claude_agents)]:
        text = path.read_text(encoding="utf-8")
        fm_agent = parse_frontmatter(text)
        if not fm_agent.get("name") or not fm_agent.get("description"):
            fail(f"invalid Claude subagent frontmatter: {path.name}")
        if "do not edit" not in text.lower() and "do not rewrite" not in text.lower():
            fail(f"Claude review subagent should be explicitly non-editing: {path.name}")

    codex_agents = ROOT / ".codex" / "agents"
    expected_codex_agents = {
        "lucid_evidence_auditor.toml",
        "lucid_skeptical_reviewer.toml",
        "lucid_manuscript_preflight.toml",
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

    # The Codex twins are hand-kept copies of agents/*.md. A full diff is too strict (the
    # wording is condensed), so guard the rules that must survive in both copies.
    twin_rules = {
        "evidence_auditor": ["cannot verify", "metadata only", "Not checked", "sounds plausible"],
        "skeptical_reviewer": ["Known weaknesses", "a Limitations sentence does not settle it", "statistical", "Not checked", "Strongest surviving conclusion"],
        "manuscript_preflight": ["You cannot run these checks", "reports running it in this session", "cannot verify", "applies only to supplied materials", "not checked"],
    }
    for stem, phrases in twin_rules.items():
        md = (claude_agents / f"lucid-{stem.replace('_', '-')}.md").read_text(encoding="utf-8").lower()
        toml = tomllib.loads((codex_agents / f"lucid_{stem}.toml").read_text(encoding="utf-8"))["developer_instructions"].lower()
        for phrase in phrases:
            for label, body in (("agents", md), (".codex", toml)):
                if phrase.lower() not in body:
                    fail(f"{label} {stem} lost the rule containing {phrase!r}")

    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    if [plugin.get("name") for plugin in market.get("plugins", [])] != [portable["name"]]:
        fail("marketplace.json must list exactly the lucid-writer plugin")

    if not (ROOT / "docs" / "subagents.md").is_file():
        fail("missing docs/subagents.md")

    # The Acumen benchmark workspace, when present. Its own files are YAML and are validated
    # by `acumen check`, which is the tool that owns them; this only guards the one thing
    # that silently breaks a pass: a skill version whose frontmatter name does not match
    # `skill_name` in bench/config.yaml, which is copied into the sandbox and never loaded.
    bench = ROOT / "bench"
    bench_versions = 0
    if (bench / "config.yaml").is_file():
        for required in ("tasks.yaml", "README.md"):
            if not (bench / required).is_file():
                fail(f"missing bench/{required}")
        config_text = (bench / "config.yaml").read_text(encoding="utf-8")
        match = re.search(r"^skill_name:\s*(\S+)\s*$", config_text, flags=re.M)
        if not match:
            fail("bench/config.yaml must set skill_name")
        declared = match.group(1).strip("\"'")
        skills_root = bench / "skills"
        versions = sorted(p for p in skills_root.glob("v*") if p.is_dir()) if skills_root.is_dir() else []
        bench_versions = len(versions)
        if not versions:
            fail("bench/skills has no skill version to benchmark")
        for version_dir in versions:
            skill_md = version_dir / "SKILL.md"
            if not skill_md.is_file():
                fail(f"bench/skills/{version_dir.name} has no SKILL.md")
            name = parse_frontmatter(skill_md.read_text(encoding="utf-8")).get("name")
            if name != declared:
                fail(
                    f"bench/skills/{version_dir.name}/SKILL.md name {name!r} does not match "
                    f"skill_name {declared!r} in bench/config.yaml"
                )

    # tasks-forced.yaml is generated from tasks.yaml; a stale copy would run different paragraphs.
    forced = subprocess.run(
        [sys.executable, str(ROOT / "bench" / "prose" / "make_forced.py"), "--check"],
        capture_output=True, text=True,
    )
    if forced.returncode != 0:
        fail((forced.stdout + forced.stderr).strip() or "bench/prose/tasks-forced.yaml is stale")

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

    # The site links skill files by GitHub URL rather than copying them, and Quarto does not
    # check absolute URLs, so a renamed or deleted file would leave a dead link unnoticed.
    site_links = 0
    for page in sorted((ROOT / "site").glob("*.qmd")):
        text = page.read_text(encoding="utf-8")
        for rel in re.findall(r"github\.com/mdmanurung/lucid-writer/(?:blob|tree)/main/([^)\s#\"]+)", text):
            site_links += 1
            if not (ROOT / rel).exists():
                fail(f"site/{page.name} links to missing repository path: {rel}")

    print(
        f"Repository OK: v{version}; {count} eval cases; "
        f"{len(py_files)} Python scripts parsed; "
        f"{bench_versions} bench skill version(s)."
    )
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
