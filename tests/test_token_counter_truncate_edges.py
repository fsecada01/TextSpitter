"""
Edge cases for ``TokenCounter.truncate`` in the pure-Python fallback.

Word branch: ``sys.modules["tiktoken"]`` is ``None`` before the counter is
built, so ``import tiktoken`` raises ``ImportError``.

Token branch: ``_bpe`` returns a tiny character-level stand-in encoder
defined in this file. No encoding data is loaded and no network is used.
"""

import sys

import pytest

from TextSpitter._fallback import TokenCounter


class _CharEncoder:
    """Stand-in encoder: one token per character."""

    def encode(self, text, allowed_special=None):
        return [ord(ch) for ch in text]

    def decode(self, tokens):
        return "".join(chr(t) for t in tokens)


@pytest.fixture
def word_counter(monkeypatch):
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    return TokenCounter()


@pytest.fixture
def token_counter(monkeypatch):
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    c = TokenCounter()
    monkeypatch.setattr(c, "_bpe", lambda: _CharEncoder())
    return c


@pytest.fixture(params=["word", "token"])
def any_counter(request):
    return request.getfixturevalue(f"{request.param}_counter")


STRATEGIES = ["end", "middle", "smart", "not-a-real-strategy"]

# Mixed separators: newlines, tabs, runs of spaces, leading/trailing space.
MIXED = "  a1 \n\n a2\tb3   b4\t\tc5\nc6  d7 d8 \n"
MIXED_WORDS = ["a1", "a2", "b3", "b4", "c5", "c6", "d7", "d8"]


# ---------------------------------------------------------------------------
# Zero limit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("strategy", ["end", "middle"])
def test_zero_limit_returns_empty_string(any_counter, strategy):
    assert any_counter.truncate("one two three", 0, strategy=strategy) == ""


def test_zero_limit_default_strategy_returns_empty_string(any_counter):
    assert any_counter.truncate("one two three", 0) == ""


def test_zero_limit_empty_text(any_counter):
    assert any_counter.truncate("", 0) == ""


# ---------------------------------------------------------------------------
# Negative limit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("max_tokens", [-1, -5])
@pytest.mark.parametrize("text", ["", "one two three"])
def test_negative_limit_raises_value_error(
    any_counter, strategy, max_tokens, text
):
    with pytest.raises(ValueError, match="max_tokens"):
        any_counter.truncate(text, max_tokens, strategy=strategy)


# ---------------------------------------------------------------------------
# Whitespace preservation (word branch)
# ---------------------------------------------------------------------------


def _span(text, first_word, last_word):
    start = text.index(MIXED_WORDS[first_word])
    end = text.index(MIXED_WORDS[last_word]) + len(MIXED_WORDS[last_word])
    return text[start:end]


@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("max_tokens", [8, 9, 50])
def test_within_limit_returned_byte_for_byte(
    word_counter, strategy, max_tokens
):
    assert word_counter.truncate(MIXED, max_tokens, strategy=strategy) == MIXED


@pytest.mark.parametrize("max_tokens", [1, 2, 3, 5, 7])
def test_end_keeps_original_separators(word_counter, max_tokens):
    expected = _span(MIXED, 0, max_tokens - 1)
    assert word_counter.truncate(MIXED, max_tokens) == expected
    assert (
        word_counter.truncate(MIXED, max_tokens, strategy="end") == expected
    )


def test_end_drops_leading_and_trailing_whitespace(word_counter):
    result = word_counter.truncate(MIXED, 4)
    assert result == "a1 \n\n a2\tb3   b4"
    assert result == result.strip()


@pytest.mark.parametrize("max_tokens", [1, 2, 3, 4, 5, 7])
def test_middle_keeps_original_separators(word_counter, max_tokens):
    n = len(MIXED_WORDS)
    half = max_tokens // 2
    tail = _span(MIXED, n - (max_tokens - half), n - 1)
    if half == 0:
        expected = tail
    else:
        expected = _span(MIXED, 0, half - 1) + " " + tail
    assert (
        word_counter.truncate(MIXED, max_tokens, strategy="middle") == expected
    )


def test_middle_literal_values(word_counter):
    assert word_counter.truncate(MIXED, 1, strategy="middle") == "d8"
    assert word_counter.truncate(MIXED, 2, strategy="middle") == "a1 d8"
    assert word_counter.truncate(MIXED, 3, strategy="middle") == "a1 d7 d8"
    assert (
        word_counter.truncate(MIXED, 4, strategy="middle")
        == "a1 \n\n a2 d7 d8"
    )


@pytest.mark.parametrize("strategy", ["smart", "not-a-real-strategy"])
@pytest.mark.parametrize("max_tokens", [1, 3, 5])
def test_unimplemented_strategy_behaves_like_end(
    word_counter, strategy, max_tokens
):
    assert word_counter.truncate(
        MIXED, max_tokens, strategy=strategy
    ) == word_counter.truncate(MIXED, max_tokens, strategy="end")


# ---------------------------------------------------------------------------
# Single-space text matches the previous behaviour
# ---------------------------------------------------------------------------


def _previous_word_truncate(text, max_tokens, strategy):
    words = text.split()
    if len(words) <= max_tokens:
        return text
    if strategy == "middle":
        half = max_tokens // 2
        kept = words[:half] + words[-(max_tokens - half) :]
    else:
        kept = words[:max_tokens]
    return " ".join(kept)


@pytest.mark.parametrize("strategy", ["end", "middle"])
def test_single_spaced_text_matches_previous_results(word_counter, strategy):
    text = " ".join(f"w{i}" for i in range(1, 11))
    for max_tokens in range(1, 11):
        assert word_counter.truncate(
            text, max_tokens, strategy=strategy
        ) == _previous_word_truncate(text, max_tokens, strategy)


# ---------------------------------------------------------------------------
# Boundaries (word branch)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("strategy", ["end", "middle"])
def test_boundary_equal_to_word_count_is_unchanged(word_counter, strategy):
    text = "a\nb  c\td"
    assert word_counter.truncate(text, 4, strategy=strategy) == text


def test_boundary_one_less_than_word_count_end(word_counter):
    assert word_counter.truncate("a\nb  c\td", 3) == "a\nb  c"


def test_boundary_one_less_than_word_count_middle(word_counter):
    # head: first 1 word; tail: last 2 words.
    assert word_counter.truncate("a\nb  c\td", 3, strategy="middle") == (
        "a c\td"
    )


# ---------------------------------------------------------------------------
# Token branch results for max_tokens >= 1 are unchanged
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("max_tokens", [1, 2, 3, 4, 5])
def test_token_branch_end(token_counter, max_tokens):
    assert token_counter.truncate("abcdefgh", max_tokens) == "abcdefgh"[
        :max_tokens
    ]


@pytest.mark.parametrize(
    ("max_tokens", "expected"),
    [(1, "h"), (2, "ah"), (3, "agh"), (4, "abgh"), (5, "abfgh")],
)
def test_token_branch_middle(token_counter, max_tokens, expected):
    result = token_counter.truncate("abcdefgh", max_tokens, strategy="middle")
    assert result == expected


def test_token_branch_within_limit_unchanged(token_counter):
    assert token_counter.truncate("abc", 3, strategy="middle") == "abc"
