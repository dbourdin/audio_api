"""API Settings."""

from functools import lru_cache
from ipaddress import IPv4Address
from typing import Any

from pydantic import PositiveInt

from audio_api.logging.settings import LoggingSettings
from audio_api.settings import EnvironmentEnum, EnvironmentSettings
from audio_api.version import __version__


class ApiSettings(EnvironmentSettings, LoggingSettings):
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
            "log_level": self.LOG_LEVEL.lower(),  # Uvicorn expects lowercase strings
            "reload": self.ENVIRONMENT == EnvironmentEnum.development,
        }


@lru_cache(maxsize=1)
def get_settings() -> ApiSettings:
    """Get the API Settings."""
    return ApiSettings()
