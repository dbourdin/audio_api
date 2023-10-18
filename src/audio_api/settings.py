"""API Settings."""

from enum import Enum
from functools import lru_cache
from ipaddress import IPv4Address
from typing import Any

from pydantic import BaseSettings, PositiveInt

from audio_api.version import __version__


class EnvironmentEnum(str, Enum):
    """API Environment Enum."""

    production = "production"
    development = "development"


class LoggingEnum(str, Enum):
    """Logging configuration Enum."""

    critical = "CRITICAL"
    error = "ERROR"
    warning = "WARNING"
    info = "INFO"
    debug = "DEBUG"


class EnvironmentSettings(BaseSettings):
    """Environment settings class.

    Includes current running environment.
    """

    ENVIRONMENT: EnvironmentEnum = EnvironmentEnum.production
    LOGLEVEL: LoggingEnum = LoggingEnum.info


class APISettings(EnvironmentSettings):
    """Basic API settings.

    Includes environment, CORS and logging, among others.
    """

    # API version
    API_VERSION: str = __version__

    # Settings related to running an ASGI app
    APP_MODULE: str = "audio_api.app:app"
    HOST: IPv4Address = "0.0.0.0"
    PORT: PositiveInt = 3000

    # To use the API behind a proxy, set this variable to the desired base route
    # This will make the /docs URL work properly
    # More info here: https://fastapi.tiangolo.com/advanced/behind-a-proxy/
    ROOT_PATH: str = ""

    def get_uvicorn_settings(self) -> dict[str, Any]:
        """Get a dictionary with settings ready to be used by Uvicorn."""
        return {
            "app": self.APP_MODULE,
            "host": str(self.HOST),
            "port": self.PORT,
            "log_level": self.LOGLEVEL.lower(),  # Uvicorn expects lowercase strings
            "reload": self.ENVIRONMENT == EnvironmentEnum.development,
        }


class Settings(APISettings):
    """API settings.

    Includes configuration tied specifically to this API.
    """


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the API Settings."""
    return Settings()
