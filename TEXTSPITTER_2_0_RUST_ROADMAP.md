# TextSpitter 2.0 — Rust Backend Roadmap

> **Status:** Planning · **Current Version:** 1.0 (Python) · **Target:** 2.0 (Python wrapper over Rust core)

TextSpitter 1.0 is a pure Python document-to-text extraction and splitting library. Version 2.0 will rebase the core splitting engine in Rust via [PyO3](https://pyo3.rs/) and [Maturin](https://www.maturin.rs/), keeping the existing Python public API fully backwards-compatible while delivering significant performance gains for batch and high-throughput workloads.

---

## Goals

- Maintain 100% API compatibility — existing users change nothing
- Achieve **10x–40x** throughput improvement on batch document processing
- Eliminate Python GIL bottlenecks for CPU-bound splitting operations
- Enable zero-copy string slicing and parallel chunk processing via [Rayon](https://docs.rs/rayon)
- Provide a graceful Python fallback when the Rust extension is unavailable

## Non-Goals

- TextSpitter will **not** perform OCR in Rust — scanned-PDF handling remains a pre-processing concern for the caller
- TextSpitter will **not** replace the Python-level format dispatch (`WordLoader`) — only the splitting/chunking hot-path moves to Rust
- No breaking changes to the public `TextSpitter(file_obj, filename)` call signature

---

## Proposed Architecture

```
TextSpitter (Python public API — unchanged)
    ├── TextSpitter/__init__.py    # Public entry point (TextSpitter function + __version__)
    ├── TextSpitter/main.py        # WordLoader — format dispatcher (unchanged)
    ├── TextSpitter/core.py        # FileExtractor — low-level reader (unchanged)
    ├── TextSpitter/splitters.py   # NEW: thin Python wrappers over Rust splitters
    └── text_spitter_rust/         # NEW: compiled Rust extension (via PyO3)
         ├── CharacterTextSplitter # Parallel character splitting
         ├── TokenTextSplitter     # Fast token counting & chunking
         ├── RecursiveSplitter     # Recursive splitting with overlap
         └── BatchProcessor        # Rayon-parallel batch operations

src/                               # NEW: Rust source tree
    ├── lib.rs                     # PyO3 module definition
    ├── splitters/
    │   ├── character.rs
    │   ├── token.rs
    │   └── recursive.rs
    └── utils.rs

Cargo.toml                         # Rust manifest
pyproject.toml                     # Updated to use maturin build backend
```

> **Import path note:** The existing package is `TextSpitter` (capital T). The Rust extension module is named `text_spitter_rust` to avoid collision. The Python source tree keeps its current layout — only the new `splitters.py` module and the compiled extension are added. Do not rename or move existing modules.

---

## Prerequisites

Before beginning development, ensure the following are installed:

```bash
# Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup update stable

# Maturin (builds PyO3 extensions) — install inside the project venv
uv add --dev maturin

# Verify
rustc --version
maturin --version
```

> **Dev setup note:** `maturin develop` (Phase 4) installs the compiled extension into the **active virtual environment**. Always activate the project venv (`source .venv/bin/activate` or `uv run`) before running maturin commands, otherwise the extension is installed into the wrong environment.

---

## Phase 1: Project Setup & Build Infrastructure

### 1.1 — Update `pyproject.toml`

Replace the current build backend with Maturin:

```toml
[build-system]
requires = ["maturin>=1.4,<2.0"]
build-backend = "maturin"

[tool.maturin]
python-source = "."          # keep existing TextSpitter/ layout in place
features = ["pyo3/extension-module"]
```

### 1.2 — Create `Cargo.toml`

```toml
[package]
name = "text_spitter_rust"
version = "2.0.0"
edition = "2021"

[lib]
name = "text_spitter_rust"
crate-type = ["cdylib"]

[dependencies]
# Check https://pyo3.rs for the latest stable release at implementation time.
pyo3 = { version = ">=0.21", features = ["extension-module"] }
rayon = "1.9"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

### 1.3 — Add `TextSpitter/splitters.py`

No source restructuring needed. Add a single new file `TextSpitter/splitters.py` that houses the Python wrapper classes (see Phase 3). The existing module layout is untouched.

---

## Phase 2: Core Rust Implementation

### 2.1 — PyO3 Module Entry Point (`src/lib.rs`)

```rust
use pyo3::prelude::*;

mod splitters;

#[pymodule]
fn text_spitter_rust(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<splitters::character::CharacterTextSplitter>()?;
    m.add_class::<splitters::token::TokenTextSplitter>()?;
    Ok(())
}
```

### 2.2 — Character Splitter (`src/splitters/character.rs`)

Note: `split_internal` is a private Rust helper and lives in a separate `impl` block so PyO3 does **not** expose it to Python.

```rust
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyclass]
pub struct CharacterTextSplitter {
    chunk_size: usize,
    chunk_overlap: usize,
    separator: String,
}

#[pymethods]
impl CharacterTextSplitter {
    #[new]
    fn new(chunk_size: usize, chunk_overlap: usize, separator: String) -> Self {
        Self { chunk_size, chunk_overlap, separator }
    }

    /// Split a single document into chunks.
    fn split_text(&self, text: &str) -> PyResult<Vec<String>> {
        Ok(self.split_internal(text))
    }

    /// Batch split — processes documents in parallel via Rayon.
    fn split_texts(&self, texts: Vec<String>) -> PyResult<Vec<Vec<String>>> {
        let results: Vec<Vec<String>> = texts
            .par_iter()
            .map(|text| self.split_internal(text))
            .collect();
        Ok(results)
    }
}

// Private Rust impl — NOT exposed to Python (separate impl block, no #[pymethods]).
impl CharacterTextSplitter {
    fn split_internal(&self, text: &str) -> Vec<String> {
        let parts: Vec<&str> = text.split(&*self.separator).collect();
        let mut chunks = Vec::new();
        let mut current = String::new();

        for part in parts {
            if current.len() + part.len() > self.chunk_size && !current.is_empty() {
                chunks.push(current.trim().to_string());
                // Carry overlap forward
                let overlap_start = current.len().saturating_sub(self.chunk_overlap);
                current = current[overlap_start..].to_string();
            }
            if !current.is_empty() {
                current.push_str(&self.separator);
            }
            current.push_str(part);
        }

        if !current.trim().is_empty() {
            chunks.push(current.trim().to_string());
        }

        chunks
    }
}
```

---

## Phase 3: Python Wrapper with Graceful Fallback

Add `TextSpitter/splitters.py`. The wrapper attempts to import the compiled Rust extension and falls back to a pure-Python implementation if unavailable. The Python fallback mirrors the same separator-based chunking logic as the Rust implementation — it must be fully implemented (not a stub) before merging to `main`.

```python
from __future__ import annotations

try:
    from text_spitter_rust import CharacterTextSplitter as _RustCharacterSplitter
    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


class CharacterTextSplitter:
    """
    Split text into overlapping chunks by a separator string.

    Uses the Rust backend automatically when available.
    Pass ``use_rust=False`` to force pure Python (useful for debugging
    or verifying parity test failures).
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n\n",
        use_rust: bool = True,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator

        if _RUST_AVAILABLE and use_rust:
            self._backend = _RustCharacterSplitter(chunk_size, chunk_overlap, separator)
            self._use_rust = True
        else:
            self._backend = None
            self._use_rust = False

    def split_text(self, text: str) -> list[str]:
        if self._use_rust:
            return self._backend.split_text(text)
        return self._split_text_python(text)

    def split_texts(self, texts: list[str]) -> list[list[str]]:
        """Batch split — dramatically faster with Rust backend."""
        if self._use_rust:
            return self._backend.split_texts(texts)
        return [self.split_text(t) for t in texts]

    def _split_text_python(self, text: str) -> list[str]:
        """Pure-Python fallback — must produce identical output to the Rust implementation."""
        parts = text.split(self.separator)
        chunks: list[str] = []
        current = ""

        for part in parts:
            if len(current) + len(part) > self.chunk_size and current:
                chunks.append(current.strip())
                overlap_start = max(0, len(current) - self.chunk_overlap)
                current = current[overlap_start:]
            if current:
                current += self.separator
            current += part

        if current.strip():
            chunks.append(current.strip())

        return chunks
```

---

## Phase 4: Build & Local Development

```bash
# Activate the project venv first (maturin installs into the active env)
source .venv/bin/activate   # or: uv run bash

# Development build (unoptimized, fast compile)
maturin develop

# Production build (optimized)
maturin develop --release

# Build a wheel for distribution
maturin build --release

# Install locally from wheel
pip install target/wheels/text_spitter_rust-*.whl
```

---

## Phase 5: Testing Strategy

### Parity Tests

Ensure Rust and Python backends produce identical output:

```python
# tests/test_parity.py

import pytest
from TextSpitter.splitters import CharacterTextSplitter

SAMPLE = "Lorem ipsum dolor sit amet. " * 500


def test_rust_python_parity():
    py_splitter = CharacterTextSplitter(use_rust=False)
    rs_splitter = CharacterTextSplitter(use_rust=True)
    assert py_splitter.split_text(SAMPLE) == rs_splitter.split_text(SAMPLE)


def test_batch_parity():
    docs = [SAMPLE] * 100
    py_results = CharacterTextSplitter(use_rust=False).split_texts(docs)
    rs_results = CharacterTextSplitter(use_rust=True).split_texts(docs)
    assert py_results == rs_results


@pytest.mark.parametrize("text", [
    "",                          # empty string
    "no separator here",         # no split point
    "\n\n" * 10,                 # only separators
    "a" * 5000,                  # single chunk larger than chunk_size
])
def test_edge_cases_parity(text):
    py = CharacterTextSplitter(use_rust=False).split_text(text)
    rs = CharacterTextSplitter(use_rust=True).split_text(text)
    assert py == rs
```

### Performance Benchmark

```python
# tests/bench_splitting.py

import time
from TextSpitter.splitters import CharacterTextSplitter

docs = ["Lorem ipsum dolor sit amet. " * 500] * 10_000

# Python baseline
start = time.perf_counter()
py = CharacterTextSplitter(use_rust=False)
for doc in docs:
    py.split_text(doc)
py_time = time.perf_counter() - start

# Rust batch
start = time.perf_counter()
rs = CharacterTextSplitter(use_rust=True)
rs.split_texts(docs)
rs_time = time.perf_counter() - start

print(f"Python: {py_time:.2f}s")
print(f"Rust:   {rs_time:.2f}s")
print(f"Speedup: {py_time / rs_time:.1f}x")
```

Expected results at 10,000 documents:

| Backend | Time    | Speedup |
|---------|---------|---------|
| Python  | ~45s    | 1x      |
| Rust    | ~1.2s   | ~37x    |

---

## Phase 6: CI/CD — GitHub Actions

Create `.github/workflows/ci-rust.yml` to lint, test, and build wheels across platforms:

```yaml
name: CI (Rust)

on: [push, pull_request]

jobs:
  lint-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy

      - name: cargo fmt --check
        run: cargo fmt --all -- --check

      - name: cargo clippy
        run: cargo clippy --all-targets --all-features -- -D warnings

  test:
    needs: lint-rust
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - uses: dtolnay/rust-toolchain@stable

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Build extension
        run: uv run maturin develop --release

      - name: Run tests
        run: uv run pytest tests/

  build-wheels:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v4

      # manylinux ensures Linux wheels run on glibc 2.17+ (broad compatibility)
      - uses: PyO3/maturin-action@v1
        with:
          command: build
          args: --release --out dist
          manylinux: auto   # produces manylinux2014-compatible wheels on Linux

      - uses: actions/upload-artifact@v4
        with:
          name: wheels-${{ matrix.os }}
          path: dist/

  benchmark:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - uses: dtolnay/rust-toolchain@stable

      - name: Install uv
        uses: astral-sh/setup-uv@v5

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Build extension (release)
        run: uv run maturin develop --release

      - name: Run benchmark
        run: uv run python tests/bench_splitting.py | tee benchmark_results.txt

      - uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark_results.txt
```

---

## Suggested Branch Strategy

```
main                  ← stable 1.x Python releases
feature/rust-backend  ← 2.0 development branch
```

Recommended workflow:

```bash
git checkout -b feature/rust-backend
# implement phases above
git push origin feature/rust-backend
# open PR → merge → tag v2.0.0
```

---

## Open Questions / Nice-to-Haves for 2.0

- [ ] Memory-mapped file processing for very large PDFs (`memmap2` crate)
- [ ] SIMD-accelerated string search for separator detection (`[features] simd = []`)
- [ ] Streaming iterator API (yield chunks vs. collect all)
- [ ] Publish to PyPI with `manylinux` wheels for zero-compile Linux installs (already wired in Phase 6 CI — needs a publish job triggered on release)
- [ ] `cargo bench` integration with criterion for reproducible micro-benchmarks

---

## References

- [PyO3 User Guide](https://pyo3.rs/)
- [Maturin Documentation](https://www.maturin.rs/)
- [Rayon — Data Parallelism for Rust](https://docs.rs/rayon/latest/rayon/)
- [TextSpitter 1.0 Repository](https://github.com/fsecada01/TextSpitter)
