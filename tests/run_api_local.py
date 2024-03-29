"""Runs the API locally in reload mode using testcontainers."""
from pprint import pformat

import uvicorn

from audio_api.api.settings import get_settings
from audio_api.logger.logger import get_logger
from tests.aws.testcontainers.localstack import localstack_container

logger = get_logger("api_runner")
settings = get_settings()


def start_reload():
    """Start the API with Uvicorn in reload mode."""
    with localstack_container:
        uvicorn_settings = settings.get_uvicorn_settings()
        logger.info(
            f"Starting uvicorn with these settings: \n{pformat(uvicorn_settings)}"
        )
        uvicorn.run(**uvicorn_settings)


if __name__ == "__main__":
    start_reload()
