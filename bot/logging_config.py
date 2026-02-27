"""
Logging setup for the trading bot.
Handles file + console logging.
"""

import logging
import logging.handlers
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "trading_bot.log"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging for the application.

    - Writes full logs to a rotating file
    - Shows warnings and errors in the console
    """

    # Make sure log directory exists
    LOG_DIR.mkdir(exist_ok=True)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # File handler (stores everything)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB per file
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler (keep it clean)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger("trading_bot")
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Prevent duplicate logs from propagating upward
    root_logger.propagate = False

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under trading_bot namespace."""
    return logging.getLogger(f"trading_bot.{name}")