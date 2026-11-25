---
title: Fix fallback truncate returning everything for a zero-token middle
---

## Intent

`TokenCounter.truncate` in `TextSpitter/_fallback.py` builds the tail of
a `"middle"` truncation with a negative slice,
`words[-(max_tokens - half):]`. When `max_tokens` is 0 that is
`words[-0:]`, which is the whole list, so
`truncate("one two three", 0, strategy="middle")` returns every word
instead of an empty string. The same expression is used for the token
list on the tiktoken branch of the same method, with the same result.

The Rust core (`src/token.rs`) slices from `len - (max_tokens - half)`
and returns an empty string. Make the Python fallback agree with it.

## Scope and non-goals

- In scope: `TokenCounter.truncate` in `TextSpitter/_fallback.py`, both
  the word branch (no tiktoken) and the token branch, and one new test
  file, `tests/test_token_counter_truncate_zero.py`.
- Change only how the tail of a `"middle"` truncation is sliced. Keep
  the method's signature, its other strategies, and its results for
  every `max_tokens` of 1 or more exactly as they are.
- Not in scope: negative `max_tokens`, a `"smart"` strategy for the
  fallback, any change under `src/`, and any other class.
- Do not edit existing test files, `tests/conftest.py`, `pyproject.toml`,
  `uv.lock`, `Cargo.toml`, `Cargo.lock` or `CHANGELOG.md`.
- No new dependency.

## Acceptance criteria

- [ ] With `tiktoken` unimportable (made so before the counter is
      constructed), `truncate(text, 0, strategy="middle")` returns `""`
      for a text of several words.
- [ ] On the token branch, the same call returns `""`. Test it without
      loading tiktoken's encoding data or using the network, by having
      `_bpe` return a small stand-in encoder whose `encode` and `decode`
      are defined in the test file.
- [ ] `truncate(text, 0)` with the default strategy still returns `""`
      on both branches.
- [ ] `strategy="middle"` with `max_tokens` of 1, 2 and 3 on a text of
      at least six words returns the same strings as before this change
      on the word branch: the first `max_tokens // 2` words and the last
      `max_tokens - max_tokens // 2` words, joined by single spaces.
- [ ] A text with `max_tokens` words or fewer is still returned
      unchanged, including the empty string with `max_tokens` of 0.
- [ ] The new zero-token tests fail against the code as it is before
      this change.
- [ ] Only `TextSpitter/_fallback.py` and
      `tests/test_token_counter_truncate_zero.py` change, and all
      existing tests still pass.

## Verification

```
uv run --no-sync ruff check --no-fix .
uv run --no-sync ty check
uv run --no-sync pytest tests/ -q
```

Ruff uses an 80-column limit for `TextSpitter/`; `tests/*.py` is exempt
from the line-length rule.
