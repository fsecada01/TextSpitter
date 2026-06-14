"""
Integration tests: end-to-end pipeline through all Rust-backed components,
plus compatibility checks between the Rust and Python fallback paths.
"""

import pytest

from TextSpitter import (
    _RUST_AVAILABLE,
    TextChunker,
    TextNormalizer,
    TokenCounter,
    detect_encoding,
)
from TextSpitter._fallback import TextChunker as FallbackChunker
from TextSpitter._fallback import TextNormalizer as FallbackNormalizer
from TextSpitter._fallback import detect_encoding as fallback_detect

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WAIVER_EXCERPT = """\
DEPARTMENT OF HEALTH AND HUMAN SERVICES

SECTION 1: ELIGIBILITY CRITERIA

To qualify for Medicaid waiver services, individuals must meet the following
requirements as established by federal and state regulations.

SECTION 2: SERVICE DEFINITIONS

Home and community-based services include personal care, respite care,
and supported employment as defined in 42 C.F.R. § 441.301.

SECTION 3: PROVIDER REQUIREMENTS

All providers must maintain current licensure and comply with state
background check requirements under applicable statutes.
"""

OCR_TEXT = (
    "The patiern presented with a diagrnosis of hypertensi0n. "
    "NPI: 1234567890. Service code T2025 was billed on 5l3/2024."
)


# ---------------------------------------------------------------------------
# Encode → decode pipeline (detect_encoding + core.py integration)
# ---------------------------------------------------------------------------

def test_encode_detect_decode_roundtrip():
    original = "Résumé: café, naïve, Ångström"
    raw = original.encode("utf-8")
    detected = detect_encoding(raw)
    assert detected == "utf-8"
    assert raw.decode(detected) == original


def test_windows1252_encode_detect_decode():
    original = "He said “hello” and ‘goodbye’"
    raw = original.encode("cp1252")
    detected = detect_encoding(raw)
    decoded = raw.decode(detected, errors="replace")
    # Content should survive the round-trip
    assert "hello" in decoded
    assert "goodbye" in decoded


# ---------------------------------------------------------------------------
# Normalize → chunk pipeline
# ---------------------------------------------------------------------------

def test_normalize_then_chunk(Norm=None):
    norm = TextNormalizer(collapse_whitespace=True)
    chunker = TextChunker(max_tokens=100, min_tokens=5)

    clean = norm.normalize(WAIVER_EXCERPT)
    assert isinstance(clean, str)
    chunks = chunker.chunk(clean)
    assert len(chunks) >= 1
    # Reconstructed content should contain original text words
    all_text = " ".join(c.text for c in chunks)
    assert "eligibility" in all_text.lower()
    assert "provider" in all_text.lower()


def test_normalize_then_chunk_token_counts_consistent():
    if not _RUST_AVAILABLE:
        pytest.skip("Rust extension not available for consistent token counts")
    norm = TextNormalizer(collapse_whitespace=True)
    counter = TokenCounter()
    chunker = TextChunker(max_tokens=50, min_tokens=1)

    clean = norm.normalize(WAIVER_EXCERPT)
    chunks = chunker.chunk(clean)
    for c in chunks:
        actual = counter.count(c.text)
        # token_count on the chunk should be close to independently counted value
        assert abs(actual - c.token_count) <= 2, (
            f"Chunk reports {c.token_count} tokens, counter says {actual}"
        )


# ---------------------------------------------------------------------------
# Section structure preserved through pipeline
# ---------------------------------------------------------------------------

def test_section_titles_detected_in_waiver():
    if not _RUST_AVAILABLE:
        pytest.skip("Section detection is Rust-only")
    norm = TextNormalizer(collapse_whitespace=True)
    chunker = TextChunker(max_tokens=2000)
    clean = norm.normalize(WAIVER_EXCERPT)
    chunks = chunker.chunk(clean)
    titles = [c.section_title for c in chunks if c.section_title]
    # At least one section header should be detected
    assert len(titles) > 0


# ---------------------------------------------------------------------------
# Fallback ↔ Rust interface compatibility
# ---------------------------------------------------------------------------

def test_fallback_and_rust_detect_encoding_same_utf8():
    data = "Hello, world!".encode("utf-8")
    rust_result = detect_encoding(data)
    fallback_result = fallback_detect(data)
    # Both must return valid Python codec names and produce the same decoded text
    assert data.decode(rust_result) == data.decode(fallback_result)


def test_fallback_and_rust_normalizer_same_interface():
    rust_norm = TextNormalizer(collapse_whitespace=True)
    fallback_norm = FallbackNormalizer(collapse_whitespace=True)
    text = "  hello   world  \n\n\n  foo  "
    assert rust_norm.normalize(text) == fallback_norm.normalize(text)


def test_fallback_and_rust_normalizer_batch_same_interface():
    texts = ["  foo  bar  ", "  baz  qux  "]
    rust_norm = TextNormalizer(collapse_whitespace=True)
    fallback_norm = FallbackNormalizer(collapse_whitespace=True)
    assert rust_norm.normalize_batch(texts) == fallback_norm.normalize_batch(texts)


def test_fallback_chunker_same_field_names():
    """Both paths must expose the same Chunk field names."""
    rust_chunker = TextChunker(max_tokens=2000) if _RUST_AVAILABLE else None
    fallback_chunker = FallbackChunker(max_tokens=2000)

    text = "Some text here.\n\nMore text here."
    fb_chunks = fallback_chunker.chunk(text)
    assert len(fb_chunks) > 0
    fb = fb_chunks[0]

    required_attrs = [
        "text", "token_count", "char_start", "char_end",
        "section_title", "chunk_index", "total_chunks", "metadata",
    ]
    for attr in required_attrs:
        assert hasattr(fb, attr), f"Fallback Chunk missing attribute: {attr}"

    if rust_chunker is not None:
        rust_chunks = rust_chunker.chunk(text)
        assert len(rust_chunks) > 0
        rc = rust_chunks[0]
        for attr in required_attrs:
            assert hasattr(rc, attr), f"Rust Chunk missing attribute: {attr}"


def test_rust_available_flag_bool():
    assert isinstance(_RUST_AVAILABLE, bool)


# ---------------------------------------------------------------------------
# Large document stress test
# ---------------------------------------------------------------------------

def test_large_document_pipeline():
    """Normalise and chunk a large synthetic document without errors."""
    # Build a ~50-section synthetic document
    sections = []
    for i in range(50):
        sections.append(f"SECTION {i + 1}: TOPIC {i + 1}\n")
        sections.append(
            f"This is the body of section {i + 1}. " * 10 + "\n"
        )
    large_doc = "\n".join(sections)

    norm = TextNormalizer(collapse_whitespace=True)
    chunker = TextChunker(max_tokens=200, min_tokens=10)

    clean = norm.normalize(large_doc)
    chunks = chunker.chunk(clean)

    assert len(chunks) > 1
    # Indices must be gapless
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
    # All chunks must have positive token counts
    assert all(c.token_count > 0 for c in chunks)


# ---------------------------------------------------------------------------
# OCR repair + chunking
# ---------------------------------------------------------------------------

def test_ocr_repair_then_chunk():
    norm = TextNormalizer(repair_ocr=True, collapse_whitespace=True)
    chunker = TextChunker(max_tokens=500)

    clean = norm.normalize(OCR_TEXT)
    chunks = chunker.chunk(clean)

    assert len(chunks) >= 1
    all_text = " ".join(c.text for c in chunks)
    # OCR repair should have fixed "diagrnosis" → "diagnosis" (rn→m between lowercase)
    assert "diagnosis" in all_text or "diagmosis" in all_text  # partial fix is ok
