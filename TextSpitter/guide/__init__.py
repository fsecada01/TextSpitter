"""
# TextSpitter — User Guide

Welcome to the TextSpitter documentation.
TextSpitter extracts plain text from documents and source-code files with a
single call, normalising every input type (file path, `BytesIO`, `SpooledTemporaryFile`,
raw `bytes`) into a `str`.

---

## Pages in this guide

| Page | Description |
|------|-------------|
| `TextSpitter.guide.overview` | Architecture and design decisions |
| `TextSpitter.guide.quickstart` | Install and run your first extraction |
| `TextSpitter.guide.tutorial` | Format-by-format walkthrough |
| `TextSpitter.guide.usecases` | FastAPI, S3, LangChain, batch processing … |
| `TextSpitter.guide.recipes` | Copy-paste snippets |

---

## Supported formats

| Format | Reader | Notes |
|--------|--------|-------|
| PDF | `pdf_file_read` | PyMuPDF → pypdf fallback |
| DOCX | `docx_file_read` | python-docx paragraph extraction |
| TXT | `text_file_read` | UTF-8 → latin-1 → UTF-8-replace |
| CSV | `csv_file_read` | Same encoding cascade as TXT |
| Source code | `code_file_read` | 50 + extensions |

---

## Quick example

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="report.pdf")
print(text[:200])
```

Install with optional loguru logging:

```sh
pip install "textspitter[logging]"
```
"""
