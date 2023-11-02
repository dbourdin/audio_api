"""Logger setup."""

import logging

from audio_api.logger.formatter import DefaultFormatter
from audio_api.logger.settings import get_settings

settings = get_settings()

formatter = DefaultFormatter(
    fmt=settings.LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.basicConfig(
    level=settings.LOG_LEVEL.value,
    handlers=[logging.StreamHandler()],
)
logging.root.handlers[0].setFormatter(formatter)


def get_logger(logger_name: str) -> logging.Logger:
    """Return a new logging.Logger with specified settings.

    Args:
        logger_name: Logger name.

    Returns:
        logging.Logger: The logger instance.
    """
    logger = logging.getLogger(name=logger_name)
    return logger
