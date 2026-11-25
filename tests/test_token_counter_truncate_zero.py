"""Zero-token ``"middle"`` truncation in the Python fallback TokenCounter."""

import sys

import pytest

from TextSpitter._fallback import TokenCounter

TEXT = "one two three four five six seven eight"


class _WordEncoder:
    """Small stand-in for a tiktoken encoding: one token per word."""

    def __init__(self) -> None:
        self._vocab: list[str] = []

    def encode(self, text: str, allowed_special: str = "all") -> list[int]:
        ids = []
        for word in text.split():
            if word not in self._vocab:
                self._vocab.append(word)
            ids.append(self._vocab.index(word))
        return ids

    def decode(self, tokens: list[int]) -> str:
        return " ".join(self._vocab[t] for t in tokens)


@pytest.fixture
def word_counter(monkeypatch):
    """Counter on the word branch: tiktoken unimportable before construction."""
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    counter = TokenCounter()
    assert counter._bpe() is None
    return counter


@pytest.fixture
def token_counter(monkeypatch):
    """Counter on the token branch, using a stand-in encoder."""
    monkeypatch.setitem(sys.modules, "tiktoken", None)
    counter = TokenCounter()
    encoder = _WordEncoder()
    monkeypatch.setattr(counter, "_bpe", lambda: encoder)
    return counter


def test_word_branch_middle_zero_is_empty(word_counter):
    assert word_counter.truncate(TEXT, 0, strategy="middle") == ""


def test_token_branch_middle_zero_is_empty(token_counter):
    assert token_counter.truncate(TEXT, 0, strategy="middle") == ""


def test_word_branch_default_zero_is_empty(word_counter):
    assert word_counter.truncate(TEXT, 0) == ""


def test_token_branch_default_zero_is_empty(token_counter):
    assert token_counter.truncate(TEXT, 0) == ""


@pytest.mark.parametrize("max_tokens", [1, 2, 3])
def test_word_branch_middle_small_limits_unchanged(word_counter, max_tokens):
    words = TEXT.split()
    half = max_tokens // 2
    expected = " ".join(words[:half] + words[len(words) - (max_tokens - half) :])
    assert word_counter.truncate(TEXT, max_tokens, strategy="middle") == expected


@pytest.mark.parametrize("max_tokens", [1, 2, 3])
def test_token_branch_middle_small_limits(token_counter, max_tokens):
    words = TEXT.split()
    half = max_tokens // 2
    expected = " ".join(words[:half] + words[len(words) - (max_tokens - half) :])
    assert token_counter.truncate(TEXT, max_tokens, strategy="middle") == expected


@pytest.mark.parametrize("strategy", ["end", "middle"])
def test_short_text_returned_unchanged(word_counter, token_counter, strategy):
    text = "alpha  beta\tgamma"
    for counter in (word_counter, token_counter):
        assert counter.truncate(text, 3, strategy=strategy) == text
        assert counter.truncate(text, 10, strategy=strategy) == text


@pytest.mark.parametrize("strategy", ["end", "middle"])
def test_empty_text_with_zero_limit_unchanged(
    word_counter, token_counter, strategy
):
    for counter in (word_counter, token_counter):
        assert counter.truncate("", 0, strategy=strategy) == ""
