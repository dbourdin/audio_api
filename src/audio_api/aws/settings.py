"""Persistence settings."""
from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings

from audio_api.settings import EnvironmentSettings


class AwsResource(str, Enum):
    """AwsResource Enum."""

    DYNAMODB = "dynamodb"
    S3 = "s3"


class DynamoDbTable(str, Enum):
    """DynamoDbTable Enum."""

    RadioPrograms = "radio_programs"


class AwsSettings(BaseSettings):
    """AwsSettings class."""

    AWS_ENDPOINT_URL: str = None
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    RADIO_PROGRAMS_BUCKET: str


class Settings(EnvironmentSettings, AwsSettings):
    """AWS settings.

    Includes configuration tied specifically to this module.
    """


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get Aws Settings."""
    return Settings()
