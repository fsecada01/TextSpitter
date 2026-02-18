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


# FileExtractor accepts all input types (Path, BytesIO, SpooledTemporaryFile)
@pytest.mark.parametrize(
    "file_input",
    [
        lf("txt_file"),
        lf("txt_bytesio"),
        lf("txt_spooled"),
    ],
)
def test_file_extractor_txt(file_input, sample_txt):
    extractor = FileExtractor(file_obj=file_input, filename="sample.txt")
    assert extractor.text_file_read() == sample_txt


# WordLoader only accepts str | Path — stream inputs belong on FileExtractor
def test_word_loader_txt_path(txt_file, sample_txt):
    loader = WordLoader(file_obj=txt_file)
    assert loader.file_load() == sample_txt


def test_word_loader_txt_str(tmp_path, sample_txt):
    file_path = tmp_path / "str_sample.txt"
    file_path.write_text(sample_txt)
    loader = WordLoader(file_obj=str(file_path))
    assert loader.file_load() == sample_txt


def test_word_loader_txt_filename_only(txt_file, sample_txt):
    loader = WordLoader(filename=str(txt_file))
    assert loader.file_load() == sample_txt
