"""Persistence settings."""
from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings


class AwsResource(str, Enum):
    """AwsResource Enum."""

    DYNAMODB = "dynamodb"
    S3 = "s3"


class DynamoDbTable(str, Enum):
    """DynamoDbTable Enum."""

    RadioPrograms = "radio_programs"


class PersistenceSettings(BaseSettings):
    """DynamoDbSettings class."""

    AWS_ENDPOINT_URL: str = None
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str


@lru_cache(maxsize=1)
def get_settings() -> PersistenceSettings:
    """Get PersistenceSettings."""
    return PersistenceSettings()
