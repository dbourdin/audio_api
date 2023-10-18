"""RadioProgram Schemas."""

from datetime import date
from uuid import UUID

from pydantic import Field

from audio_api.schemas import APISchema
from audio_api.schemas.s3_base_schema import S3BaseSchema


class RadioProgramFileSchema(S3BaseSchema):
    """RadioProgramFileSchema class."""

    program_length: int | None


class BaseRadioProgramSchema(APISchema):
    """Base RadioProgram API Model."""


class BaseRadioProgram(BaseRadioProgramSchema):
    """BaseRadioProgram schema class."""

    title: str | None = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot program")
    air_date: date | None
    radio_program: RadioProgramFileSchema | None


class RadioProgram(BaseRadioProgram):
    """RadioProgram schema class."""

    id: UUID | None


class RadioProgramCreateIn(BaseRadioProgramSchema):
    """Parameters received in a POST request."""

    title: str = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot program")
    air_date: date | None
    spotify_playlist: str | None = Field(
        example=(
            "https://open.spotify.com/playlist/"
            "37i9dQZF1DWSDoVybeQisg?si=e15a3a65324a4628"
        )
    )


class RadioProgramCreateDB(BaseRadioProgram):
    """Model used to create a new record in a POST request."""


class RadioProgramCreateOut(RadioProgram):
    """Parameters returned in a POST request."""


class RadioProgramGet(RadioProgramCreateOut):
    """Parameters returned in a GET request."""


class RadioProgramList(RadioProgramCreateOut):
    """Parameters returned in a GET LIST request."""


class RadioProgramUpdateIn(RadioProgramCreateIn):
    """Parameters received in a PUT request."""

    title: str | None = Field(example="Shopping 2.0 #1")


class RadioProgramUpdateDB(RadioProgramCreateDB):
    """Model used to update a record in a PUT request."""


class RadioProgramUpdateOut(RadioProgramCreateOut):
    """Parameters returned in a PUT request."""
