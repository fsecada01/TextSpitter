# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
TextSpitter adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.0] - 2026-02-17

### Added
- `CONTRIBUTING.md` with development setup, testing, and code-style guidelines
- `tests/test_cli.py` — comprehensive CLI test suite (stdout, `-o` flag, error handling, encoding)
- `tests/test_txt.py` — replaces `txt_test.py`; clarifies WordLoader vs FileExtractor input contracts
- `__all__` in `TextSpitter/__init__.py` (`TextSpitter`, `WordLoader`, `__version__`)
- `ty` pre-commit hook for static type checking on every commit

### Changed
- `WordLoader.__init__` now accepts `str | Path | None` only; `str` is converted to `Path` automatically. Stream inputs (`BytesIO`, `SpooledTemporaryFile`, `bytes`) belong on `FileExtractor` directly.
- `WordLoader.file_load()` return type annotated as `-> str`
- `TextSpitter()` convenience function return type annotated as `-> str`
- `FILE_EXT_MATRIX` type narrowed from `dict` to `dict[str, str]`
- `TEXT_MIME_TYPES` type narrowed from `frozenset` to `frozenset[str]`
- `PROGRAMMING_EXTENSIONS` type narrowed from `frozenset` to `frozenset[str]`
- `WordLoader` docstring rewritten; "CBO" jargon removed
- `csv_file_read` dead `newline` parameter removed
- Legacy `requirements.txt`, `core_requirements.txt`, `dev_requirements.txt`, `core_requirements.in`, `dev_requirements.in` removed — install exclusively via `pyproject.toml` and `uv`
- Python version matrix updated: 3.12 – 3.14 (dropped 3.9 – 3.11)
- README project-structure section updated to reflect `TextSpitter/guide/` subpackage

### Fixed
- README dead link to `CONTRIBUTING.md` (file now exists)

---

## [0.4.0] - 2026-02-17

### Added
- `[project.scripts]` CLI entry point (`textspitter` command)
- `TextSpitter/cli.py` with argparse-based argument parsing and `-o`/`--output` flag
- Optional `loguru` dependency (`pip install "textspitter[logging]"`)
- `py.typed` marker (PEP 561) for typed-package support
- pdoc documentation infrastructure published to GitHub Pages
- GitHub Actions test matrix (Python 3.12 – 3.14)
- GitHub Actions docs workflow (GitHub Pages via pdoc + syn dracula theme)
- `TextSpitter/guide/` documentation subpackage (overview, quickstart, tutorial, usecases, recipes)
- `tests/conftest.py` with dual-mode `log_capture` fixture (loguru or stdlib)

### Changed
- `loguru` moved from required to optional dependency
- `[build-system]` table added to `pyproject.toml`
- `__version__` now derived from `importlib.metadata`
- Constants in `FileExtractor` and `WordLoader` promoted to class-level
- `text_file_read` and `csv_file_read` deduplicated via shared `_decode_bytes` helper
- Logging unified through `TextSpitter/logger.py`
- Bare `Exception` raises replaced with `ValueError`
- `FileExtractor` type annotations tightened (`cast(BinaryIO, ...)` for stream operations)
- `PROGRAMMING_EXTENSIONS` extended to 50+ file types

---

## [0.3.6] - 2024-01-15

### Changed
- Maintenance release; dependency updates

---

## [0.3.5] - 2023-11-20

### Added
- Support for `SpooledTemporaryFile` input in `FileExtractor`

### Fixed
- PDF stream handling when PyMuPDF unavailable

---

## [0.3.3] - 2023-09-10

### Added
- Programming-language file support via `code_file_read()`
- `PROGRAMMING_EXTENSIONS` frozenset with 30+ extensions

---

## [0.3.2] - 2023-07-05

### Fixed
- Encoding cascade in `text_file_read`: UTF-8 → latin-1 → UTF-8-replace

---

## [0.3.1] - 2023-05-18

### Added
- `BytesIO` support as `file_obj` input

---

## [0.3.0] - 2023-04-01

### Added
- `FileExtractor` class extracted from `WordLoader` as separate layer
- MIME-type fallback routing in `WordLoader.file_load()`

---

## [0.2.0] - 2022-12-10

### Added
- CSV file support
- `get_file_type` static method for MIME sniffing

---

## [0.1.0] - 2022-09-01

### Added
- Initial release
- PDF extraction via PyMuPDF with PyPDF fallback
- DOCX extraction via python-docx
- Plain-text (TXT) extraction
- `WordLoader` dispatcher class
- `TextSpitter()` convenience function
