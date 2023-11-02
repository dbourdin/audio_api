#!/usr/local/bin/python

"""Main API CLI file."""

from pprint import pformat

import typer
import uvicorn

from audio_api.api.settings import get_settings
from audio_api.logging.logger import get_logger

logger = get_logger("manage_cli")
app = typer.Typer()
settings = get_settings()


@app.command()
def start_reload():
    """Start the API with Uvicorn in reload mode."""
    uvicorn_settings = settings.get_uvicorn_settings()
    logger.info(f"Starting uvicorn with these settings: \n{pformat(uvicorn_settings)}")
    uvicorn.run(**uvicorn_settings)


@app.command()
def start():
    """Start the API with Uvicorn."""
    uvicorn_settings = settings.get_uvicorn_settings()
    uvicorn_settings["reload"] = False
    logger.info(f"Starting uvicorn with these settings: \n{pformat(uvicorn_settings)}")
    uvicorn.run(**uvicorn_settings)


if __name__ == "__main__":
    app()
