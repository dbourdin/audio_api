"""RadioPrograms Schemas."""
from datetime import date

from fastapi import Form

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

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str | None = Form(default=None),
        air_date: date | None = Form(default=None),
        spotify_playlist: str | None = Form(default=None),
    ) -> "RadioProgramCreateInSchema":
        """Convert parameters to a form."""
        return cls(
            title=title,
            description=description,
            air_date=air_date,
            spotify_playlist=spotify_playlist,
        )


class RadioProgramCreateOutSchema(RadioProgramApiSchema):
    """Parameters returned in a POST request."""


class RadioProgramUpdateInSchema(BaseRadioProgramApiSchema):
    """Parameters returned in a PUT request."""

    title: str | None = None

    @classmethod
    def as_form(
        cls,
        title: str | None = Form(default=None),
        description: str | None = Form(default=None),
        air_date: date | None = Form(default=None),
        spotify_playlist: str | None = Form(default=None),
    ) -> "RadioProgramCreateInSchema":
        """Convert parameters to a form."""
        return cls(
            title=title,
            description=description,
            air_date=air_date,
            spotify_playlist=spotify_playlist,
        )


class RadioProgramUpdateOutSchema(RadioProgramApiSchema):
    """Parameters returned in a PUT request."""
