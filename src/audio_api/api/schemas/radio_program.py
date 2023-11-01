"""RadioPrograms Schemas."""

from audio_api.api.schemas import APISchema
from audio_api.domain.models import RadioProgramModel


class BaseRadioProgramApiSchema(APISchema, RadioProgramModel):
    """BaseRadioProgramApiSchema class."""


class RadioProgramGetSchema(BaseRadioProgramApiSchema):
    """Parameters returned in a GET request."""


class RadioProgramListSchema(BaseRadioProgramApiSchema):
    """Parameters returned in a GET LIST request."""
