"""RadioProgram DynamoDB Models."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from audio_api.schemas.s3_base_schema import S3BaseSchema


class RadioProgramFileModel(S3BaseSchema):
    """RadioProgramFileModel class."""

    program_length: int | None


class BaseRadioProgramModel(BaseModel):
    """BaseRadioProgramModel schema class."""

    title: str | None = Field(example="Shopping 2.0 #1")
    description: str | None = Field(example="Pilot program")
    air_date: date | None
    radio_program: RadioProgramFileModel | None


class RadioProgramModel(BaseRadioProgramModel):
    """RadioProgramModel class."""

    id: UUID | None
