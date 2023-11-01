"""BaseS3Repository class to write and read files from S3."""
from datetime import datetime
from typing import Generic, TypeVar

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from audio_api.aws.s3.buckets import S3_BUCKETS
from audio_api.aws.s3.exceptions import (
    S3BucketNotImplementedError,
    S3ClientError,
    S3PersistenceError,
)
from audio_api.aws.s3.models import S3CreateModel, S3FileModel
from audio_api.aws.settings import AwsResources, S3Buckets, get_settings
from audio_api.settings import EnvironmentEnum

settings = get_settings()


ModelType = TypeVar("ModelType", bound=S3FileModel)
CreateModelType = TypeVar("CreateModelType", bound=S3CreateModel)


class BaseS3Repository(Generic[ModelType, CreateModelType]):
    """BaseS3Repository class."""

    def __init__(self, model: type[ModelType]):
        """Repository with default methods to Store, Read, and Delete files from S3.

        Args:
            model: A pydantic BaseModel class.
        """
        self.model = model
        self.bucket = self._get_s3_bucket()
        self.s3_client = self.get_s3_client()

    def _get_s3_bucket(self) -> S3Buckets:
        """Get S3 bucket from S3_BUCKETS."""
        bucket = S3_BUCKETS.get(self.model)
        if not bucket:
            raise S3BucketNotImplementedError
        return bucket

    @classmethod
    def get_s3_client(cls) -> BaseClient:
        """Return an S3 client for the current AWS S3 configuration.

        Returns:
            BaseClient: Boto3 client set up for S3.
        """
        return boto3.client(
            AwsResources.S3,
            endpoint_url=settings.AWS_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )

    def _build_object_url(self, object_key: str) -> str:
        """Return the uploaded file URL.

        Args:
            object_key: File name.

        Returns:
            str: Uploaded file URL.
        """
        if settings.ENVIRONMENT == EnvironmentEnum.development:
            return f"{settings.AWS_ENDPOINT_URL}/{self.bucket}/{object_key}"
        return f"https://{self.bucket}.s3.amazonaws.com/{object_key}"

    def store(self, item: CreateModelType) -> type[ModelType]:
        """Upload an object to the S3 bucket.

        Args:
            item: Item to be stored in S3 bucket.

        Raises:
            S3ClientError: If failed to get response from S3.
            S3PersistenceError: If failed to store object in S3.

        Returns:
            ModelType: Object containing file_name and file_url.
        """
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        # TODO: Make filename url friendly.
        item.file_name = f"{timestamp}_{item.file_name}.mp3"
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket, Key=item.file_name, Body=item.file
            )
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 200:
            raise S3PersistenceError(
                f"Unsuccessful S3 put_object response. Status: {status}"
            )

        return self.model(
            file_name=item.file_name, file_url=self._build_object_url(item.file_name)
        )

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
            response = self.s3_client.get_object(Bucket=self.bucket, Key=object_key)
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 200:
            raise S3PersistenceError(
                f"Unsuccessful S3 get_object response. Status - {status}"
            )

        return response.get("Body")

    def list_all(self) -> list[type[ModelType]]:
        """Get a list with all items created in S3 Bucket.

        Raises:
            S3ClientError: If failed to receive response from S3

        Returns:
            list[type[ModelType]]: List containing all files in S3 bucket.
        """
        try:
            files = self.s3_client.list_objects_v2(Bucket=self.bucket)
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")
        return [
            self.model(
                file_name=obj["Key"], file_url=self._build_object_url(obj["Key"])
            )
            for obj in files.get("Contents", [])
        ]

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
            response = self.s3_client.delete_object(Bucket=self.bucket, Key=object_key)
        except ClientError as e:
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 204:
            raise S3PersistenceError(
                f"Object deletion was not successful. Status - {status}"
            )

    def delete_file_by_url(self, url: str):
        """Delete a file in S3 by url.

        Args:
            url: URL to the file to be deleted.
        """
        file_name = url.split("/")[-1]
        self.delete_object(object_key=file_name)
