"""
Command-line interface for textspitter.

Usage:
    textspitter FILE [FILE ...]
    textspitter FILE [FILE ...] -o OUTPUT
"""

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Entry point for the ``textspitter`` CLI command."""
    parser = argparse.ArgumentParser(
        prog="textspitter",
        description=(
            "Extract text from PDF, DOCX, TXT, CSV, and source-code files."
        ),
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to the file(s) to extract text from.",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Write extracted text to FILE instead of stdout.",
    )
    args = parser.parse_args()

    # Import here so the CLI fails gracefully if the package is broken
    from . import TextSpitter

    parts: list[str] = []
    errors: list[str] = []

    for file_path in args.files:
        try:
            text = TextSpitter(filename=file_path)
            parts.append(text)
        except Exception as exc:
            errors.append(f"Error processing {file_path!r}: {exc}")

    result = "\n".join(parts)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result)

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
