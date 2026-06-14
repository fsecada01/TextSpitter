"""
Tests for TextNormalizer (Rust and Python fallback paths).
"""

import unicodedata

import pytest

from TextSpitter import _RUST_AVAILABLE
from TextSpitter import TextNormalizer as RustNormalizer
from TextSpitter._fallback import TextNormalizer as FallbackNormalizer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["rust", "fallback"])
def Norm(request):
    """Return the TextNormalizer class for the current path under test."""
    if request.param == "rust":
        if not _RUST_AVAILABLE:
            pytest.skip("Rust extension not available")
        return RustNormalizer
    return FallbackNormalizer


# ---------------------------------------------------------------------------
# Default construction
# ---------------------------------------------------------------------------

def test_instantiation_defaults(Norm):
    norm = Norm()
    assert norm is not None


def test_normalize_returns_str(Norm):
    norm = Norm()
    result = norm.normalize("hello")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Unicode normalization forms
# ---------------------------------------------------------------------------

def test_nfc_composes_accents(Norm):
    # NFD café: e + combining acute accent (two code points)
    nfd_cafe = "café"
    norm = Norm(unicode_form="NFC")
    result = norm.normalize(nfd_cafe)
    assert result == "café"
    assert unicodedata.is_normalized("NFC", result)


def test_nfd_decomposes_accents(Norm):
    composed = "café"
    norm = Norm(unicode_form="NFD")
    result = norm.normalize(composed)
    # NFD splits é into e + combining acute
    assert len(result) > len(composed)
    assert unicodedata.is_normalized("NFD", result)


def test_nfkc_collapses_compatibility_chars(Norm):
    # ﬁ (U+FB01, fi ligature) → "fi" under NFKC
    norm = Norm(unicode_form="NFKC")
    result = norm.normalize("ﬁ")
    assert result == "fi"


# ---------------------------------------------------------------------------
# Whitespace collapsing
# ---------------------------------------------------------------------------

def test_collapses_horizontal_whitespace(Norm):
    norm = Norm(collapse_whitespace=True)
    assert norm.normalize("hello   world") == "hello world"


def test_collapses_tabs(Norm):
    norm = Norm(collapse_whitespace=True)
    assert norm.normalize("a\t\tb") == "a b"


def test_preserves_single_newlines(Norm):
    norm = Norm(collapse_whitespace=True)
    result = norm.normalize("line1\nline2")
    assert "\n" in result


def test_collapses_triple_newlines_to_double(Norm):
    norm = Norm(collapse_whitespace=True)
    result = norm.normalize("a\n\n\n\nb")
    assert "\n\n\n" not in result
    assert "\n\n" in result


def test_strips_leading_trailing_whitespace(Norm):
    norm = Norm(collapse_whitespace=True)
    assert norm.normalize("  hello  ") == "hello"


def test_whitespace_disabled_preserves_spaces(Norm):
    norm = Norm(collapse_whitespace=False)
    result = norm.normalize("a   b")
    assert "   " in result


# ---------------------------------------------------------------------------
# OCR artifact repair
# ---------------------------------------------------------------------------

def test_ocr_rn_to_m_between_lowercase(Norm):
    norm = Norm(repair_ocr=True)
    # "clirnb" → "climb" (the 'rn' between 'i' and 'b' becomes 'm')
    assert norm.normalize("clirnb") == "climb"


def test_ocr_l_to_1_between_digits(Norm):
    norm = Norm(repair_ocr=True)
    # "5l3" → "513"
    assert norm.normalize("5l3") == "513"


def test_ocr_repair_does_not_touch_uppercase(Norm):
    norm = Norm(repair_ocr=True)
    # Capital RN should not be replaced
    result = norm.normalize("CORN")
    assert result == "CORN"


def test_ocr_disabled_leaves_artifacts(Norm):
    norm = Norm(repair_ocr=False)
    assert norm.normalize("5l3") == "5l3"


# ---------------------------------------------------------------------------
# Header/footer stripping
# ---------------------------------------------------------------------------

def test_strip_headers_noop_without_formfeed(Norm):
    norm = Norm(strip_headers_footers=True)
    text = "Page header\nContent\nPage footer"
    # No \f → no page boundaries detected → text returned unchanged
    result = norm.normalize(text)
    # Content must be preserved
    assert "Content" in result


def test_strip_headers_removes_repeated_lines(Norm):
    norm = Norm(strip_headers_footers=True)
    # Three pages, each with the same header "CONFIDENTIAL"
    pages = [
        "CONFIDENTIAL\nPage one content",
        "CONFIDENTIAL\nPage two content",
        "CONFIDENTIAL\nPage three content",
    ]
    text = "\x0c".join(pages)
    result = norm.normalize(text)
    # Content must survive
    assert "one content" in result
    assert "two content" in result
    # The repeated header should be stripped from at least some pages
    confidential_count = result.count("CONFIDENTIAL")
    assert confidential_count < 3


def test_strip_headers_disabled_preserves_all(Norm):
    norm = Norm(strip_headers_footers=False)
    pages = ["HDR\nBody1", "HDR\nBody2"]
    text = "\x0c".join(pages)
    result = norm.normalize(text)
    assert result.count("HDR") == 2


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def test_normalize_batch_returns_list(Norm):
    norm = Norm()
    result = norm.normalize_batch(["foo", "bar"])
    assert isinstance(result, list)
    assert len(result) == 2


def test_normalize_batch_empty_list(Norm):
    norm = Norm()
    assert norm.normalize_batch([]) == []


def test_normalize_batch_matches_single(Norm):
    norm = Norm(collapse_whitespace=True)
    texts = ["  a  b  ", "  x  y  "]
    batch = norm.normalize_batch(texts)
    singles = [norm.normalize(t) for t in texts]
    assert batch == singles


def test_normalize_batch_large(Norm):
    norm = Norm(collapse_whitespace=True)
    texts = [f"  word{i}  stuff  " for i in range(200)]
    results = norm.normalize_batch(texts)
    assert len(results) == 200
    assert all(not r.startswith(" ") for r in results)


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def test_normalize_is_idempotent(Norm):
    norm = Norm(unicode_form="NFC", collapse_whitespace=True)
    text = "  Hello   world\n\n\ncafé  "
    once = norm.normalize(text)
    twice = norm.normalize(once)
    assert once == twice
