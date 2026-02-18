"""
# Technical Overview

Architecture, module map, and design decisions.

---

## Module map

```
TextSpitter/
├── __init__.py    TextSpitter()   — convenience function + __version__
├── cli.py         main()          — argparse CLI entry point
├── core.py        FileExtractor   — low-level reader
├── guide/                         — this user guide (subpackage)
├── logger.py      logger          — optional loguru / stdlib shim
└── main.py        WordLoader      — format dispatcher
```

---

## Three-layer design

<details open>
<summary><strong>Layer 1 — Public surface (<code>__init__.py</code>)</strong></summary>

`TextSpitter(file_obj, filename)` is a plain function that creates a
`WordLoader`, calls `file_load()`, and returns the `str`.

```python
from TextSpitter import TextSpitter

text = TextSpitter(filename="notes.txt")
```

</details>

<details>
<summary><strong>Layer 2 — Dispatcher (<code>WordLoader</code>)</strong></summary>

`WordLoader` holds two class-level constants:

- `FILE_EXT_MATRIX` — maps file extensions to `FileExtractor` method names.
- `TEXT_MIME_TYPES` — MIME subtypes treated as plain-text.

`file_load()` checks the extension first, then `is_programming_language_file()`,
then MIME type. Unknown formats log an error and return `""`.

</details>

<details>
<summary><strong>Layer 3 — Reader (<code>FileExtractor</code>)</strong></summary>

`FileExtractor.__init__` resolves any input into three normalised attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `file` | `Path \| IO \| bytes` | The underlying file object |
| `file_name` | `str` | Filename including extension |
| `file_ext` | `str` | Lowercase extension without dot |

All reader methods call `get_contents()` first, which always returns `bytes`.

</details>

---

## Input resolution

`get_contents()` handles four input shapes:

| `self.file` type | Behaviour |
|-----------------|-----------|
| `Path` | Opens in binary mode and reads |
| `BytesIO` / `SpooledTemporaryFile` | Seeks to 0, then reads |
| `bytes` | Returned as-is |
| Other stream (`IOBase`) | Cast to `BinaryIO`, seek, read |

---

## PDF fallback chain

```
pymupdf.open(stream=…)
    │ success → return text
    └─ ImportError / any Exception
           │
           ▼
    pypdf.PdfReader(BytesIO(…))
           │ success → return text
           └─ Exception
                  │
                  ▼
              log error, return ""
```

---

## Encoding strategy

`_decode_bytes()` uses a three-step cascade for TXT and CSV:

1. `bytes.decode("utf-8")` — strict
2. `bytes.decode("latin-1")` — strict (never raises for any byte value)
3. `bytes.decode("utf-8", errors="replace")` — logs a warning

`code_file_read()` tries a wider list: `utf-8 → utf-8-sig → latin-1 → cp1252 → utf-8/replace`.

---

## Optional logging

`logger.py` exports a single `logger` object. At import time it tries
`from loguru import logger`; on `ImportError` it falls back to
`logging.getLogger("textspitter")`. All call sites use this shim, so the
rest of the codebase is backend-agnostic.

```sh
pip install "textspitter[logging]"   # enable loguru
```
"""
