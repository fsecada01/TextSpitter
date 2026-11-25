"""
Tests for the fallback TokenCounter when tiktoken cannot be imported.

``sys.modules["tiktoken"]`` is set to ``None`` before each counter is built,
so ``import tiktoken`` raises ``ImportError``. The constructor and ``_bpe``
run unmodified; no encoding data is loaded and no network is used.
"""

import sys

import pytest

from TextSpitter._fallback import TokenCounter


@pytest.fixture
def counter(monkeypatch):
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    return TokenCounter()


WORDS = "w1 w2 w3 w4 w5 w6 w7 w8 w9 w10"


# ---------------------------------------------------------------------------
# Construction and _bpe
# ---------------------------------------------------------------------------


def test_constructor_does_not_raise_when_tiktoken_unimportable(monkeypatch):
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    c = TokenCounter(model="cl100k_base")
    assert c.model == "cl100k_base"


def test_bpe_returns_none_when_tiktoken_unimportable(counter):
    assert counter._bpe() is None


# ---------------------------------------------------------------------------
# count
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "",
        "abc",
        "a",
        "abcd",
        "abcdefg",
        "hello world, this is a longer piece of text for counting.",
    ],
)
def test_count_is_len_floor_div_four(counter, text):
    assert counter.count(text) == len(text) // 4


def test_count_literal_values(counter):
    assert counter.count("") == 0
    assert counter.count("abc") == 0
    assert counter.count("a" * 40) == 10
    assert counter.count("a" * 43) == 10


# ---------------------------------------------------------------------------
# count_batch
# ---------------------------------------------------------------------------


def test_count_batch_empty_list(counter):
    assert counter.count_batch([]) == []


def test_count_batch_values(counter):
    texts = ["", "abc", "a" * 8, "a" * 11, "a" * 100]
    assert counter.count_batch(texts) == [0, 0, 2, 2, 25]


def test_count_batch_matches_len_floor_div_four(counter):
    texts = ["", "xy", "wxyz", "some longer sample text here"]
    assert counter.count_batch(texts) == [len(t) // 4 for t in texts]


# ---------------------------------------------------------------------------
# truncate: default / "end"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("max_tokens", [10, 11, 100])
def test_truncate_unchanged_when_words_within_limit(counter, max_tokens):
    text = "w1  w2\tw3\nw4 w5 w6 w7 w8 w9 w10"
    assert counter.truncate(text, max_tokens) == text


def test_truncate_empty_text_unchanged(counter):
    assert counter.truncate("", 3) == ""


def test_truncate_keeps_first_words_when_over_limit(counter):
    assert counter.truncate(WORDS, 3) == "w1 w2 w3"


def test_truncate_keeps_original_separators_between_kept_words(counter):
    text = "w1   w2\n\nw3\tw4  w5"
    assert counter.truncate(text, 3) == "w1   w2\n\nw3"


def test_truncate_one_word_over_limit(counter):
    assert counter.truncate(WORDS, 9) == "w1 w2 w3 w4 w5 w6 w7 w8 w9"


def test_truncate_end_strategy_matches_default(counter):
    assert counter.truncate(WORDS, 4, strategy="end") == counter.truncate(
        WORDS, 4
    )
    assert counter.truncate(WORDS, 4, strategy="end") == "w1 w2 w3 w4"


def test_truncate_end_strategy_unchanged_when_within_limit(counter):
    text = "w1  w2 w3"
    assert counter.truncate(text, 3, strategy="end") == text


# ---------------------------------------------------------------------------
# truncate: "middle"
# ---------------------------------------------------------------------------


def test_truncate_middle_even_max_tokens(counter):
    # max_tokens=4: first 2 words and last 2 words.
    assert counter.truncate(WORDS, 4, strategy="middle") == "w1 w2 w9 w10"


def test_truncate_middle_odd_max_tokens(counter):
    # max_tokens=5: first 5 // 2 = 2 words and last 5 - 2 = 3 words.
    assert counter.truncate(WORDS, 5, strategy="middle") == "w1 w2 w8 w9 w10"


def test_truncate_middle_minimum_max_tokens(counter):
    assert counter.truncate(WORDS, 2, strategy="middle") == "w1 w10"


def test_truncate_middle_keeps_original_separators_within_head_and_tail(
    counter,
):
    text = "w1   w2\n\nw3\tw4  w5\tw6"
    assert counter.truncate(text, 4, strategy="middle") == "w1   w2 w5\tw6"


def test_truncate_middle_unchanged_when_words_within_limit(counter):
    text = "w1  w2 w3 w4"
    assert counter.truncate(text, 4, strategy="middle") == text
    assert counter.truncate(text, 9, strategy="middle") == text


# ---------------------------------------------------------------------------
# truncate: unimplemented strategy names behave like "end"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("strategy", ["smart", "not-a-real-strategy"])
@pytest.mark.parametrize("max_tokens", [2, 3, 5])
def test_truncate_unrecognised_strategy_matches_end(
    counter, strategy, max_tokens
):
    expected = counter.truncate(WORDS, max_tokens, strategy="end")
    assert counter.truncate(WORDS, max_tokens, strategy=strategy) == expected


@pytest.mark.parametrize("strategy", ["smart", "not-a-real-strategy"])
def test_truncate_unrecognised_strategy_keeps_first_words(counter, strategy):
    assert counter.truncate(WORDS, 3, strategy=strategy) == "w1 w2 w3"


@pytest.mark.parametrize("strategy", ["smart", "not-a-real-strategy"])
def test_truncate_unrecognised_strategy_unchanged_within_limit(
    counter, strategy
):
    text = "w1  w2 w3"
    assert counter.truncate(text, 3, strategy=strategy) == text
