
import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging."""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
    )

    logger = logging.getLogger("cinebook")
    logger.setLevel(level.upper())

    # Avoid duplicate handlers when configuring repeatedly.
    for existing_handler in logger.handlers[:]:
        logger.removeHandler(existing_handler)
        existing_handler.close()

    logger.addHandler(handler)

    # Prevent records from also propagating to the root logger.
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a named CineBook logger."""
    return logging.getLogger(f"cinebook.{name}")
