"""Logger setup."""

import logging

from audio_api.logger.settings import get_settings

settings = get_settings()
logging.basicConfig(format=settings.LOG_FORMAT, level=settings.LOG_LEVEL)


def get_logger(logger_name: str) -> logging.Logger:
    """Return a new logging.Logger with specified settings.

    Args:
        logger_name: Logger name.

    Returns:
        logging.Logger: The logger instance.
    """
    logger = logging.getLogger(name=logger_name)
    return logger
