"""Environment Settings."""

from enum import Enum

from pydantic import BaseSettings

from audio_api.version import __version__


class EnvironmentEnum(str, Enum):
    """API Environment Enum."""

    production = "production"
    development = "development"


class EnvironmentSettings(BaseSettings):
    """Environment settings class.

    Includes current running environment.
    """

    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.production
    API_VERSION: str = __version__
