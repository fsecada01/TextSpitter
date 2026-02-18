"""
# Recipes

Copy-paste snippets for common tasks.

---

## Input handling

<details open>
<summary><strong>From <code>BytesIO</code></strong></summary>

```python
from io import BytesIO
from TextSpitter import TextSpitter

with open("report.pdf", "rb") as f:
    text = TextSpitter(file_obj=BytesIO(f.read()), filename="report.pdf")
# Stream is rewound automatically — no seek(0) needed.
```

</details>

<details>
<summary><strong>From <code>SpooledTemporaryFile</code></strong></summary>

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
<summary><strong>From raw <code>bytes</code></strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(file_obj=pdf_bytes, filename="document.pdf")
```

</details>

<details>
<summary><strong>Custom filename attribute</strong></summary>

Some frameworks expose the original name on a non-standard attribute.
Pass `file_attr` to tell `FileExtractor` where to look:

```python
from TextSpitter.core import FileExtractor

fe = FileExtractor(file_obj=upload_obj, file_attr="original_name")
text = fe.text_file_read()
```

</details>

---

## Format-specific

<details open>
<summary><strong>Force pypdf (skip PyMuPDF)</strong></summary>

```python
import TextSpitter.core as _core
from TextSpitter.core import FileExtractor

_real, _core.pymupdf = _core.pymupdf, None
try:
    text = FileExtractor(file_obj=pdf_bytes, filename="doc.pdf").pdf_file_read()
finally:
    _core.pymupdf = _real
```

</details>

<details>
<summary><strong>DOCX paragraphs as a list</strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="doc.docx")
paragraphs = [ln for ln in text.splitlines() if ln.strip()]
```

</details>

<details>
<summary><strong>CSV into rows</strong></summary>

```python
import csv, io
from TextSpitter import TextSpitter

raw = TextSpitter(filename="data.csv")
rows = list(csv.DictReader(io.StringIO(raw)))
print(rows[0])
```

</details>

---

## Error and encoding

<details open>
<summary><strong>Detect decode warnings (loguru)</strong></summary>

```python
from loguru import logger

seen = []
logger.add(lambda m: seen.append(m.record["message"]), level="WARNING")

from TextSpitter import TextSpitter
TextSpitter(filename="legacy.txt")

if seen:
    print("Encoding issues:", seen)
```

</details>

<details>
<summary><strong>Validate extraction result</strong></summary>

```python
from TextSpitter import TextSpitter

def safe_extract(path: str) -> str | None:
    text = TextSpitter(filename=path)
    return text if text and text.strip() else None
```

</details>

---

## Testing

<details open>
<summary><strong>Unit-test a function that calls TextSpitter</strong></summary>

```python
def test_my_function(tmp_path):
    (tmp_path / "doc.txt").write_text("Hello world")
    result = my_function(str(tmp_path / "doc.txt"))
    assert "Hello" in result
```

</details>

<details>
<summary><strong>Mock TextSpitter in integration tests</strong></summary>

```python
from unittest.mock import patch

with patch("myapp.routes.TextSpitter", return_value="mocked text"):
    response = client.post("/extract", ...)

assert response.json()["text"] == "mocked text"
```

</details>

<details>
<summary><strong>Capture log output (log_capture fixture)</strong></summary>

```python
def test_warns_on_bad_encoding(log_capture, tmp_path):
    (tmp_path / "bad.txt").write_bytes(b"\\x81\\xfe\\xff")
    from TextSpitter import TextSpitter
    TextSpitter(filename=str(tmp_path / "bad.txt"))
    assert any("utf-8 or latin-1" in m for m in log_capture)
```

See `tests/conftest.py` for the `log_capture` fixture definition.

</details>
"""
