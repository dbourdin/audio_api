"""API initialization and setup file."""

from fastapi import FastAPI

from audio_api.api.routers import router
from audio_api.api.schemas import ApiVersionModel
from audio_api.api.settings import ApiSettings, get_settings
from audio_api.settings import EnvironmentEnum

settings = get_settings()

app = FastAPI(
    title="Audio API",
    description="Audio API built with FastAPI, PostgreSQL and S3 integration",
    version=settings.API_VERSION,
    debug=settings.ENVIRONMENT == EnvironmentEnum.development,
    root_path=settings.ROOT_PATH,
)
app.include_router(router)


@app.get("/version", tags=["version"], response_model=ApiVersionModel)
def get_api_version():
    """Get ApiVersionModel with the current API version."""
    return ApiVersionModel(
        title=app.title, description=app.description, version=app.version
    )


if settings.ENVIRONMENT != EnvironmentEnum.production:

    @app.get("/settings", tags=["settings"], response_model=ApiSettings)
    def get_api_settings():
        """Get API Settings."""
        return settings
