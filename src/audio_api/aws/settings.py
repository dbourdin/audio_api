"""Persistence settings."""
from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings

from audio_api.settings import EnvironmentSettings


class AwsService(str, Enum):
    """AwsService Enum."""

    dynamodb = "dynamodb"
    s3 = "s3"


class DynamoDbTables(str, Enum):
    """DynamoDbTable Enum."""

    radio_programs = "radio_programs"


class S3Bucket(str, Enum):
    """S3Buckets Enum."""

    radio_programs = "radio-programs"


class AwsSettings(EnvironmentSettings, BaseSettings):
    """AwsSettings class."""

    AWS_ENDPOINT_URL: str = None
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    RADIO_PROGRAMS_BUCKET: str


@lru_cache(maxsize=1)
def get_settings() -> AwsSettings:
    """Get Aws Settings."""
    return AwsSettings()
