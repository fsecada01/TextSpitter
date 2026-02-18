<div id="top">

<!-- HEADER STYLE: MODERN -->
<div align="left" style="position: relative; width: 100%; height: 100%; ">

# TextSpitter

<em>Transforming documents into insights, effortlessly and efficiently.</em>

<!-- BADGES -->
<img src="https://img.shields.io/github/license/fsecada01/TextSpitter?style=flat-square&logo=opensourceinitiative&logoColor=white&color=8a2be2" alt="license">
<img src="https://img.shields.io/github/last-commit/fsecada01/TextSpitter?style=flat-square&logo=git&logoColor=white&color=8a2be2" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/fsecada01/TextSpitter?style=flat-square&color=8a2be2" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/fsecada01/TextSpitter?style=flat-square&color=8a2be2" alt="repo-language-count">
<img src="https://img.shields.io/badge/docs-GitHub%20Pages-8a2be2?style=flat-square&logo=github" alt="docs">

<em>Built with the tools and technologies:</em>

<img src="https://img.shields.io/badge/TOML-9C4121.svg?style=flat-square&logo=TOML&logoColor=white" alt="TOML">
<img src="https://img.shields.io/badge/Pytest-0A9EDC.svg?style=flat-square&logo=Pytest&logoColor=white" alt="Pytest">
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/GitHub%20Actions-2088FF.svg?style=flat-square&logo=GitHub-Actions&logoColor=white" alt="GitHub%20Actions">
<img src="https://img.shields.io/badge/uv-DE5FE9.svg?style=flat-square&logo=uv&logoColor=white" alt="uv">

</div>
</div>
<br clear="right">

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

TextSpitter is a lightweight Python library that extracts text from documents and source-code files with a single call. It normalises diverse input types — file paths, `BytesIO` streams, `SpooledTemporaryFile` objects, and raw `bytes` — into plain strings, making it ideal for pipelines that feed text into LLMs, search engines, or data-processing workflows.

**Why TextSpitter?**

- 📄 **Multi-format extraction** — PDF (PyMuPDF + PyPDF fallback), DOCX, TXT, CSV, and 50 + programming-language file types.
- 🔌 **Stream-first API** — accepts file paths, `BytesIO`, `SpooledTemporaryFile`, or raw `bytes`; no temp files required.
- 🛠️ **Optional structured logging** — install `textspitter[logging]` to add `loguru`; falls back to stdlib `logging` transparently.
- 🖥️ **CLI included** — `uv tool install textspitter` gives you a `textspitter` command for quick one-off extractions.
- 🚀 **Automated CI/CD** — GitHub Actions run the test matrix (Python 3.12–3.14) and publish docs to GitHub Pages on every push.

---

## Features

|      | Component        | Details                              |
| :--- | :--------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Three-layer design: `TextSpitter` convenience function → `WordLoader` dispatcher → `FileExtractor` low-level reader</li><li>OOP design enables straightforward subclassing and extension</li></ul> |
| 🔩 | **Code Quality**   | <ul><li>Strict PEP 8 / ruff linting with black formatting</li><li>Full type hints; ships a `py.typed` PEP 561 marker</li></ul> |
| 📄 | **Documentation**  | <ul><li>API docs auto-published to GitHub Pages via pdoc</li><li>Quick-start guide, tutorial, use-case examples, and recipes</li></ul> |
| 🔌 | **Integrations**   | <ul><li>CI/CD with GitHub Actions (tests + docs + PyPI publish)</li><li>Package management via `uv`; installable via `pip` or `uv tool install`</li></ul> |
| 🧩 | **Modularity**     | <ul><li>Core `FileExtractor` separated from dispatch logic in `WordLoader`</li><li>Logging abstraction in `logger.py` isolates the optional `loguru` dependency</li></ul> |
| 🧪 | **Testing**        | <ul><li>~70 pytest tests covering all readers and input types</li><li>Dual-mode log capture fixture works with or without `loguru`</li></ul> |
| ⚡️  | **Performance**    | <ul><li>Class-level `frozenset` / `dict` constants avoid per-call allocation</li><li>Stream rewind avoids re-reading large files</li></ul> |
| 📦 | **Dependencies**   | <ul><li>Core: `pymupdf`, `pypdf`, `python-docx`</li><li>Optional logging: `loguru` (`pip install textspitter[logging]`)</li></ul> |

---

## Project Structure

```sh
TextSpitter/
├── .github/
│   └── workflows/
│       ├── docs.yml             # pdoc → GitHub Pages
│       ├── python-publish.yml   # PyPI release
│       └── tests.yml            # pytest matrix (3.12 – 3.14)
├── TextSpitter/
│   ├── __init__.py              # TextSpitter() + WordLoader public API
│   ├── cli.py                   # argparse CLI entry point
│   ├── core.py                  # FileExtractor class
│   ├── logger.py                # Optional loguru / stdlib fallback
│   ├── main.py                  # WordLoader dispatcher
│   ├── py.typed                 # PEP 561 marker
│   └── guide/                   # pdoc documentation pages (subpackage)
├── tests/
│   ├── conftest.py              # shared fixtures (log_capture)
│   ├── test_cli.py
│   ├── test_file_extractor.py
│   ├── test_txt.py
│   └── ...
├── CHANGELOG.md
├── CONTRIBUTING.md
├── pyproject.toml
└── uv.lock
```

---

## Getting Started

### Prerequisites

- **Python** ≥ 3.12
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip

### Installation

**From PyPI:**

```sh
pip install textspitter

# With optional loguru logging
pip install "textspitter[logging]"
```

**Using uv:**

```sh
uv add textspitter

# With optional loguru logging
uv add "textspitter[logging]"
```

**As a standalone CLI tool:**

```sh
uv tool install textspitter
```

**From source:**

```sh
git clone https://github.com/fsecada01/TextSpitter.git
cd TextSpitter
uv sync --all-extras --dev
```

### Usage

**As a library (one-liner):**

```python
from TextSpitter import TextSpitter

# From a file path
text = TextSpitter(filename="report.pdf")
print(text)

# From a BytesIO stream
from io import BytesIO
text = TextSpitter(file_obj=BytesIO(pdf_bytes), filename="report.pdf")

# From raw bytes
text = TextSpitter(file_obj=docx_bytes, filename="contract.docx")
```

**Using the `WordLoader` class directly:**

```python
from TextSpitter.main import WordLoader

loader = WordLoader(filename="data.csv")
text = loader.file_load()
```

**As a CLI tool:**

```sh
# Extract a single file to stdout
textspitter report.pdf

# Extract multiple files and write to a combined output file
textspitter file1.pdf file2.docx notes.txt -o combined.txt
```

### Testing

```sh
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=TextSpitter --cov-report=term-missing
```

---

## Roadmap

### v1.x (current)

- [x] Stream-based API (`BytesIO`, `SpooledTemporaryFile`, raw `bytes`)
- [x] CLI entry point (`uv tool install textspitter`)
- [x] Optional loguru logging with stdlib fallback
- [x] Programming-language file support (50 + extensions)
- [x] CI matrix (Python 3.12 – 3.14) + GitHub Pages docs
- [ ] Async extraction API
- [ ] CSV → structured output (list of dicts)
- [ ] PPTX support

### v2.0 — Rust backend ([full roadmap](https://github.com/fsecada01/TextSpitter/wiki/TextSpitter-2.0-Rust-Roadmap))

- [ ] Rust splitting core via PyO3 + Maturin — **10x–40x** batch throughput
- [ ] Graceful Python fallback when Rust extension is unavailable
- [ ] `manylinux` wheels on PyPI — zero-compile install for Linux users
- [ ] Memory-mapped file processing for very large PDFs (`memmap2`)
- [ ] SIMD-accelerated string search for separator detection
- [ ] Streaming iterator API (yield chunks instead of collecting all)
- [ ] Optional SIMD feature flag (`pip install "textspitter[simd]"`)

---

## Contributing

- **💬 [Join the Discussions](https://github.com/fsecada01/TextSpitter/discussions)**: Share insights, give feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/fsecada01/TextSpitter/issues)**: Submit bugs or log feature requests.
- **💡 [Submit Pull Requests](https://github.com/fsecada01/TextSpitter/blob/main/CONTRIBUTING.md)**: Review open PRs or submit your own.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Fork the project to your GitHub account.
2. **Clone Locally**: Clone the forked repository.
   ```sh
   git clone https://github.com/fsecada01/TextSpitter.git
   ```
3. **Create a New Branch**: Always work on a new branch.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message.
   ```sh
   git commit -m 'Add new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your fork.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against `main`. Describe the changes and motivation clearly.
8. **Review**: Once approved, your PR will be merged. Thanks for contributing!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com/fsecada01/TextSpitter/graphs/contributors">
      <img src="https://contrib.rocks/image?repo=fsecada01/TextSpitter">
   </a>
</p>
</details>

---

## License

TextSpitter is released under the [MIT License](https://github.com/fsecada01/TextSpitter/blob/main/LICENSE).

<div align="right">

[![][back-to-top]](#top)

</div>

[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square
