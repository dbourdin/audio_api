"""RadioProgram DynamoDB Models."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from audio_api.aws.s3.models import RadioProgramFile


class RadioProgramFileModel(RadioProgramFile):
    """RadioProgramFileModel class."""

    program_length: int | None


class BaseRadioProgramSchema(BaseModel):
    """BaseRadioProgramSchema class."""

    title: str = Field(example="Shopping 2.0 #001")
    description: str | None = Field(example="Pilot program")
    air_date: date | None = Field(example=date(2018, 8, 11))
    spotify_playlist: str | None = Field(
        example=("https://open.spotify.com/playlist/2xDwNVlBPYOVeqzsQjxVCe")
    )


class BaseRadioProgramModel(BaseRadioProgramSchema):
    """BaseRadioProgramModel class."""

    radio_program: RadioProgramFileModel


class RadioProgramModel(BaseRadioProgramModel):
    """RadioProgramModel class."""

    # TODO: This shouldn't be None
    id: UUID | None
