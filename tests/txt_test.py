from io import BytesIO
from tempfile import SpooledTemporaryFile

import pytest
from pytest_lazy_fixtures import lf

from TextSpitter.core import FileExtractor
from TextSpitter.main import WordLoader


@pytest.fixture
def sample_txt():
    return "This is a sample text file."

@pytest.fixture
def txt_file(tmp_path, sample_txt):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(sample_txt)
    return file_path

@pytest.fixture
def txt_bytesio(sample_txt):
    return BytesIO(sample_txt.encode("utf-8"))

@pytest.fixture
def txt_spooled(sample_txt):
    spooled_file = SpooledTemporaryFile()
    spooled_file.write(sample_txt.encode("utf-8"))
    spooled_file.seek(0)
    return spooled_file

@pytest.mark.parametrize("file_input", [
    lf("txt_file"),  # File on disk
    lf("txt_bytesio"),  # BytesIO
    lf("txt_spooled"),  # SpooledTemporaryFile
])
def test_file_extractor_txt(file_input, sample_txt):
    extractor = FileExtractor(file_obj=file_input, filename="sample.txt")
    assert extractor.text_file_read() == sample_txt

@pytest.mark.parametrize("file_input", [
    lf("txt_file"),
    lf("txt_bytesio"),
    lf("txt_spooled"),
])
def test_word_loader_txt(file_input, sample_txt):
    loader = WordLoader(file_obj=file_input, filename="sample.txt")
    assert loader.file_load() == sample_txt
