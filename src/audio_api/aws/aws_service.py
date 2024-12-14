"""AwsService interface to obtain a boto3 Client or boto3 Resource."""
from dataclasses import dataclass
from enum import Enum

import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient

from audio_api.aws.settings import get_settings

settings = get_settings()


class AwsServices(str, Enum):
    """AwsServices Enum."""

    dynamodb = "dynamodb"
    s3 = "s3"


@dataclass
class AwsService:
    """AwsService class used to get a client or resource."""

    service_name: AwsServices

    def get_client(self) -> BaseClient:
        """Return a boto3 Client for a specified service_name."""
        return boto3.client(
            service_name=self.service_name,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )

    def get_resource(self) -> ServiceResource:
        """Return a boto3 Resource for a specified service_name."""
        return boto3.resource(
            service_name=self.service_name,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )
