#!/usr/bin/env python3
"""Initialize lightweight .research-writer state without overwriting existing files."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

TEMPLATE_MAP = {
    "project-brief.md": "brief.md",
    "claim-evidence-ledger.csv": "claims.csv",
    "extended-outline.md": "outline.md",
    "decisions.md": "decisions.md",
    "review-log.md": "review.md",
}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", default=".", help="Project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing state files")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    state_dir = project / ".research-writer"
    assets_dir = Path(__file__).resolve().parent.parent / "assets"

    state_dir.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for src_name, dst_name in TEMPLATE_MAP.items():
        src = assets_dir / src_name
        dst = state_dir / dst_name
        if dst.exists() and not args.force:
            skipped.append(dst_name)
            continue
        shutil.copyfile(src, dst)
        created.append(dst_name)

    print(f"Research Writer state: {state_dir}")
    if created:
        print("Created: " + ", ".join(created))
    if skipped:
        print("Kept existing: " + ", ".join(skipped))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
