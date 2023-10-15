"""RadioProgram Schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from audio_api.schemas import APISchema


class BaseRadioProgramSchema(APISchema):
    """Base RadioProgram API Model."""


class BaseDbRadioProgramSchema(BaseRadioProgramSchema):
    """Base RadioProgramSchema with DB created values."""

    program_id: UUID
    created_at: datetime
    updated_at: datetime


class RadioProgramCreateIn(BaseRadioProgramSchema):
    """Parameters received in a POST request."""

    title: str = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot program")
    air_date: date | None
    length: int | None = Field(example=3600)
    spotify_playlist: str | None = Field(
        example=(
            "https://open.spotify.com/playlist/"
            "37i9dQZF1DWSDoVybeQisg?si=e15a3a65324a4628"
        )
    )


class RadioProgramCreateDB(RadioProgramCreateIn):
    """Model used to create a new record in a POST request."""

    url: str | None


class RadioProgramCreateOut(BaseDbRadioProgramSchema, RadioProgramCreateDB):
    """Parameters returned in a POST request."""


class RadioProgramGet(RadioProgramCreateOut):
    """Parameters returned in a GET request."""


class RadioProgramList(RadioProgramCreateOut):
    """Parameters returned in a GET LIST request."""


class RadioProgramUpdateIn(RadioProgramCreateIn):
    """Parameters received in a PUT request."""


class RadioProgramUpdateDB(RadioProgramCreateDB):
    """Model used to update a record in a PUT request."""


class RadioProgramUpdateOut(RadioProgramCreateOut):
    """Parameters returned in a PUT request."""
