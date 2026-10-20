#!/usr/bin/env python3
"""Copy the growth workspace into an existing project without overwriting."""

import argparse
from pathlib import Path
import shutil
import sys


def initialize(project: Path) -> Path:
    source = Path(__file__).resolve().parent.parent / "growth"
    project = project.expanduser().resolve()
    if not project.is_dir():
        raise ValueError("The target project directory does not exist; create or clone the project first.")
    if project == source or source in project.parents:
        raise ValueError("Cannot initialize a project inside the template growth directory.")
    destination = project / "growth"
    if destination.exists() or destination.is_symlink():
        raise ValueError("The target already has a growth path; merge the template manually. Nothing will be overwritten.")
    # copytree also rejects destinations created after the preflight check.
    def exclude_local(folder, names):
        ignored = shutil.ignore_patterns(".local-data", "config.local.json", ".venv", "__pycache__", "*.py[cod]", ".env", ".env.*", "*.p8")(folder, names)
        ignored.discard(".env.example")
        ignored.update(name for name in names if (Path(folder) / name).is_symlink())
        return ignored

    shutil.copytree(source, destination, ignore=exclude_local)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Path to an existing target project")
    args = parser.parse_args()
    try:
        destination = initialize(args.project)
    except (OSError, ValueError) as error:
        print(f"Initialization failed: {error}", file=sys.stderr)
        return 1
    print(f"Template copied to: {destination}")
    print("Next: follow growth/SETUP.md in the target project to configure its context and first-cycle plan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
