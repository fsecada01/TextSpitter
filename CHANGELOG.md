# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-02-17

### Added
- Added CHANGELOG.md
- Added `[project.scripts]` CLI entry point (`textspitter` command)
- Added `TextSpitter/cli.py` with argument parsing
- Added optional `loguru` dependency (`pip install textspitter[logging]`)
- Added `py.typed` marker for typed package support
- Added pdoc documentation infrastructure
- Added GitHub Actions test matrix (Python 3.9–3.12)
- Added GitHub Actions docs workflow (GitHub Pages via pdoc)

### Changed
- Bumped version to 0.4.0
- Fixed README testing section placeholder
- Updated roadmap (marked TDB done)
- `loguru` moved from required to optional dependency
- `[build-system]` table added to `pyproject.toml`
- `__version__` now uses `importlib.metadata`
- Constants in `FileExtractor` and `WordLoader` promoted to class-level
- `text_file_read` and `csv_file_read` deduplicated via shared `_decode_bytes` helper
- Logging unified through `TextSpitter/logger.py`
- Bare `Exception` raises replaced with `ValueError`
