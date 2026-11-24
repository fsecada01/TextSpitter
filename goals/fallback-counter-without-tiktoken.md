---
title: Test the fallback TokenCounter when tiktoken is unavailable
---

## Intent

`TextSpitter/_fallback.py` has a pure-Python `TokenCounter` for installs
without the Rust extension. When `tiktoken` cannot be loaded, its `_bpe()`
method returns `None` and the class approximates instead: `count` returns
`len(text) // 4`, and `truncate` keeps whole words, treating one word as
one token. `tiktoken` is always installed where the tests run, so these
branches never execute and a regression in them would go unnoticed. Pin
the current behaviour with tests.

## Scope and non-goals

- In scope: one new test file, `tests/test_token_counter_no_tiktoken.py`.
- Do not change any file under `TextSpitter/` or `src/`: this goal records
  what the code does today, it does not change it.
- Do not edit existing test files, `tests/conftest.py`, `pyproject.toml`,
  `uv.lock`, `Cargo.toml`, `Cargo.lock` or `CHANGELOG.md`.
- No new dependency. Do not uninstall `tiktoken` or tamper with
  `sys.modules`; make `_bpe` return `None` for the counter under test with
  `monkeypatch` (or `pytest-mock`, which is already a dev dependency).
- Import the class as
  `from TextSpitter._fallback import TokenCounter`, so the tests run the
  same way whether or not the Rust extension is built.

## Acceptance criteria

- [ ] With `_bpe` returning `None`, `count` is tested for the empty
      string, a text shorter than four characters, and a longer text, and
      each expected value is `len(text) // 4`.
- [ ] `count_batch` is tested on the same path and agrees with `count`
      for each item.
- [ ] `truncate` with the default strategy returns the text unchanged
      when it has `max_tokens` words or fewer, and the first `max_tokens`
      words joined by single spaces when it has more.
- [ ] `truncate` with `strategy="middle"` keeps the first
      `max_tokens // 2` words and the last `max_tokens - max_tokens // 2`
      words, tested for an even and an odd `max_tokens`.
- [ ] Every test would fail if the no-tiktoken branch were removed, which
      means each one asserts a value that differs from what the tiktoken
      path returns for the same input, or asserts that `_bpe` was the
      patched one.
- [ ] No file outside `tests/test_token_counter_no_tiktoken.py` changes,
      and all existing tests still pass.

## Verification

```
uv run --no-sync ruff check --no-fix .
uv run --no-sync ty check
uv run --no-sync pytest tests/ -q
```

Ruff uses an 80-column limit, but `tests/*.py` is exempt from the
line-length rule.
