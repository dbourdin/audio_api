"""Base interfaces for getting AWS client or resource."""
import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient

from audio_api.aws.settings import AwsService, get_settings

settings = get_settings()


def get_aws_client(service_name: AwsService) -> BaseClient:
    """Return a boto3 Client for a specified service_name."""
    return boto3.client(
        service_name=service_name,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )


def get_aws_resource(service_name) -> ServiceResource:
    """Return a boto3 Resource for a specified service_name."""
    return boto3.resource(
        service_name=service_name,
        endpoint_url=settings.AWS_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )
