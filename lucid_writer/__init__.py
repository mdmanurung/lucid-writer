"""Packaging shim for the lucid-writer repository.

This repository is a Markdown Agent Skill plus agents, evals, and standard-library
helper scripts. It has no Python API and none is intended: the helpers under
``skills/lucid-writer/scripts/`` are command-line programs invoked by path, as
documented in the README, and they stay that way.

This module exists for one reason. ``acumen`` benchmarks a skill by building a venv with
the target package installed and then probing that the package actually imports
(``acumen.check._PROBE_CODE``), because a distribution whose metadata resolves is not
necessarily importable. A repository with no importable module fails that probe, and the
harness refuses to spend anything on a pass whose every cell would fail identically.

So this file carries the one thing a probe needs — ``__version__`` — and ``pyproject.toml``
reads it from here via ``[tool.hatch.version] path``. That makes this the single source of
the version string; ``scripts/validate_repo.py`` asserts the plugin manifests agree with
it, so the number cannot drift.

Deliberately no prose about the skill's guidance lives in here. Acumen scrubs a target venv
of agent-facing files so its no-skill baseline arm is genuinely skill-free; keeping this
module free of skill content means there is nothing here for that scrub to miss.
"""

__version__ = "1.4.0"
