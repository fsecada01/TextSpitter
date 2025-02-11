"""
Doc string
"""

import os

__version__ = os.environ.get("VERSION", "0.3.7rc4")

from .main import WordLoader

name = "TextSpitter"


def TextSpitter(
    file_obj=None, filename: str | None = None, file_attr: str = "name"
):
    """
    The main function that returns text contents from `WordLoader`
    Args:
        file_obj:
        filename: str | None
        file_attr: str

    Returns:

    """
    return WordLoader(
        file_obj=file_obj, filename=filename, file_attr=file_attr
    ).file_load()
