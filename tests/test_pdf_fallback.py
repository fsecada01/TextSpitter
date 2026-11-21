"""
Regression tests for the pypdf fallback path in ``FileExtractor.pdf_file_read``.

The primary extractor is PyMuPDF. When it is unavailable or raises, the code
falls back to ``pypdf.PdfReader``. These tests force that path by setting the
module-level ``core.pymupdf`` to ``None`` and pin the behaviour the code
defines: text is returned for a valid PDF, and any failure (encrypted, corrupt,
truncated) degrades to an empty string rather than raising.
"""

from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

from TextSpitter import core
from TextSpitter.core import FileExtractor

SAMPLE_TEXT = "Hello fallback world"


def _build_pdf(
    encrypt_with: str | None = None, pages: tuple[str, ...] = (SAMPLE_TEXT,)
) -> bytes:
    """Build a PDF with one page per entry of ``pages``, using public pypdf
    APIs only. Encryption (AES) additionally needs ``cryptography``."""
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    for text in pages:
        page = writer.add_blank_page(width=300, height=200)
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
        )
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 18 Tf 20 100 Td ({text}) Tj ET".encode())
        page.replace_contents(stream)
    if encrypt_with is not None:
        writer.encrypt(encrypt_with)
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


@pytest.fixture
def force_pypdf(monkeypatch):
    """Make the PyMuPDF branch fail so the pypdf fallback is exercised."""
    monkeypatch.setattr(core, "pymupdf", None)
    assert core.pypdf is not None


def _extract(data: bytes) -> str:
    return FileExtractor(
        file_obj=BytesIO(data), filename="sample.pdf"
    ).pdf_file_read()


def test_fixture_pdf_is_valid():
    """Guard: the generated PDF really contains the sample text."""
    text = PdfReader(BytesIO(_build_pdf())).pages[0].extract_text()
    assert SAMPLE_TEXT in text


def test_fallback_valid_pdf_returns_text(force_pypdf):
    assert SAMPLE_TEXT in _extract(_build_pdf())


def test_fallback_encrypted_pdf_returns_empty_without_raising(force_pypdf):
    """An encrypted PDF cannot be read without a password: empty string."""
    data = _build_pdf(encrypt_with="s3cret")
    assert _extract(data) == ""


def test_fallback_corrupt_pdf_returns_empty_without_raising(force_pypdf):
    assert _extract(b"this is definitely not a pdf") == ""


def test_fallback_pdf_missing_eof_tail_is_recovered(force_pypdf):
    """pypdf 7.x tolerates a file cut inside the trailing ``%%EOF`` marker."""
    data = _build_pdf()
    assert SAMPLE_TEXT in _extract(data[:-1])
    assert SAMPLE_TEXT in _extract(data[:-5])


def test_fallback_truncated_pdf_returns_empty(force_pypdf):
    """Truncation that loses the xref/trailer is unrecoverable for pypdf
    (``Stream has ended unexpectedly``): the code degrades to ""."""
    data = _build_pdf()
    assert _extract(data[:-6]) == ""
    assert _extract(data[: len(data) // 2]) == ""


def test_fallback_logs_when_both_extractors_fail(force_pypdf, log_capture):
    _extract(b"%PDF-1.4\ngarbage")
    assert any("failed" in m.lower() for m in log_capture)


# --- Primary path: PyMuPDF active, pypdf fallback must stay unused ---------


class _PdfReaderSpy:
    """Stand-in for the ``pypdf`` module that records fallback usage."""

    def __init__(self):
        self.calls = 0

    def PdfReader(self, *args, **kwargs):  # noqa: N802 - mirrors pypdf API
        self.calls += 1
        raise AssertionError("pypdf fallback must not be used")


@pytest.fixture
def primary_only(monkeypatch):
    """Keep the real PyMuPDF and trap any use of the pypdf fallback."""
    assert core.pymupdf is not None
    spy = _PdfReaderSpy()
    monkeypatch.setattr(core, "pypdf", spy)
    return spy


def test_primary_valid_pdf_uses_pymupdf(primary_only):
    assert SAMPLE_TEXT in _extract(_build_pdf())
    assert primary_only.calls == 0


def test_primary_multi_page_pdf_extracts_every_page_in_order(primary_only):
    pages = ("First page text", "Second page text", "Third page text")
    result = _extract(_build_pdf(pages=pages))
    positions = [result.index(p) for p in pages]
    assert positions == sorted(positions)
    assert primary_only.calls == 0


def test_primary_recovers_truncated_pdf_without_fallback(primary_only):
    """PyMuPDF repairs a file that lost its xref table and trailer, a case
    where pypdf alone returns ""."""
    data = _build_pdf()
    truncated = data[: data.index(b"xref")]
    assert SAMPLE_TEXT in _extract(truncated)
    assert primary_only.calls == 0


def test_primary_corrupt_pdf_falls_back_then_returns_empty(
    monkeypatch, log_capture
):
    """Garbage: PyMuPDF raises, the pypdf fallback is entered and also fails,
    leaving ""."""
    spy = _PdfReaderSpy()
    monkeypatch.setattr(core, "pypdf", spy)
    assert _extract(b"this is definitely not a pdf") == ""
    assert spy.calls == 1
    assert any("PyMuPDF failed" in m for m in log_capture)


def test_primary_failure_falls_back_to_pypdf_for_valid_pdf(monkeypatch):
    """If PyMuPDF raises on an otherwise valid PDF, pypdf supplies the text."""

    def boom(*args, **kwargs):
        raise RuntimeError("simulated PyMuPDF failure")

    monkeypatch.setattr(core.pymupdf, "open", boom)
    assert SAMPLE_TEXT in _extract(_build_pdf())
