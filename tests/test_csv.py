import csv
from io import BytesIO
from pathlib import Path
from tempfile import SpooledTemporaryFile

import pytest
from pytest_lazy_fixtures import lf

from TextSpitter.core import FileExtractor


@pytest.fixture
def sample_csv():
    """
    Sample CSV data.
    """
    return "name,age\nAlice,30\nBob,25"


@pytest.fixture
def csv_file(tmp_path, sample_csv):
    """
    Generate a CSV file on disk.
    """
    file_path = tmp_path / "sample.csv"
    with file_path.open("w", newline="") as f:
        writer = csv.writer(f)
        for row in sample_csv.splitlines():
            if row:
                writer.writerow(row.split(","))
    return file_path


@pytest.fixture
def csv_bytesio(sample_csv):
    """
    Generate CSV File in memory.
    """
    return BytesIO(sample_csv.encode("utf-8"))

@pytest.mark.parametrize(
    "file_input",
    [
        lf("csv_file"),
        lf("csv_bytesio"),
    ],
)
def test_file_extractor_csv(file_input, sample_csv):
    """
    Test CSV file extraction.
    """
    if any(
        isinstance(file_input, x)
        for x in (SpooledTemporaryFile, BytesIO, bytes)
    ):
        file_name = "sample.csv"
    elif isinstance(file_input, Path):
        file_name = file_input.name
    else:
        file_name = file_input
    extractor = FileExtractor(file_obj=file_input, filename=file_name)
    assert (
        extractor.csv_file_read(newline="").strip().replace("\r", "")
        == sample_csv.strip()
    )
