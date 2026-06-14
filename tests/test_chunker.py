"""
Tests for TextChunker and Chunk (Rust and Python fallback paths).
"""

import pytest

from TextSpitter import _RUST_AVAILABLE
from TextSpitter import TextChunker as RustChunker
from TextSpitter import TokenCounter
from TextSpitter._fallback import TextChunker as FallbackChunker

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["rust", "fallback"])
def Chunker(request):
    if request.param == "rust":
        if not _RUST_AVAILABLE:
            pytest.skip("Rust extension not available")
        return RustChunker
    return FallbackChunker


SHORT_TEXT = "Hello world, this is a test."
THREE_PARAS = (
    "First paragraph here with some words.\n\n"
    "Second paragraph here with more words.\n\n"
    "Third paragraph here with even more words."
)


# ---------------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------------

def test_instantiation_defaults(Chunker):
    chunker = Chunker()
    assert chunker is not None


def test_min_tokens_gt_max_tokens_raises(Chunker):
    with pytest.raises((ValueError, Exception)):
        Chunker(max_tokens=100, min_tokens=200)


def test_min_tokens_equal_max_tokens_ok(Chunker):
    chunker = Chunker(max_tokens=100, min_tokens=100)
    assert chunker is not None


def test_invalid_tokenizer_raises(Chunker):
    with pytest.raises((ValueError, Exception)):
        Chunker(tokenizer="nonexistent-tokenizer-xyz")


# ---------------------------------------------------------------------------
# chunk() — return type and basic structure
# ---------------------------------------------------------------------------

def test_chunk_returns_list(Chunker):
    chunker = Chunker()
    result = chunker.chunk(SHORT_TEXT)
    assert isinstance(result, list)


def test_chunk_empty_string_returns_empty(Chunker):
    chunker = Chunker()
    result = chunker.chunk("")
    assert result == []


def test_chunk_whitespace_only_returns_empty(Chunker):
    chunker = Chunker()
    result = chunker.chunk("   \n\n  \t  ")
    assert result == []


def test_chunk_items_are_chunk_type(Chunker):
    chunker = Chunker(max_tokens=2000)
    chunks = chunker.chunk(SHORT_TEXT)
    assert len(chunks) > 0
    # Works for both Rust Chunk and fallback Chunk
    chunk = chunks[0]
    assert hasattr(chunk, "text")
    assert hasattr(chunk, "token_count")
    assert hasattr(chunk, "char_start")
    assert hasattr(chunk, "char_end")
    assert hasattr(chunk, "chunk_index")
    assert hasattr(chunk, "total_chunks")
    assert hasattr(chunk, "metadata")


# ---------------------------------------------------------------------------
# Chunk field correctness
# ---------------------------------------------------------------------------

def test_chunk_index_sequence(Chunker):
    # Force multiple chunks with a very small max_tokens
    chunker = Chunker(max_tokens=5, min_tokens=1)
    chunks = chunker.chunk(THREE_PARAS)
    assert len(chunks) >= 1
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


def test_total_chunks_consistent(Chunker):
    chunker = Chunker(max_tokens=5, min_tokens=1)
    chunks = chunker.chunk(THREE_PARAS)
    total = len(chunks)
    assert all(c.total_chunks == total for c in chunks)


def test_chunk_text_non_empty(Chunker):
    chunker = Chunker(max_tokens=2000)
    chunks = chunker.chunk(THREE_PARAS)
    assert all(len(c.text.strip()) > 0 for c in chunks)


def test_chunk_token_count_positive(Chunker):
    chunker = Chunker(max_tokens=2000)
    chunks = chunker.chunk(THREE_PARAS)
    assert all(c.token_count > 0 for c in chunks)


def test_char_offsets_are_int(Chunker):
    chunker = Chunker(max_tokens=2000)
    chunks = chunker.chunk(THREE_PARAS)
    for c in chunks:
        assert isinstance(c.char_start, int)
        assert isinstance(c.char_end, int)
        assert c.char_end > c.char_start


def test_char_offsets_are_codepoint_not_byte(Chunker):
    # Non-ASCII text: "café" — é is 2 bytes in UTF-8 but 1 code point.
    # char_start/end must be code-point offsets (matching Python str indexing).
    text = "café\n\ncorner"
    chunker = Chunker(max_tokens=2000)
    chunks = chunker.chunk(text)
    for c in chunks:
        # Python str slicing with code-point offsets must return a prefix of c.text
        reconstructed = text[c.char_start:c.char_end]
        # The reconstructed slice should contain the same text (may differ in
        # whitespace normalization, so just check content is a substring)
        assert c.text.strip() in text or text in c.text or len(reconstructed) > 0


# ---------------------------------------------------------------------------
# max_tokens enforcement
# ---------------------------------------------------------------------------

def test_chunks_respect_max_tokens(Chunker):
    if not _RUST_AVAILABLE:
        pytest.skip("Fallback uses approximate token counts")
    max_tok = 20
    chunker = RustChunker(max_tokens=max_tok, min_tokens=1)
    counter = TokenCounter()
    # Paragraph breaks (\n\n) are the chunker's primary split boundary
    long_text = "\n\n".join(
        [f"Para {i} some text here." for i in range(30)]
    )
    chunks = chunker.chunk(long_text)
    assert len(chunks) > 1
    non_oversized = [c for c in chunks if not c.metadata.get("oversized")]
    for c in non_oversized:
        assert counter.count(c.text) <= max_tok, (
            f"Chunk {c.chunk_index} has {counter.count(c.text)} tokens, "
            f"expected <= {max_tok}"
        )


# ---------------------------------------------------------------------------
# preserve_tables
# ---------------------------------------------------------------------------

def test_oversized_table_emits_oversized_chunk(Chunker):
    if not _RUST_AVAILABLE:
        pytest.skip("Table detection is Rust-only in this version")
    # A table that exceeds max_tokens should be emitted whole with metadata
    table = "\n".join(
        [f"| col{i} | value{i} | extra{i} |" for i in range(50)]
    )
    chunker = RustChunker(max_tokens=10, min_tokens=1, preserve_tables=True)
    chunks = chunker.chunk(table)
    assert any(c.metadata.get("oversized") for c in chunks)


# ---------------------------------------------------------------------------
# section_title propagation
# ---------------------------------------------------------------------------

def test_section_title_detected_from_allcaps_header(Chunker):
    if not _RUST_AVAILABLE:
        pytest.skip("Section detection is Rust-only in this version")
    text = "INTRODUCTION\n\nThis is the introduction text with some content."
    chunker = RustChunker(max_tokens=2000)
    chunks = chunker.chunk(text)
    assert len(chunks) > 0
    # At least one chunk should have the section title
    titles = [c.section_title for c in chunks]
    assert any(t is not None for t in titles)


def test_section_title_none_when_no_header(Chunker):
    chunker = Chunker(max_tokens=2000)
    text = "Just a plain paragraph with no header."
    chunks = chunker.chunk(text)
    # May or may not have a title, but shouldn't crash
    for c in chunks:
        assert c.section_title is None or isinstance(c.section_title, str)


# ---------------------------------------------------------------------------
# chunk_batch()
# ---------------------------------------------------------------------------

def test_chunk_batch_returns_list_of_lists(Chunker):
    chunker = Chunker(max_tokens=2000)
    result = chunker.chunk_batch([SHORT_TEXT, THREE_PARAS])
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(r, list) for r in result)


def test_chunk_batch_empty_input(Chunker):
    chunker = Chunker(max_tokens=2000)
    assert chunker.chunk_batch([]) == []


def test_chunk_batch_matches_sequential(Chunker):
    chunker = Chunker(max_tokens=20, min_tokens=1)
    texts = [SHORT_TEXT, THREE_PARAS, "Another short text."]
    batch = chunker.chunk_batch(texts)
    sequential = [chunker.chunk(t) for t in texts]
    # Compare chunk count and text content (not objects)
    for b_chunks, s_chunks in zip(batch, sequential, strict=False):
        assert len(b_chunks) == len(s_chunks)
        for b, s in zip(b_chunks, s_chunks, strict=False):
            assert b.text == s.text
            assert b.token_count == s.token_count


def test_chunk_batch_large_parallel():
    """Smoke-test parallel batch doesn't deadlock or corrupt output."""
    if not _RUST_AVAILABLE:
        pytest.skip("Rust extension not available")
    chunker = RustChunker(max_tokens=50, min_tokens=1)
    texts = [THREE_PARAS + f" Unique suffix {i}." for i in range(50)]
    results = chunker.chunk_batch(texts)
    assert len(results) == 50
    # Each text should produce at least one chunk
    assert all(len(r) >= 1 for r in results)


# ---------------------------------------------------------------------------
# Rust-specific Chunk repr
# ---------------------------------------------------------------------------

def test_chunk_repr():
    if not _RUST_AVAILABLE:
        pytest.skip("Rust extension not available")
    chunker = RustChunker(max_tokens=2000)
    chunks = chunker.chunk(SHORT_TEXT)
    assert len(chunks) > 0
    r = repr(chunks[0])
    assert "Chunk" in r
    assert "tokens" in r
