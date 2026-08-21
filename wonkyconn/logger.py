"""General logger for the wonkyconn package."""

from __future__ import annotations

import logging

from rich.logging import RichHandler


def _setup_logger(log_level: str = "INFO") -> logging.Logger:
    """Create and configure the package-wide logger with rich output."""
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    return logging.getLogger("wonkyconn")


logger = _setup_logger()
