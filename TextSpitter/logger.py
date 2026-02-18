"""
Logging setup for TextSpitter.

Uses loguru if available (install textspitter[logging]), otherwise falls back
to the standard library logging module.
"""

try:
    from loguru import logger  # type: ignore[import]
except ImportError:
    import logging

    logger = logging.getLogger("textspitter")  # type: ignore[assignment]
