"""S3Connector class to write and read files from S3."""

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from audio_api.settings import EnvironmentEnum, get_settings

settings = get_settings()


def get_s3_client() -> BaseClient:
    """Return an s3 client for the current AWS S3 configuration.

    Returns:
        BaseClient: Boto3 client set up for S3.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )


class S3PersistenceError(Exception):
    """S3PersistenceError class."""


class S3ClientError(Exception):
    """S3ClientError class."""


class S3Connector:
    """Base S3Connector class."""

    def __init__(self, bucket_name):
        """Create a new S3Connector for a specific bucket.

        Args:
            bucket_name (str): S3 bucket name to be used by the S3Connector.
        """
        self.s3_client = get_s3_client()
        self.bucket_name = bucket_name

    def store(self, object_key: str, object_data: bytes) -> str:
        """
        Upload an object to the S3 bucket.

        Args:
            object_key (str): The key (path) of the object in the S3 bucket.
            object_data (bytes): The data to be stored in the object.

        Raises:
            S3ClientError: If failed to get response from S3.
            S3PersistenceError: If failed to persist requested object.

        Returns:
            str: String containing the url of the uploaded object.
        """
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name, Key=object_key, Body=object_data
            )
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 200:
            raise S3PersistenceError(
                f"Unsuccessful S3 put_object response. Status: {status}"
            )

        if settings.ENVIRONMENT == EnvironmentEnum.development:
            return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{object_key}"
        return f"https://{self.bucket_name}.s3.amazonaws.com/{object_key}"

    def read_object(self, object_key: str) -> StreamingBody:
        """Read an object from the S3 bucket.

        Args:
            object_key (str): The key (path) of the object in the S3 bucket.

        Raises:
            S3ClientError: If failed to get response from S3.
            S3PersistenceError: If failed to retrieve object from S3.

        Returns:
            StreamingBody: The content of the file.
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=object_key
            )
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 200:
            raise S3PersistenceError(
                f"Unsuccessful S3 get_object response. Status - {status}"
            )

        return response.get("Body")

    def delete_object(self, object_key: str):
        """Delete an object from the S3 bucket.

        Args:
            object_key (str): The key (path) of the object in the S3 bucket.

        Raises:
            S3ClientError: If failed to get response from S3.
            S3PersistenceError: If failed to retrieve object from S3.
        """
        # Attempt to delete the object
        try:
            response = self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=object_key
            )
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 204:
            raise S3PersistenceError(
                f"Object deletion was not successful. Status - {status}"
            )
