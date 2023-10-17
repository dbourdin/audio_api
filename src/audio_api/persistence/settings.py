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

    ENDPOINT_URL: str = None


@lru_cache(maxsize=1)
def get_settings() -> PersistenceSettings:
    """Get PersistenceSettings."""
    return PersistenceSettings()
