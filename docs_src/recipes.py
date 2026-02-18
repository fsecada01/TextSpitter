"""
# Recipes

Copy-paste snippets for the most common TextSpitter tasks.

---

## Input Handling

<details open>
<summary><strong>Extract from a <code>BytesIO</code> stream</strong></summary>

```python
from io import BytesIO
from TextSpitter import TextSpitter

with open("report.pdf", "rb") as f:
    buf = BytesIO(f.read())

text = TextSpitter(file_obj=buf, filename="report.pdf")
```

The stream is rewound automatically — you do not need to call `buf.seek(0)`
first.

</details>

<details>
<summary><strong>Extract from a <code>SpooledTemporaryFile</code></strong></summary>

```python
from tempfile import SpooledTemporaryFile
from TextSpitter import TextSpitter

with SpooledTemporaryFile(max_size=10 * 1024 * 1024) as stf:
    stf.write(pdf_bytes)
    stf.seek(0)
    text = TextSpitter(file_obj=stf, filename="upload.pdf")
```

</details>

<details>
<summary><strong>Extract from raw <code>bytes</code></strong></summary>

```python
from TextSpitter import TextSpitter

pdf_bytes: bytes = ...          # from requests, boto3, httpx, etc.
text = TextSpitter(file_obj=pdf_bytes, filename="document.pdf")
```

</details>

<details>
<summary><strong>Resolve filename from a custom attribute</strong></summary>

Some frameworks expose the original filename on a non-standard attribute
(e.g. `upload.original_name`).  Pass `file_attr` to tell `FileExtractor`
where to look:

```python
from TextSpitter.core import FileExtractor

fe = FileExtractor(file_obj=upload_obj, file_attr="original_name")
text = fe.text_file_read()
```

</details>

---

## Format-Specific

<details open>
<summary><strong>Force the pypdf reader (skip PyMuPDF)</strong></summary>

```python
from io import BytesIO
from TextSpitter.core import FileExtractor
import TextSpitter.core as _core

# Temporarily mask pymupdf so the fallback path is exercised
_real = _core.pymupdf
_core.pymupdf = None
try:
    fe = FileExtractor(file_obj=pdf_bytes, filename="doc.pdf")
    text = fe.pdf_file_read()
finally:
    _core.pymupdf = _real
```

</details>

<details>
<summary><strong>Extract DOCX paragraphs as a list</strong></summary>

```python
from io import BytesIO
from docx import Document

def extract_paragraphs(docx_bytes: bytes) -> list[str]:
    doc = Document(BytesIO(docx_bytes))
    return [p.text for p in doc.paragraphs if p.text.strip()]
```

For a plain-string join, use `TextSpitter` directly:

```python
text = TextSpitter(file_obj=docx_bytes, filename="doc.docx")
paragraphs = [line for line in text.splitlines() if line.strip()]
```

</details>

<details>
<summary><strong>Extract CSV and parse into rows</strong></summary>

```python
import csv, io
from TextSpitter import TextSpitter

raw = TextSpitter(filename="data.csv")
reader = csv.DictReader(io.StringIO(raw))
rows = list(reader)
print(rows[0])          # {'col1': 'val1', 'col2': 'val2'}
```

</details>

---

## Encoding & Error Handling

<details open>
<summary><strong>Detect and handle decode warnings</strong></summary>

Install `loguru` and attach a sink that captures warnings:

```python
from loguru import logger

warnings_seen: list[str] = []
logger.add(lambda m: warnings_seen.append(m.record["message"]), level="WARNING")

from TextSpitter import TextSpitter
text = TextSpitter(filename="legacy.txt")

if warnings_seen:
    print("Encoding issues detected:", warnings_seen)
```

Without loguru, configure the stdlib logger:

```python
import logging

handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)
logging.getLogger("textspitter").addHandler(handler)
```

</details>

<details>
<summary><strong>Validate extraction succeeded</strong></summary>

```python
from TextSpitter import TextSpitter

def safe_extract(path: str) -> str | None:
    text = TextSpitter(filename=path)
    if not text or not text.strip():
        return None     # empty result — likely image-only PDF or wrong format
    return text
```

</details>

---

## Testing

<details open>
<summary><strong>Unit-test a function that calls TextSpitter</strong></summary>

```python
from unittest.mock import patch
from myapp import summarise   # calls TextSpitter internally

def test_summarise(tmp_path):
    (tmp_path / "doc.txt").write_text("Hello world")
    result = summarise(str(tmp_path / "doc.txt"))
    assert "Hello" in result
```

</details>

<details>
<summary><strong>Mock TextSpitter in integration tests</strong></summary>

```python
from unittest.mock import patch

with patch("myapp.routes.TextSpitter", return_value="mocked text"):
    response = client.post("/extract", files={"file": ("doc.pdf", b"...", "application/pdf")})

assert response.json()["text"] == "mocked text"
```

</details>

<details>
<summary><strong>Capture log output in tests (log_capture fixture)</strong></summary>

The shared `log_capture` fixture in `tests/conftest.py` works whether or not
loguru is installed:

```python
def test_bad_encoding_warns(log_capture, tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\\x81\\xfe\\xff")
    from TextSpitter import TextSpitter
    TextSpitter(filename=str(bad))
    assert any("utf-8 or latin-1" in msg for msg in log_capture)
```

</details>
"""
