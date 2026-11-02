# Security

Agent Skills may contain executable scripts. Audit the repository before installing or running code from an untrusted fork.

Lucid Writer's bundled scripts:

- use only the Python standard library;
- make no network requests;
- do not read credentials;
- do not transmit manuscript content;
- `lint.py` performs local heuristic review only and does not classify authorship;
- write only when `init_project.py` is explicitly run.

Report security issues through the repository's private security-reporting mechanism when available.
