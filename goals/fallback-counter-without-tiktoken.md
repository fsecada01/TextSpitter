---
title: Test the fallback TokenCounter when tiktoken is unavailable
---

## Intent

`TextSpitter/_fallback.py` has a pure-Python `TokenCounter` for installs
without the Rust extension. When `tiktoken` cannot be imported, the
constructor swallows the `ImportError`, `_bpe()` returns `None`, and the
class approximates instead: `count` returns `len(text) // 4`, and
`truncate` keeps whole words, treating one word as one token. `tiktoken`
is always installed where the tests run, so none of this executes and a
regression in it would go unnoticed. Pin the current behaviour with
tests that run the real unavailable path, not a stand-in for it.

## Scope and non-goals

- In scope: one new test file, `tests/test_token_counter_no_tiktoken.py`.
- Do not change any file under `TextSpitter/` or `src/`: this goal records
  what the code does today, it does not change it.
- Do not edit existing test files, `tests/conftest.py`, `pyproject.toml`,
  `uv.lock`, `Cargo.toml`, `Cargo.lock` or `CHANGELOG.md`.
- No new dependency. Do not uninstall `tiktoken`.
- Import the class as
  `from TextSpitter._fallback import TokenCounter`, so the tests run the
  same way whether or not the Rust extension is built.
- Not in scope: `truncate` with `max_tokens` of zero or less. That case
  has a known defect with its own goal; do not test it here.

## Acceptance criteria

- [ ] `tiktoken` is made unimportable for the duration of each test
      (for example `monkeypatch.setitem(sys.modules, "tiktoken", None)`)
      **before** the counter is constructed. The constructor's
      `ImportError` handling and the real `_bpe` method both run; `_bpe`
      itself is not replaced. One test asserts that `_bpe()` returns
      `None` in that state.
- [ ] No test loads tiktoken's encoding data or needs the network: the
      file passes on a machine with no network and an empty tiktoken
      cache.
- [ ] `count` is tested for the empty string, a text shorter than four
      characters, and a longer text, and each expected value is
      `len(text) // 4`.
- [ ] `count_batch` is tested by calling `count_batch` alone and
      comparing its result with a list of expected numbers written out
      or computed as `len(text) // 4`. It includes the empty list. The
      expected values do not come from calling `count`.
- [ ] `truncate` with the default strategy returns the text unchanged
      when it has `max_tokens` words or fewer, and the first `max_tokens`
      words joined by single spaces when it has more. `strategy="end"`
      gives the same result as the default.
- [ ] `truncate` with `strategy="middle"` keeps the first
      `max_tokens // 2` words and the last `max_tokens - max_tokens // 2`
      words, tested for an even and an odd `max_tokens`, both at least 2.
- [ ] `truncate` with a strategy name the fallback does not implement
      (use `"smart"` and one made-up name) behaves exactly like `"end"`.
      This matches the Rust core, where any unrecognised name means
      `"end"`.
- [ ] Test names and comments describe only what the test asserts. No
      name or comment states what tiktoken would return unless the test
      checks it.
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
