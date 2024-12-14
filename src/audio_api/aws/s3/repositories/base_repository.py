"""BaseS3Repository class to write and read files from S3."""
from datetime import datetime
from typing import Generic, TypeVar

from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from audio_api.aws.aws_service import AwsService, AwsServices
from audio_api.aws.s3.buckets import S3_BUCKETS
from audio_api.aws.s3.exceptions import (
    S3BucketNotImplementedError,
    S3ClientError,
    S3FileNotFoundError,
    S3PersistenceError,
)
from audio_api.aws.s3.models import S3CreateModel, S3FileModel
from audio_api.aws.settings import S3Bucket, get_settings
from audio_api.logger.logger import get_logger
from audio_api.settings import EnvironmentEnum

logger = get_logger("s3_repository")
settings = get_settings()


ModelType = TypeVar("ModelType", bound=S3FileModel)
CreateModelType = TypeVar("CreateModelType", bound=S3CreateModel)


class BaseS3Repository(Generic[ModelType, CreateModelType]):
    """BaseS3Repository class."""

    service: AwsService = AwsService(AwsServices.s3)

    def __init__(self, model: type[ModelType]):
        """Repository with default methods to Store, Read, and Delete files from S3.

        Args:
            model: A pydantic BaseModel class.
        """
        self.model = model
        self.bucket_name = self._get_s3_bucket_name()
        self.s3_client = self.service.get_client()
        self.s3_bucket = self.service.get_resource().Bucket(self.bucket_name)

    def _get_s3_bucket_name(self) -> S3Bucket:
        """Get S3 bucket from S3_BUCKETS."""
        bucket = S3_BUCKETS.get(self.model)
        if not bucket:
            raise S3BucketNotImplementedError
        return bucket

    def _build_object_url(self, object_key: str) -> str:
        """Return the uploaded file URL.

        Args:
            object_key: File name.

        Returns:
            str: Uploaded file URL.
        """
        if settings.ENVIRONMENT == EnvironmentEnum.development:
            endpoint_url = settings.AWS_ENDPOINT_URL.replace("localstack", "localhost")
            return f"{endpoint_url}/{self.bucket_name}/{object_key}"
        return f"https://{self.bucket_name}.s3.amazonaws.com/{object_key}"

    def put_object(self, item: CreateModelType) -> type[ModelType]:
        """Put an object to the S3 bucket.

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
                Bucket=self.bucket_name, Key=item.file_name, Body=item.file
            )
        except ClientError as e:
            logger.error(
                f"Failed to put_object {item.file_name} in {self.bucket_name} bucket."
            )
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 200:
            logger.error(
                f"Failed to put_object {item.file_name} in {self.bucket_name} bucket."
            )
            raise S3PersistenceError(
                f"Unsuccessful S3 put_object response. Status: {status}"
            )

        logger.info(
            f"Successfully put_object {item.file_name} in {self.bucket_name} bucket."
        )
        return self.model(
            file_name=item.file_name, file_url=self._build_object_url(item.file_name)
        )

    def get_object(self, object_key: str) -> StreamingBody:
        """Get an object from the S3 bucket.

        Args:
            object_key (str): The key (path) of the object in the S3 bucket.

        Raises:
            S3FileNotFoundError: If file does not exist in S3 bucket.
            S3ClientError: If failed to get response from S3.
            S3PersistenceError: If failed to retrieve object from S3.

        Returns:
            StreamingBody: The content of the file.
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=object_key
            )
        except self.s3_client.exceptions.NoSuchKey as e:
            logger.error(f"File {object_key} not found in {self.bucket_name} bucket.")
            raise S3FileNotFoundError(
                f"File {object_key} not found in {self.bucket_name} bucket: {e}"
            )
        except ClientError as e:
            logger.error(
                f"Failed to get_object {object_key} from {self.bucket_name} bucket."
            )
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 200:
            logger.error(
                f"Failed to get_object {object_key} from {self.bucket_name} bucket."
            )
            raise S3PersistenceError(
                f"Unsuccessful S3 get_object response. Status - {status}"
            )

        return response.get("Body")

    def list_objects(self) -> list[type[ModelType]]:
        """Get a list with all objects created in S3 Bucket.

        Raises:
            S3ClientError: If failed to receive response from S3

        Returns:
            list[type[ModelType]]: List containing all files in S3 bucket.
        """
        try:
            files = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        except ClientError as e:
            logger.error(f"Failed to list_objects_v2 from {self.bucket_name} bucket.")
            raise S3ClientError(f"Failed to get response from S3: {e}")
        return [
            self.model(
                file_name=obj["Key"], file_url=self._build_object_url(obj["Key"])
            )
            for obj in files.get("Contents", [])
        ]

    def delete_object(self, object_key: str) -> None:
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
            logger.error(
                f"Failed to delete_object {object_key} from {self.bucket_name} bucket."
            )
            raise S3ClientError(f"Failed to get response from S3: {e}")

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status != 204:
            logger.error(
                f"Failed to delete_object {object_key} from {self.bucket_name} bucket."
            )
            raise S3PersistenceError(
                f"Object deletion was not successful. Status - {status}"
            )

        logger.info(
            f"Successfully delete_object {object_key} from {self.bucket_name} bucket."
        )

    def _delete_all(self) -> list:
        """Delete all objects in the S3 bucket.

        Returns:
            list: List containing delete response data.
        """
        return self.s3_bucket.objects.all().delete()

    def delete_all(self) -> list:
        """Delete all objects in the S3 bucket.

        Raises:
            S3ClientError: If failed to delete objects from S3.

        Returns:
            list: List containing delete response data.
        """
        try:
            return self._delete_all()
        except Exception:
            logger.error(
                f"Failed to delete all objects from {self.bucket_name} bucket."
            )
            raise S3ClientError(
                f"Failed to delete all objects from {self.bucket_name} bucket."
            )
