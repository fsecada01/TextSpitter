# Contributing to TextSpitter

Thanks for taking the time to contribute! This guide covers everything you need to get started.

---

## Table of Contents

- [Development setup](#development-setup)
- [Running tests](#running-tests)
- [Code style and type checking](#code-style-and-type-checking)
- [Project structure](#project-structure)
- [Submitting changes](#submitting-changes)
- [Reporting bugs](#reporting-bugs)

---

## Development setup

TextSpitter uses [uv](https://docs.astral.sh/uv/) for dependency management.

```sh
# 1. Fork and clone
git clone https://github.com/fsecada01/TextSpitter.git
cd TextSpitter

# 2. Install all dependencies (editable install + dev extras)
uv sync --all-extras --dev

# 3. Install pre-commit hooks (prek — Rust-based, fast)
uv run prek install
```

Python 3.12 or higher is required.

---

## Running tests

```sh
# Run the full test suite
uv run pytest

# With coverage
uv run pytest --cov=TextSpitter --cov-report=term-missing

# Run a specific test file
uv run pytest tests/test_cli.py -v
```

---

## Code style and type checking

All checks are enforced by pre-commit hooks (via [prek](https://github.com/nickel-lang/prek)):

| Tool | Purpose |
|------|---------|
| **ruff** | Linting (E, F, B rules) |
| **isort** | Import ordering |
| **black** | Code formatting (line length 80) |
| **ty** | Static type checking |

Run all checks manually:

```sh
uv run ruff check TextSpitter tests
uv run black TextSpitter tests
uv run isort TextSpitter tests
uv run ty check
```

Type annotations are required for all public functions and class attributes. The package ships a `py.typed` PEP 561 marker.

---

## Project structure

```
TextSpitter/
├── TextSpitter/
│   ├── __init__.py      # Public API: TextSpitter(), WordLoader, __version__
│   ├── cli.py           # argparse CLI entry point
│   ├── core.py          # FileExtractor — low-level readers
│   ├── logger.py        # loguru / stdlib logging abstraction
│   ├── main.py          # WordLoader — dispatch logic
│   ├── py.typed         # PEP 561 marker
│   └── guide/           # pdoc documentation pages (importable subpackage)
│       ├── __init__.py
│       ├── overview.py
│       ├── quickstart.py
│       ├── tutorial.py
│       ├── usecases.py
│       └── recipes.py
├── tests/
├── .github/workflows/
├── pyproject.toml
└── uv.lock
```

**Layer responsibilities:**

- `TextSpitter()` (function) — one-liner convenience wrapper
- `WordLoader` — accepts `str | Path`; converts str→Path; dispatches to the correct reader
- `FileExtractor` — low-level reader; accepts any input type (`Path`, `BytesIO`, `SpooledTemporaryFile`, `bytes`)

---

## Submitting changes

1. **Fork** the repo and create a branch from `main`.
2. **Write tests** for any new functionality or bug fix.
3. **Ensure all checks pass** (`uv run pytest && uv run ty check`).
4. **Open a pull request** against `main` with a clear description of what changed and why.

Pull requests that add features without tests, or that break existing tests, will not be merged.

---

## Reporting bugs

Open an issue at [github.com/fsecada01/TextSpitter/issues](https://github.com/fsecada01/TextSpitter/issues) with:

- Python version (`python --version`)
- TextSpitter version (`pip show textspitter`)
- A minimal reproducible example
- The full traceback
