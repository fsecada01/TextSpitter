"""
# Quick Start

Get up and running in under two minutes.

---

## 1 — Install

<details open>
<summary><strong>pip</strong></summary>

```sh
pip install textspitter

# With optional loguru logging
pip install "textspitter[logging]"
```

</details>

<details>
<summary><strong>uv (library dependency)</strong></summary>

```sh
uv add textspitter
uv add "textspitter[logging]"
```

</details>

<details>
<summary><strong>uv tool (standalone CLI)</strong></summary>

```sh
uv tool install textspitter
```

Installs `textspitter` as an isolated tool — no virtual environment management required.

</details>

---

## 2 — Extract your first file

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="path/to/document.pdf")
print(text[:500])
```

`TextSpitter()` auto-detects the format from the file extension, picks the
right reader, and returns a plain `str`.

---

## 3 — Use the CLI

```sh
# Single file to stdout
textspitter report.pdf

# Multiple files saved to a combined output
textspitter chapter1.pdf chapter2.pdf -o book.txt
```

---

## 4 — Work with streams

```python
from io import BytesIO
from TextSpitter import TextSpitter

# From BytesIO (e.g. web upload, boto3, httpx)
text = TextSpitter(file_obj=BytesIO(pdf_bytes), filename="report.pdf")

# From raw bytes
text = TextSpitter(file_obj=some_bytes, filename="data.csv")
```

`filename` is required for streams so TextSpitter knows which reader to use.

---

## 5 — Next steps

- **`TextSpitter.guide.tutorial`** — format-by-format walkthrough
- **`TextSpitter.guide.usecases`** — FastAPI, S3, LangChain patterns
- **`TextSpitter.guide.recipes`** — copy-paste snippets
- **`TextSpitter.core`** / **`TextSpitter.main`** — full API reference
"""
