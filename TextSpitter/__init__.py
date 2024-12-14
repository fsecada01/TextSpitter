"""
Doc string
"""

import os

__version__ = os.environ.get("VERSION", "0.3.7b2")

from .main import WordLoader

name = "TextSpitter"


def TextSpitter(file_obj=None, filename: str or None = None):
    """
    The main function that returns text contents from `WordLoader`
    Args:
        file_obj:
        filename:

    Returns:

    """
    return WordLoader(file_obj=file_obj, filename=filename).file_load()
