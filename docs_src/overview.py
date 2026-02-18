"""
# Technical Overview

This page describes TextSpitter's internal architecture, the responsibility of
each module, and the design decisions that shape the public API.

---

## Module Map

```
TextSpitter/
├── __init__.py    TextSpitter()   — top-level convenience function
├── cli.py         main()          — argparse CLI entry point
├── core.py        FileExtractor   — low-level file reader
├── logger.py      logger          — optional loguru / stdlib shim
└── main.py        WordLoader      — format dispatcher
```

---

## Three-Layer Design

<details open>
<summary><strong>Layer 1 — Public surface (<code>__init__.py</code>)</strong></summary>

`TextSpitter(file_obj=..., filename=...)` is a plain function that creates a
`WordLoader`, calls `file_load()`, and returns the resulting string.  It
exists purely for ergonomics — most callers need only a single import and a
single call.

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="notes.txt")
```

</details>

<details>
<summary><strong>Layer 2 — Dispatcher (<code>main.py</code>)</strong></summary>

`WordLoader` holds two class-level constants:

* `FILE_EXT_MATRIX` — maps file extensions to `FileExtractor` method names.
* `TEXT_MIME_TYPES` — set of MIME subtypes treated as plain-text.

`file_load()` checks the extension first, falls back to
`FileExtractor.is_programming_language_file()`, then resolves by MIME type.
Unknown formats log an error and return `""`.

</details>

<details>
<summary><strong>Layer 3 — Reader (<code>core.py</code>)</strong></summary>

`FileExtractor.__init__` resolves whatever input it receives (path string,
`Path`, stream, bytes) into three normalised attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `file` | `Path \| IO \| bytes` | The underlying file object |
| `file_name` | `str` | Filename including extension |
| `file_ext` | `str` | Lowercase extension without dot |

The reader methods (`pdf_file_read`, `docx_file_read`, `text_file_read`,
`csv_file_read`, `code_file_read`) all call `get_contents()` first, which
returns raw `bytes` regardless of the input type.

</details>

---

## Input Resolution

`get_contents()` handles four input shapes:

| `self.file` type | Behaviour |
|-----------------|-----------|
| `Path` | Opens in binary mode and reads |
| `BytesIO` / `SpooledTemporaryFile` | Seeks to 0 then reads |
| `bytes` | Returned as-is |
| Other stream (`IOBase`) | Casts to `BinaryIO`, seeks, reads |

If the stream returns a `str` instead of `bytes` (unusual but handled), it
encodes with UTF-8 and emits a warning.

---

## PDF Fallback Chain

```
pymupdf.open(stream=…)  ──▶  success  ──▶  return text
        │
        └──(ImportError / any Exception)
                │
                ▼
         pypdf.PdfReader(BytesIO(…))  ──▶  success  ──▶  return text
                │
                └──(Exception)
                        │
                        ▼
                    log error, return ""
```

---

## Encoding Strategy

Text and CSV files use a three-step cascade inside `_decode_bytes()`:

1. `bytes.decode("utf-8")` — strict
2. `bytes.decode("latin-1")` — strict (latin-1 never raises for any byte)
3. `bytes.decode("utf-8", errors="replace")` — logs a warning; reached only
   when latin-1 itself raises (should be unreachable in practice, but
   guards against mocked-out bytes objects in tests)

Code files (`code_file_read`) use a wider list:
`utf-8 → utf-8-sig → latin-1 → cp1252 → utf-8 replace`.

---

## Optional Logging

`logger.py` exports a single `logger` object.  At import time it tries
`from loguru import logger`; on `ImportError` it falls back to
`logging.getLogger("textspitter")`.  Every call site in `core.py` and
`main.py` uses this shim, so the rest of the codebase is backend-agnostic.

Install loguru with:

```sh
pip install "textspitter[logging]"
```

---

## CLI

`cli.py` is a thin argparse wrapper around the `TextSpitter()` function.
`[project.scripts]` in `pyproject.toml` wires it up as the `textspitter`
console entry point.

```
textspitter FILE [FILE ...] [-o OUTPUT]
```
"""
