"""RadioProgram Schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from audio_api.schemas import APISchema


class BaseRadioProgramSchema(APISchema):
    """Base RadioProgram API Model."""

    title: str = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot episode")
    air_date: date | None
    length: int | None = Field(example=3600)
    spotify_playlist: str | None = Field(
        example=(
            "https://open.spotify.com/playlist/"
            "37i9dQZF1DWSDoVybeQisg?si=e15a3a65324a4628"
        )
    )
    url: str | None


class RadioProgramSchema(BaseRadioProgramSchema):
    """RadioProgramSchema with all RadioProgram parameters."""

    program_id: UUID
    created_at: datetime
    updated_at: datetime


class RadioProgramCreateIn(BaseRadioProgramSchema):
    """Parameters received in a POST request."""


class RadioProgramCreateDB(RadioProgramCreateIn):
    """Model used to create a new record in a POST request."""


class RadioProgramCreateOut(RadioProgramSchema):
    """Parameters returned in a POST request."""


class RadioProgramGet(RadioProgramSchema):
    """Parameters returned in a GET request."""


class RadioProgramList(RadioProgramSchema):
    """Parameters returned in a GET LIST request."""


class RadioProgramUpdateIn(BaseRadioProgramSchema):
    """Parameters received in a PUT request."""


class RadioProgramUpdateDB(RadioProgramUpdateIn):
    """Model used to update a record in a PUT request."""


class RadioProgramUpdateOut(RadioProgramCreateOut):
    """Parameters returned in a PUT request."""
