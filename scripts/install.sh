#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-both}"
MODE="${2:-with-agents}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_SRC="$ROOT/skills/research-writer"

if [[ "$MODE" != "with-agents" && "$MODE" != "--skill-only" ]]; then
  echo "Usage: $0 [codex|claude|both] [--skill-only]" >&2
  exit 2
fi

install_skill() {
  local dest="$1"
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  cp -R "$SKILL_SRC" "$dest"
  echo "Installed skill -> $dest"
}

install_agent_files() {
  local src_dir="$1"
  local dest_dir="$2"
  local pattern="$3"
  mkdir -p "$dest_dir"
  local count=0
  for src in "$src_dir"/$pattern; do
    [[ -e "$src" ]] || continue
    cp "$src" "$dest_dir/$(basename "$src")"
    echo "Installed subagent -> $dest_dir/$(basename "$src")"
    count=$((count + 1))
  done
  [[ "$count" -gt 0 ]] || { echo "No subagent files found in $src_dir" >&2; exit 1; }
}

install_codex() {
  install_skill "${HOME}/.agents/skills/research-writer"
  if [[ "$MODE" != "--skill-only" ]]; then
    install_agent_files "$ROOT/.codex/agents" "${HOME}/.codex/agents" "*.toml"
  fi
}

install_claude() {
  install_skill "${HOME}/.claude/skills/research-writer"
  if [[ "$MODE" != "--skill-only" ]]; then
    install_agent_files "$ROOT/agents" "${HOME}/.claude/agents" "*.md"
  fi
}

case "$TARGET" in
  codex) install_codex ;;
  claude) install_claude ;;
  both) install_codex; install_claude ;;
  *) echo "Usage: $0 [codex|claude|both] [--skill-only]" >&2; exit 2 ;;
esac
