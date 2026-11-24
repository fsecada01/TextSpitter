"""Pin the fallback TokenCounter behaviour when tiktoken is unavailable.

``_bpe`` is patched to return ``None`` on the counter under test. Every test
also asserts that the patched ``_bpe`` was consulted, so none of them can pass
by accident on the tiktoken path (e.g. for empty input, where both paths
return 0).
"""

import pytest

from TextSpitter._fallback import TokenCounter


class _NoBpe:
    """Stand-in for ``TokenCounter._bpe`` that records its calls."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return None


@pytest.fixture
def no_bpe(monkeypatch):
    spy = _NoBpe()
    counter = TokenCounter()
    monkeypatch.setattr(counter, "_bpe", spy)
    return counter, spy


class TestCountWithoutTiktoken:
    @pytest.mark.parametrize(
        "text",
        [
            "",
            "abc",
            "a",
            "abcd",
            "hello world, this is a longer sentence of text.",
            "x" * 103,
        ],
    )
    def test_count_is_len_div_four(self, no_bpe, text):
        counter, spy = no_bpe
        assert counter.count(text) == len(text) // 4
        assert spy.calls == 1

    def test_count_differs_from_tiktoken_for_short_word(self, no_bpe):
        # Three characters: the approximation gives 0, tiktoken gives 1.
        counter, spy = no_bpe
        assert counter.count("abc") == 0
        assert spy.calls == 1

    def test_count_differs_from_tiktoken_for_long_text(self, no_bpe):
        # 40 identical characters: the approximation yields 10, tiktoken 5.
        counter, spy = no_bpe
        text = "a" * 40
        assert counter.count(text) == 10
        assert spy.calls == 1


class TestCountBatchWithoutTiktoken:
    def test_count_batch_agrees_with_count(self, no_bpe):
        counter, spy = no_bpe
        texts = ["", "abc", "abcdefgh", "x" * 37, "hello world, longer text"]
        expected = [len(t) // 4 for t in texts]
        assert counter.count_batch(texts) == expected
        assert counter.count_batch(texts) == [counter.count(t) for t in texts]
        assert spy.calls >= len(texts)


class TestTruncateEndWithoutTiktoken:
    def test_unchanged_when_fewer_words_than_max(self, no_bpe):
        counter, spy = no_bpe
        # Two long words: far more than 3 real tokens, but only 2 words.
        text = "internationalization   counterrevolutionary"
        assert counter.truncate(text, 3) == text
        assert spy.calls == 1

    def test_unchanged_when_exactly_max_words(self, no_bpe):
        counter, spy = no_bpe
        text = "antidisestablishmentarianism pneumonoultramicroscopic"
        assert counter.truncate(text, 2) == text
        assert spy.calls == 1

    def test_keeps_first_max_words_joined_by_single_spaces(self, no_bpe):
        counter, spy = no_bpe
        text = "one  two\tthree\nfour   five six"
        assert counter.truncate(text, 3) == "one two three"
        assert spy.calls == 1

    def test_end_strategy_is_the_default(self, no_bpe):
        counter, spy = no_bpe
        text = "alpha beta gamma delta epsilon"
        assert counter.truncate(text, 2) == counter.truncate(
            text, 2, strategy="end"
        )
        assert counter.truncate(text, 2) == "alpha beta"
        assert spy.calls == 3


class TestTruncateMiddleWithoutTiktoken:
    def test_even_max_tokens(self, no_bpe):
        counter, spy = no_bpe
        text = "w1 w2 w3 w4 w5 w6 w7 w8"
        # 4 // 2 == 2 from the front, 4 - 2 == 2 from the back.
        assert counter.truncate(text, 4, strategy="middle") == "w1 w2 w7 w8"
        assert spy.calls == 1

    def test_odd_max_tokens(self, no_bpe):
        counter, spy = no_bpe
        text = "w1 w2 w3 w4 w5 w6 w7 w8"
        # 5 // 2 == 2 from the front, 5 - 2 == 3 from the back.
        assert counter.truncate(text, 5, strategy="middle") == "w1 w2 w6 w7 w8"
        assert spy.calls == 1

    def test_middle_unchanged_when_within_limit(self, no_bpe):
        counter, spy = no_bpe
        text = "internationalization   counterrevolutionary"
        assert counter.truncate(text, 3, strategy="middle") == text
        assert spy.calls == 1
