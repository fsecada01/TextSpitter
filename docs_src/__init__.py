"""
# TextSpitter Documentation

**TextSpitter** is a lightweight Python library that extracts plain text from
documents and source-code files.  It normalises every supported input type —
file paths, `BytesIO` streams, `SpooledTemporaryFile` objects, and raw
`bytes` — into a single `str`, making it a natural drop-in for any text
pipeline.

---

## Navigation

| Page | Description |
|------|-------------|
| [Overview](../docs_src/overview.html) | Architecture, module map, design decisions |
| [Quick Start](../docs_src/quickstart.html) | Install and run your first extraction in 60 seconds |
| [Tutorial](../docs_src/tutorial.html) | End-to-end walkthrough of every supported format |
| [Use Cases](../docs_src/usecases.html) | Real-world integration patterns (FastAPI, S3, RAG …) |
| [Recipes](../docs_src/recipes.html) | Copy-paste snippets for common tasks |
| [API Reference](../TextSpitter.html) | Auto-generated from source docstrings |

---

## Supported Formats

| Format | Notes |
|--------|-------|
| **PDF** | PyMuPDF (primary) with automatic fallback to pypdf |
| **DOCX** | python-docx paragraph extraction |
| **TXT / CSV** | UTF-8 → latin-1 → UTF-8-replace cascade |
| **Source code** | 50 + extensions — `.py`, `.js`, `.ts`, `.go`, `.rs`, … |

---

## Installation

```sh
pip install textspitter                    # core
pip install "textspitter[logging]"         # + loguru structured logging
uv tool install textspitter               # CLI only
```

---

## Minimal Example

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="report.pdf")
print(text[:200])
```
"""
