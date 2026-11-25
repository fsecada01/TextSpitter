"""
Shared pytest fixtures for TextSpitter tests.
"""

import logging
from typing import Any, cast

import pytest

from TextSpitter.logger import logger


@pytest.fixture
def log_capture():
    """
    Capture log messages from TextSpitter regardless of whether loguru or the
    stdlib logging fallback is active.

    Yields a list that is populated with each log message string as the test
    runs. The handler is removed automatically after the test.

    Usage::

        def test_something(log_capture):
            do_thing()
            assert "expected message" in "\\n".join(log_capture)
    """
    messages: list[str] = []

    if hasattr(logger, "add"):
        # loguru is installed
        def _sink(message):
            messages.append(message.record["message"])

        # ``hasattr`` narrows ``logger`` to an object with an ``add`` member
        # of type ``object``; cast so the loguru API stays callable for ty.
        loguru_logger = cast("Any", logger)
        handler_id = loguru_logger.add(
            _sink, level="DEBUG", format="{message}"
        )
        yield messages
        loguru_logger.remove(handler_id)
    else:
        # stdlib logging fallback
        class _ListHandler(logging.Handler):
            def emit(self, record):
                messages.append(record.getMessage())

        handler = _ListHandler(level=logging.DEBUG)
        logger.addHandler(handler)
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        yield messages
        logger.removeHandler(handler)
        logger.setLevel(old_level)
