"""RadioProgram DynamoDB Models."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from audio_api.aws.s3.models import RadioProgramFile


class RadioProgramFileModel(RadioProgramFile):
    """RadioProgramFileModel class."""

    program_length: int | None


class BaseRadioProgramModel(BaseModel):
    """BaseRadioProgramModel class."""

    title: str = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot program")
    air_date: date | None
    spotify_playlist: str | None = Field(
        example=(
            "https://open.spotify.com/playlist/"
            "37i9dQZF1DWSDoVybeQisg?si=e15a3a65324a4628"
        )
    )
    radio_program: RadioProgramFileModel


class RadioProgramModel(BaseRadioProgramModel):
    """RadioProgramModel class."""

    # TODO: This shouldn't be None
    id: UUID | None
