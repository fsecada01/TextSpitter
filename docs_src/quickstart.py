"""
# Quick Start

Get up and running with TextSpitter in under two minutes.

---

## 1 — Install

<details open>
<summary><strong>pip</strong></summary>

```sh
pip install textspitter
```

Add optional structured logging:

```sh
pip install "textspitter[logging]"
```

</details>

<details>
<summary><strong>uv (library)</strong></summary>

```sh
uv add textspitter
uv add "textspitter[logging]"   # optional loguru logging
```

</details>

<details>
<summary><strong>uv (CLI tool)</strong></summary>

```sh
uv tool install textspitter
```

This installs `textspitter` as an isolated tool — no virtual environment
management required.

</details>

---

## 2 — Extract Your First File

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="path/to/document.pdf")
print(text[:500])
```

That's it.  `TextSpitter()` auto-detects the format from the file extension,
picks the right reader, and returns a plain `str`.

---

## 3 — Use the CLI

```sh
# Extract a single PDF to stdout
textspitter report.pdf

# Extract multiple files and save to a combined text file
textspitter chapter1.pdf chapter2.pdf -o book.txt
```

---

## 4 — Work with Streams

When files come from a web upload, S3, or an in-memory buffer, pass a
stream directly — no temp files needed:

```python
from io import BytesIO
from TextSpitter import TextSpitter

# BytesIO
with open("doc.docx", "rb") as f:
    text = TextSpitter(file_obj=BytesIO(f.read()), filename="doc.docx")

# Raw bytes
text = TextSpitter(file_obj=some_bytes_var, filename="data.csv")
```

The `filename` keyword is required for streams so TextSpitter knows which
reader to invoke.

---

## 5 — Next Steps

- Read the [Tutorial](tutorial.html) for a format-by-format walkthrough.
- Browse the [Use Cases](usecases.html) for integration patterns (FastAPI,
  S3, LangChain …).
- Grab ready-to-run snippets from the [Recipes](recipes.html) page.
- See the full [API Reference](../TextSpitter.html) for every class and method.
"""
