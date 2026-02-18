"""
# Tutorial

End-to-end walkthrough covering every supported format and input type.

---

## PDF files

<details open>
<summary><strong>From a file path</strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="annual_report.pdf")
print(f"Extracted {len(text)} characters")
```

Internally, `pdf_file_read()` tries PyMuPDF first, then falls back to pypdf
if PyMuPDF fails for any reason (import error, corrupt file, platform
restriction).

</details>

<details>
<summary><strong>From bytes (downloaded at runtime)</strong></summary>

```python
import httpx
from TextSpitter import TextSpitter

response = httpx.get("https://example.com/report.pdf")
text = TextSpitter(file_obj=response.content, filename="report.pdf")
```

</details>

<details>
<summary><strong>Scanned / image-only PDFs</strong></summary>

TextSpitter extracts *embedded text layers* only. Scanned PDFs with no text
layer return an empty string. Pre-process with an OCR tool (e.g.
`pytesseract`) and pass the resulting text directly.

</details>

---

## Word documents (DOCX)

<details open>
<summary><strong>From a file path</strong></summary>

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="contract.docx")
```

`docx_file_read()` uses python-docx to iterate every `Paragraph` and joins
them with newlines.

</details>

<details>
<summary><strong>From a FastAPI upload</strong></summary>

```python
from fastapi import UploadFile
from io import BytesIO
from TextSpitter import TextSpitter

async def extract(file: UploadFile) -> str:
    data = await file.read()
    return TextSpitter(file_obj=BytesIO(data), filename=file.filename)
```

</details>

---

## Plain text and CSV

<details open>
<summary><strong>TXT</strong></summary>

```python
text = TextSpitter(filename="notes.txt")
```

`text_file_read()` tries UTF-8, then latin-1. If both fail, falls back to
UTF-8 with replacement characters and logs a warning.

</details>

<details>
<summary><strong>CSV — raw string</strong></summary>

```python
import csv, io
from TextSpitter import TextSpitter

raw = TextSpitter(filename="data.csv")
rows = list(csv.reader(io.StringIO(raw)))
```

</details>

<details>
<summary><strong>Non-UTF-8 encoded files</strong></summary>

Files saved in latin-1 or Windows-1252 are handled automatically — no
configuration required.

```python
text = TextSpitter(filename="legacy_export.txt")  # cp1252? latin-1? works.
```

</details>

---

## Source code files

50 + programming-language extensions are routed through `code_file_read()`,
which uses a wider encoding cascade than the plain-text reader.

<details open>
<summary><strong>Single file</strong></summary>

```python
source = TextSpitter(filename="main.py")
```

</details>

<details>
<summary><strong>Batch extraction from a directory</strong></summary>

```python
from pathlib import Path
from TextSpitter import TextSpitter

texts = {
    str(p): TextSpitter(filename=str(p))
    for p in Path("my_project").rglob("*.py")
}
```

</details>

<details>
<summary><strong>Supported extensions (sample)</strong></summary>

`.py` `.js` `.ts` `.jsx` `.tsx` `.java` `.kt` `.go` `.rs` `.cpp` `.c`
`.cs` `.rb` `.php` `.swift` `.dart` `.elm` `.ex` `.erl` `.jl` `.nim`
`.zig` `.lua` `.r` `.sql` `.sh` `.bash` `.html` `.css` `.scss` `.json`
`.yaml` `.toml` `.xml` `.md` `.rst` and more.

</details>

---

## Using `WordLoader` directly

```python
from TextSpitter.main import WordLoader

loader = WordLoader(filename="document.pdf")
text = loader.file_load()
```

---

## Using `FileExtractor` directly

```python
from TextSpitter.core import FileExtractor

fe = FileExtractor(file_obj=pdf_bytes, filename="report.pdf")
raw   = fe.get_contents()    # always bytes
text  = fe.pdf_file_read()   # extracted text
```

Useful when you need to call multiple reader methods on the same file, or
inspect `file_name` / `file_ext` before extracting.
"""
