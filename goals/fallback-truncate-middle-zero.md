---
title: Fix fallback truncate for zero and negative limits and keep whitespace
depends_on: [fallback-counter-without-tiktoken]
labels: [bug, testing]
---

## Intent

`TokenCounter.truncate` in `TextSpitter/_fallback.py` has three defects.
Fix all three.

1. **Zero limit.** The tail of a `"middle"` truncation is built with a
   negative slice, `words[-(max_tokens - half):]`. When `max_tokens` is
   0 that is `words[-0:]`, the whole list, so
   `truncate("one two three", 0, strategy="middle")` returns every word
   instead of an empty string. The token branch of the method has the
   same expression. The Rust core (`src/token.rs`) slices from
   `len - (max_tokens - half)` and returns an empty string.
2. **Negative limit.** A negative `max_tokens` is accepted and produces
   nonsense: `truncate(text, -1)` drops only the last word, and with
   `"middle"` it returns nearly the whole text. The Rust core takes an
   unsigned integer and rejects a negative one. The fallback must
   reject it too.
3. **Lost whitespace.** When `tiktoken` is unavailable the result is
   rebuilt with `" ".join(kept)`, which turns every newline, tab and
   run of spaces between kept words into one space. Extracted documents
   lose their layout. Kept words that were next to each other in the
   original must keep the original text between them.

## Scope and non-goals

- In scope: `TokenCounter.truncate` in `TextSpitter/_fallback.py`; one
  new test file, `tests/test_token_counter_truncate_edges.py`; and the
  existing `tests/test_token_counter_no_tiktoken.py`, only where a test
  there asserts that kept words are joined by single spaces. Update
  those assertions to the new behaviour; do not delete or skip a test.
- Keep the method's signature. Keep its results on the token branch for
  every `max_tokens` of 1 or more exactly as they are.
- Not in scope: a `"smart"` strategy for the fallback, any change under
  `src/`, any other class, and `count` or `count_batch`.
- Do not edit `tests/conftest.py`, `tests/test_token_counter.py`,
  `pyproject.toml`, `uv.lock`, `Cargo.toml`, `Cargo.lock` or
  `CHANGELOG.md`.
- No new dependency.

## Acceptance criteria

"Word branch" means `tiktoken` is unimportable, made so before the
counter is constructed (for example
`monkeypatch.setitem(sys.modules, "tiktoken", None)`). "Token branch"
means `_bpe` returns a small stand-in encoder whose `encode` and
`decode` are defined in the test file. No test loads tiktoken's
encoding data or uses the network.

Zero limit:

- [ ] On both branches, `truncate(text, 0, strategy="middle")` and
      `truncate(text, 0)` return `""` for a text of several words.
- [ ] `truncate("", 0)` returns `""`.

Negative limit:

- [ ] On both branches and for every strategy, a negative `max_tokens`
      raises `ValueError` whose message names `max_tokens`. The check
      comes first, so it raises even for an empty text.

Whitespace, word branch only. A word is a maximal run of non-whitespace
characters:

- [ ] A text with `max_tokens` words or fewer is returned unchanged,
      byte for byte.
- [ ] With the default strategy and more words than `max_tokens`, the
      result is the slice of the original text from the start of the
      first word to the end of word number `max_tokens`. Separators
      between those words are exactly as in the original; whitespace
      before the first word and after the last kept word is dropped.
      Tested with a text that mixes newlines, tabs and runs of spaces.
- [ ] With `strategy="middle"`, the head is the slice from the start of
      the first word to the end of word number `max_tokens // 2`, and
      the tail is the slice from the start of the first of the last
      `max_tokens - max_tokens // 2` words to the end of the last word.
      The result is head, one space, tail. When the head is empty
      (`max_tokens` of 1) the result is the tail alone. Tested for
      `max_tokens` of 1, 2, 3 and 4 on a text of at least six words
      with mixed separators.
- [ ] For a text whose words are separated by single spaces, with no
      leading or trailing whitespace, every result is the same string
      the method returned before this change, for `max_tokens` from 1
      up to the number of words, with both strategies.
- [ ] A strategy name the fallback does not implement still behaves
      exactly like `"end"`.

Boundaries, word branch:

- [ ] Tested with `max_tokens` equal to the number of words (unchanged)
      and one less than the number of words (truncated), for both
      strategies.

Overall:

- [ ] The new zero-limit and negative-limit tests fail against the code
      as it is before this change.
- [ ] Only `TextSpitter/_fallback.py`,
      `tests/test_token_counter_truncate_edges.py` and
      `tests/test_token_counter_no_tiktoken.py` change, and all tests
      pass.

## Verification

```
uv run --no-sync ruff check --no-fix .
uv run --no-sync ty check
uv run --no-sync pytest tests/ -q
```

Ruff uses an 80-column limit for `TextSpitter/`; `tests/*.py` is exempt
from the line-length rule.
