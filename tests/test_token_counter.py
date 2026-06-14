"""
Tests for TokenCounter (Rust and Python fallback paths).
"""

import pytest

from TextSpitter import _RUST_AVAILABLE
from TextSpitter import TokenCounter as RustCounter
from TextSpitter._fallback import TokenCounter as FallbackCounter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["rust", "fallback"])
def Counter(request):
    if request.param == "rust":
        if not _RUST_AVAILABLE:
            pytest.skip("Rust extension not available")
        return RustCounter
    return FallbackCounter


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_default_model(Counter):
    c = Counter()
    assert c is not None


def test_unknown_model_raises(Counter):
    with pytest.raises((ValueError, Exception)):
        Counter(model="this-model-does-not-exist-xyz")


# ---------------------------------------------------------------------------
# count()
# ---------------------------------------------------------------------------

def test_count_returns_int(Counter):
    c = Counter()
    assert isinstance(c.count("hello"), int)


def test_count_empty_string(Counter):
    c = Counter()
    assert c.count("") == 0


def test_count_known_value(Counter):
    # cl100k_base: "Hello, world!" → 4 tokens
    c = Counter()
    assert c.count("Hello, world!") == 4


def test_count_longer_text(Counter):
    c = Counter()
    n = c.count("The quick brown fox jumps over the lazy dog.")
    assert n > 0


def test_count_is_positive(Counter):
    c = Counter()
    assert c.count("some text here") > 0


# ---------------------------------------------------------------------------
# count_batch()
# ---------------------------------------------------------------------------

def test_count_batch_returns_list(Counter):
    c = Counter()
    result = c.count_batch(["hello", "world"])
    assert isinstance(result, list)


def test_count_batch_empty(Counter):
    c = Counter()
    assert c.count_batch([]) == []


def test_count_batch_matches_singles(Counter):
    c = Counter()
    texts = ["Hello, world!", "foo bar baz", ""]
    batch = c.count_batch(texts)
    singles = [c.count(t) for t in texts]
    assert batch == singles


def test_count_batch_large(Counter):
    c = Counter()
    texts = [f"word number {i}" for i in range(100)]
    results = c.count_batch(texts)
    assert len(results) == 100
    assert all(isinstance(n, int) and n > 0 for n in results)


# ---------------------------------------------------------------------------
# truncate() — strategy: "end"
# ---------------------------------------------------------------------------

def test_truncate_end_returns_str(Counter):
    c = Counter()
    result = c.truncate("hello world", max_tokens=10)
    assert isinstance(result, str)


def test_truncate_end_no_op_when_under_limit(Counter):
    c = Counter()
    text = "hello"
    result = c.truncate(text, max_tokens=100, strategy="end")
    assert result == text


def test_truncate_end_respects_limit(Counter):
    c = Counter()
    text = " ".join([f"word{i}" for i in range(50)])
    result = c.truncate(text, max_tokens=10, strategy="end")
    assert c.count(result) <= 10


def test_truncate_end_preserves_start(Counter):
    c = Counter()
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
    result = c.truncate(text, max_tokens=3, strategy="end")
    # The first tokens should be kept
    assert result.startswith("alpha")


# ---------------------------------------------------------------------------
# truncate() — strategy: "middle"
# ---------------------------------------------------------------------------

def test_truncate_middle_respects_limit(Counter):
    c = Counter()
    text = " ".join([f"word{i}" for i in range(50)])
    result = c.truncate(text, max_tokens=10, strategy="middle")
    assert c.count(result) <= 10


def test_truncate_middle_preserves_start_and_end(Counter):
    c = Counter()
    # Build a 20-token text; truncate to 6 — should keep start and end tokens
    words = [f"w{i}" for i in range(20)]
    text = " ".join(words)
    result = c.truncate(text, max_tokens=6, strategy="middle")
    # The very first word and very last word should survive
    assert "w0" in result
    assert "w19" in result


# ---------------------------------------------------------------------------
# truncate() — strategy: "smart"
# ---------------------------------------------------------------------------

def test_truncate_smart_respects_limit(Counter):
    c = Counter()
    text = " ".join([f"word{i}" for i in range(50)])
    result = c.truncate(text, max_tokens=8, strategy="smart")
    assert c.count(result) <= 8


def test_truncate_smart_returns_nonempty(Counter):
    c = Counter()
    text = "one two three four five six seven eight"
    result = c.truncate(text, max_tokens=4, strategy="smart")
    assert len(result) > 0


# ---------------------------------------------------------------------------
# Alternative models (Rust path only — fallback may not have tiktoken)
# ---------------------------------------------------------------------------

def test_o200k_base_model():
    if not _RUST_AVAILABLE:
        pytest.skip("Rust extension not available")
    c = RustCounter(model="o200k_base")
    n = c.count("Hello, world!")
    assert n > 0


def test_cl100k_base_count_batch_parallel():
    """Smoke-test that GIL-released batch doesn't deadlock or corrupt."""
    if not _RUST_AVAILABLE:
        pytest.skip("Rust extension not available")
    c = RustCounter(model="cl100k_base")
    texts = ["sentence number " + str(i) for i in range(500)]
    results = c.count_batch(texts)
    assert len(results) == 500
    assert all(n > 0 for n in results)
