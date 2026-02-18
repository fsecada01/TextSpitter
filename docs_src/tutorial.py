"""
# Tutorial

This tutorial walks through every supported format and input type, explaining
what TextSpitter does under the hood at each step.

---

## PDF Files

<details open>
<summary><strong>From a file path</strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="annual_report.pdf")
print(f"Extracted {len(text)} characters")
```

Internally, `FileExtractor.pdf_file_read()` tries **PyMuPDF** first.  If
that fails for any reason (import error, corrupt file, platform restriction),
it automatically retries with **pypdf**.

</details>

<details>
<summary><strong>From bytes (e.g. downloaded from the web)</strong></summary>

```python
import httpx
from TextSpitter import TextSpitter

response = httpx.get("https://example.com/report.pdf")
text = TextSpitter(file_obj=response.content, filename="report.pdf")
```

</details>

<details>
<summary><strong>Handling scanned / image-only PDFs</strong></summary>

TextSpitter extracts embedded text layers only.  Scanned PDFs without a text
layer will return an empty string.  For OCR, pre-process with a tool like
`pytesseract` or `azure-cognitiveservices-vision-computervision` before
passing the result to TextSpitter.

</details>

---

## Word Documents (DOCX)

<details open>
<summary><strong>From a file path</strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="contract.docx")
```

`docx_file_read()` uses `python-docx` to iterate over every `Paragraph`
object and joins them with newlines.

</details>

<details>
<summary><strong>From a FastAPI / Django upload</strong></summary>

```python
# FastAPI example
from fastapi import UploadFile
from io import BytesIO
from TextSpitter import TextSpitter

async def extract(file: UploadFile) -> str:
    data = await file.read()
    return TextSpitter(file_obj=BytesIO(data), filename=file.filename)
```

</details>

---

## Plain Text & CSV

<details open>
<summary><strong>TXT files</strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="notes.txt")
```

`text_file_read()` tries UTF-8 first, then latin-1.  If both fail it falls
back to UTF-8 with replacement characters and logs a warning.

</details>

<details>
<summary><strong>CSV files</strong></summary>

```python
from TextSpitter import TextSpitter

raw_csv = TextSpitter(filename="data.csv")
# raw_csv is the entire file as a string; parse with csv.reader as needed
import csv, io
rows = list(csv.reader(io.StringIO(raw_csv)))
```

</details>

<details>
<summary><strong>Non-UTF-8 encoded files</strong></summary>

Files encoded in latin-1 or Windows-1252 are handled automatically.
TextSpitter's `_decode_bytes()` helper tries encodings in order and only
falls back to lossy replacement as a last resort.

```python
# A file saved by an old Windows application in cp1252
text = TextSpitter(filename="legacy_export.txt")
# Works without any extra configuration
```

</details>

---

## Source Code Files

TextSpitter recognises 50 + programming-language extensions and routes them
through `code_file_read()`, which uses a wider encoding cascade than the
plain-text reader.

<details open>
<summary><strong>Single file</strong></summary>

```python
from TextSpitter import TextSpitter

source = TextSpitter(filename="main.py")
print(source)
```

</details>

<details>
<summary><strong>Batch extraction from a directory</strong></summary>

```python
from pathlib import Path
from TextSpitter import TextSpitter

repo_root = Path("my_project")
texts = {}
for path in repo_root.rglob("*.py"):
    texts[str(path)] = TextSpitter(filename=str(path))
```

</details>

<details>
<summary><strong>Supported extensions (sample)</strong></summary>

`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.kt`, `.go`, `.rs`,
`.cpp`, `.c`, `.h`, `.cs`, `.rb`, `.php`, `.swift`, `.dart`, `.elm`,
`.ex`, `.exs`, `.erl`, `.jl`, `.nim`, `.zig`, `.lua`, `.r`, `.sql`,
`.sh`, `.bash`, `.zsh`, `.ps1`, `.html`, `.htm`, `.css`, `.scss`,
`.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.md`, `.rst`, and more.

</details>

---

## Using `WordLoader` Directly

`WordLoader` gives you a reusable object instead of a single call:

```python
from TextSpitter.main import WordLoader

loader = WordLoader(filename="document.pdf")
text = loader.file_load()

# Re-use the loader with the same file
text_again = loader.file_load()
```

---

## Using `FileExtractor` Directly

For advanced use-cases you can work with the low-level `FileExtractor` class:

```python
from TextSpitter.core import FileExtractor

fe = FileExtractor(file_obj=pdf_bytes, filename="report.pdf")
raw_bytes = fe.get_contents()   # always returns bytes
text       = fe.pdf_file_read() # extract text
```

`FileExtractor` is especially useful when you need to call multiple reader
methods on the same file or inspect the resolved `file_name` / `file_ext`
before extracting.
"""
