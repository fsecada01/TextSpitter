from io import BytesIO

import pytest
from pypdf import PdfWriter
from pytest_lazy_fixtures import lf

from TextSpitter.core import FileExtractor
from TextSpitter.main import WordLoader


@pytest.fixture
def sample_pdf():
    """
    Test PDF file
    """
    buffer = BytesIO()
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=72, height=72)
    pdf_writer.write(buffer)
    buffer.seek(0)
    return buffer

@pytest.mark.parametrize("file_input", [
    lf("sample_pdf"),
])
def test_file_extractor_pdf(file_input):
    extractor = FileExtractor(file_obj=file_input, filename="sample.pdf")
    assert extractor.pdf_file_read() is not None

@pytest.mark.parametrize("file_input", [
    lf("sample_pdf"),
])
def test_word_loader_pdf(file_input):
    loader = WordLoader(file_obj=file_input, filename="sample.pdf")
    assert loader.file_load() is not None
