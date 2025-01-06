"""RadioProgram DynamoDB Models."""
from datetime import date
from uuid import UUID

from pydantic import BaseModel

from audio_api.aws.s3.models import RadioProgramFile


class RadioProgramFileModel(RadioProgramFile):
    """RadioProgramFileModel class."""

    program_length: int | None = None


class BaseRadioProgramSchema(BaseModel):
    """BaseRadioProgramSchema class."""

    title: str
    description: str | None = None
    air_date: date | None = None
    spotify_playlist: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Shopping 2.0 #001",
                    "description": "Pilot program",
                    "air_date": date(2018, 8, 11),
                    "spotify_playlist": (
                        "https://open.spotify.com/playlist/2xDwNVlBPYOVeqzsQjxVCe"
                    ),
                }
            ]
        }
    }


class BaseRadioProgramModel(BaseRadioProgramSchema):
    """BaseRadioProgramModel class."""

    radio_program: RadioProgramFileModel


class RadioProgramModel(BaseRadioProgramModel):
    """RadioProgramModel class."""

    # TODO: This shouldn't be None
    id: UUID | None = None
