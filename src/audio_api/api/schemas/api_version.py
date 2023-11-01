"""API Version information."""

from audio_api.api.schemas import APISchema


class ApiVersionModel(APISchema):
    """Data structure to hold the API version information."""

    title: str
    description: str
    version: str
