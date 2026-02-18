"""Build documentation with pdoc while preserving custom HTML pages.

This script generates API reference documentation for TextSpitter using pdoc,
while preserving custom HTML pages (landing page, guides, etc.) that are
maintained separately.

Usage:
    python docs/make.py
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Build documentation with pdoc and restore custom HTML pages."""
    docs_dir = Path(__file__).parent
    project_root = docs_dir.parent

    # Files to preserve during pdoc generation
    custom_files = ["index.html"]

    # Backup custom HTML files
    backups: dict[str, bytes] = {}
    for filename in custom_files:
        filepath = docs_dir / filename
        if filepath.exists():
            print(f"Backing up {filename}...")
            backups[filename] = filepath.read_bytes()

    # Run pdoc to generate documentation
    print("Generating API reference with pdoc...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pdoc",
                "TextSpitter",
                "-o",
                str(docs_dir),
            ],
            cwd=project_root,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running pdoc: {e}", file=sys.stderr)
        sys.exit(1)

    # Restore custom HTML files
    for filename, content in backups.items():
        filepath = docs_dir / filename
        print(f"Restoring {filename}...")
        filepath.write_bytes(content)

    print("Documentation built successfully!")


if __name__ == "__main__":
    main()
