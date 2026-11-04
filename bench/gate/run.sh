#!/usr/bin/env bash
# Release gate: run before opening a PR that changes hooks/rules/ or the skill.
# Usage: bench/gate/run.sh [--setups prose,full] [--voice path/voice.md] [--runs 3]
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=$(command -v python3.11 || command -v python3)
exec "$PY" bench/gate/gate.py "$@"
