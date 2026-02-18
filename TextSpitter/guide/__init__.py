"""
# TextSpitter Documentation

## Welcome to TextSpitter

**Transforming documents into insights, effortlessly and efficiently.**

TextSpitter extracts plain text from documents and source-code files with a single call.
It normalises every input type — file paths, `BytesIO` streams, `SpooledTemporaryFile` objects,
and raw `bytes` — into plain strings, making it ideal for LLM pipelines, search engines,
and data-processing workflows.

---

## 📚 Start Here

Choose your path based on what you want to do:

<details open>
<summary><strong>⚡ I want to extract text right now</strong></summary>

Start with **[Quick Start](quickstart.html)** to install and run your first extraction in under 2 minutes.

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="report.pdf")
print(text[:500])
```

</details>

<details>
<summary><strong>🎯 I need to understand how TextSpitter works</strong></summary>

Read the **[Technical Overview](overview.html)** for architecture, module design, and implementation details.

Covers: three-layer design, input resolution, PDF fallback chains, encoding strategy, and logging.

</details>

<details>
<summary><strong>🔍 I want to learn by example</strong></summary>

Follow the **[Tutorial](tutorial.html)** for a format-by-format walkthrough covering:
- PDF extraction (with PyMuPDF + pypdf fallback)
- DOCX extraction via FastAPI
- TXT & CSV with encoding handling
- Source code files (50+ extensions)
- Direct `FileExtractor` and `WordLoader` usage

</details>

<details>
<summary><strong>💼 I'm building a real application</strong></summary>

Check **[Common Use Cases](usecases.html)** for production patterns:
- Web APIs (FastAPI, Django/DRF)
- Cloud storage (AWS S3)
- LLM pipelines (LangChain, OpenAI embeddings)
- Batch processing (directory trees, parallel extraction)
- Logging strategies

</details>

<details>
<summary><strong>📋 I need a code snippet</strong></summary>

Browse **[Recipes](recipes.html)** for copy-paste snippets covering:
- Input handling (BytesIO, SpooledTemporaryFile, raw bytes)
- Format-specific extraction
- Error and encoding handling
- Testing patterns

</details>

---

## ✨ Supported Formats

| Format | Method | Notes |
|--------|--------|-------|
| **PDF** | `pdf_file_read()` | PyMuPDF → pypdf fallback |
| **DOCX** | `docx_file_read()` | python-docx paragraph extraction |
| **TXT** | `text_file_read()` | UTF-8 → latin-1 → UTF-8-replace |
| **CSV** | `csv_file_read()` | Same encoding cascade as TXT |
| **Source code** | `code_file_read()` | 50+ extensions (py, js, ts, go, rs, java, …) |

---

## 🚀 Quick Start

### Install

```sh
pip install textspitter

# With optional loguru logging
pip install "textspitter[logging]"
```

### Extract

```python
from TextSpitter import TextSpitter

# From a file
text = TextSpitter(filename="report.pdf")

# From a stream
from io import BytesIO
text = TextSpitter(file_obj=BytesIO(pdf_bytes), filename="report.pdf")

# From raw bytes
text = TextSpitter(file_obj=docx_bytes, filename="contract.docx")
```

### CLI

```sh
# Single file to stdout
textspitter report.pdf

# Multiple files to combined output
textspitter chapter1.pdf chapter2.pdf -o book.txt
```

---

## 🔗 Navigation

| Page | Purpose | Best for |
|------|---------|----------|
| [Overview](overview.html) | Architecture & design | Understanding the internals |
| [Quick Start](quickstart.html) | Installation & first extraction | Getting started fast |
| [Tutorial](tutorial.html) | Format-by-format guide | Learning by example |
| [Use Cases](usecases.html) | Production patterns | Building real applications |
| [Recipes](recipes.html) | Code snippets | Copy-paste solutions |

---

## 📖 Full API Reference

For complete API documentation including class definitions, method signatures, and parameters,
see the **TextSpitter module reference** in the sidebar.

"""
