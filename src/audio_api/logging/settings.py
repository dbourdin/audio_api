"""Logging settings."""

from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings


class LoggingEnum(str, Enum):
    """Logging configuration Enum."""

    critical = "CRITICAL"
    error = "ERROR"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"


class LoggingSettings(BaseSettings):
    """Logging settings class.

    Includes current logging configuration.
    """

    LOG_LEVEL: LoggingEnum = LoggingEnum.info
    LOG_FORMAT: str = "%(levelprefix)s %(asctime)s | %(message)s"


@lru_cache(maxsize=1)
def get_settings() -> LoggingSettings:
    """Get the API Settings."""
    return LoggingSettings()
