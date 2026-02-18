"""
TextSpitter — a text-extraction library that facilitates string consumption.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("textspitter")
except PackageNotFoundError:
    __version__ = "unknown"

from .main import WordLoader


def TextSpitter(
    file_obj=None, filename: str | None = None, file_attr: str = "name"
):
    """
    Extract text from a file and return it as a string.

    Args:
        file_obj: A file path (str/Path), file-like object, bytes, or None.
        filename: Filename with extension. Used when file_obj has no name
                  attribute, or as the sole argument for path-based loading.
        file_attr: Attribute name to read from file_obj for its filename.
                   Defaults to "name".

    Returns:
        str: Extracted text content.
    """
    return WordLoader(
        file_obj=file_obj, filename=filename, file_attr=file_attr
    ).file_load()
