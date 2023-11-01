"""RadioProgram DynamoDB Models."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from audio_api.aws.s3.schemas import RadioProgramFile


class RadioProgramFileModel(RadioProgramFile):
    """RadioProgramFileModel class."""

    program_length: int | None


class BaseRadioProgramModel(BaseModel):
    """BaseRadioProgramModel schema class."""

    title: str = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot program")
    air_date: date | None
    radio_program: RadioProgramFileModel | None


class RadioProgramModel(BaseRadioProgramModel):
    """RadioProgramModel class."""

    # TODO: This shouldn't be None
    id: UUID | None
