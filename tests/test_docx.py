from io import BytesIO

import pytest
from docx import Document
from pytest_lazy_fixtures import lf

from TextSpitter.core import FileExtractor
from TextSpitter.main import WordLoader


@pytest.fixture
def sample_docx():
    doc = Document()
    doc.add_paragraph("This is a sample DOCX file.")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

@pytest.mark.parametrize("file_input", [
    lf("sample_docx"),
])
def test_file_extractor_docx(file_input):
    extractor = FileExtractor(file_obj=file_input, filename="sample.docx")
    assert "This is a sample DOCX file." in extractor.docx_file_read()

@pytest.mark.parametrize("file_input", [
    lf("sample_docx"),
])
def test_word_loader_docx(file_input):
    loader = WordLoader(file_obj=file_input, filename="sample.docx")
    assert "This is a sample DOCX file." in loader.file_load()
