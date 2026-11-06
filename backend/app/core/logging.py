import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level: str = "INFO") -> None:
    """Configure CineBook application logging."""

    logger = logging.getLogger("cinebook")
    logger.setLevel(level.upper())

    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        logging.Formatter(
            fmt=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
    )

    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger within the CineBook namespace."""

    return logging.getLogger(f"cinebook.{name}")
