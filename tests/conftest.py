"""
Shared pytest fixtures for TextSpitter tests.
"""

import logging

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

        handler_id = logger.add(_sink, level="DEBUG", format="{message}")
        yield messages
        logger.remove(handler_id)
    else:
        # stdlib logging fallback
        class _ListHandler(logging.Handler):
            def emit(self, record):
                messages.append(record.getMessage())

        handler = _ListHandler(level=logging.DEBUG)
        logger.addHandler(handler)  # type: ignore[union-attr]
        old_level = logger.level  # type: ignore[union-attr]
        logger.setLevel(logging.DEBUG)  # type: ignore[union-attr]
        yield messages
        logger.removeHandler(handler)  # type: ignore[union-attr]
        logger.setLevel(old_level)  # type: ignore[union-attr]
