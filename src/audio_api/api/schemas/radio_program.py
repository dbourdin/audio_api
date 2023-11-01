"""RadioPrograms Schemas."""
from pydantic import Field

from audio_api.api.schemas import APISchema
from audio_api.domain.models import RadioProgramModel
from audio_api.domain.models.radio_program import BaseRadioProgramSchema


class BaseRadioProgramApiSchema(APISchema, BaseRadioProgramSchema):
    """BaseRadioProgramApiSchema class."""


class RadioProgramApiSchema(APISchema, RadioProgramModel):
    """RadioProgramApiSchema class."""


class RadioProgramGetSchema(RadioProgramApiSchema):
    """Parameters returned in a GET request."""


class RadioProgramListSchema(RadioProgramApiSchema):
    """Parameters returned in a GET LIST request."""


class RadioProgramCreateInSchema(BaseRadioProgramApiSchema):
    """Parameters returned in a POST request."""


class RadioProgramCreateOutSchema(RadioProgramApiSchema):
    """Parameters returned in a POST request."""


class RadioProgramUpdateInSchema(BaseRadioProgramApiSchema):
    """Parameters returned in a PUT request."""

    title: str | None = Field(example="Shopping 2.0 #1")


class RadioProgramUpdateOutSchema(RadioProgramApiSchema):
    """Parameters returned in a PUT request."""
