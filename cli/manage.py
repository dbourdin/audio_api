#!/usr/local/bin/python

"""Main API CLI file."""

from pprint import pformat

import typer
import uvicorn

from audio_api.api.settings import get_settings

app = typer.Typer()
settings = get_settings()


@app.command()
def start_reload():
    """Start the API with Uvicorn in reload mode."""
    uvicorn_settings = settings.get_uvicorn_settings()
    print(f"Starting uvicorn with these settings: \n{pformat(uvicorn_settings)}")
    uvicorn.run(**uvicorn_settings)


@app.command()
def start():
    """Start the API with Uvicorn."""
    uvicorn_settings = settings.get_uvicorn_settings()
    uvicorn_settings["reload"] = False
    print(f"Starting uvicorn with these settings: \n{pformat(uvicorn_settings)}")
    uvicorn.run(**uvicorn_settings)


if __name__ == "__main__":
    app()
