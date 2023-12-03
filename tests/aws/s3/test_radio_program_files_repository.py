"""Test RadioProgramFilesRepository."""
from pathlib import Path
from unittest import mock

import pytest
import requests
from botocore.exceptions import ClientError

from audio_api.aws.s3.exceptions import S3ClientError, S3PersistenceError
from audio_api.aws.s3.models import S3CreateModel
from audio_api.aws.s3.repositories import radio_program_files_repository
from tests.api.test_utils import UploadFileModel, create_upload_file
from tests.aws.testcontainers.localstack import localstack_container

TEST_AUDIO_FILE = Path(__file__).resolve().parent.joinpath("test_audio_file.mp3")
S3_CLIENT_MOCK_PATCH = (
    "audio_api.aws.s3.repositories.radio_program_files"
    ".radio_program_files_repository.s3_client"
)


@pytest.fixture(scope="class")
def upload_file() -> UploadFileModel:
    """Return an UploadFileModel instance."""
    return create_upload_file(TEST_AUDIO_FILE)


class TestRadioProgramFilesRepository:
    """TestRadioProgramFilesRepository class."""

    _localstack_container = localstack_container
    _radio_program_files_repository = radio_program_files_repository

    @pytest.fixture(scope="class", autouse=True)
    def localstack_container(self):
        """Start and stop localstack container."""
        with self._localstack_container:
            yield self._localstack_container

    def test_upload_file_to_s3(self, upload_file: UploadFileModel):
        """Test that we can upload a file successfully to S3."""
        # Given
        radio_program_create_model = S3CreateModel(**upload_file.dict())

        # When
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        downloaded_file_response = requests.get(uploaded_file.file_url)

        # Then
        assert (
            downloaded_file_response.content == upload_file.file_content
        ), "file content is different"
        assert radio_program_create_model.file_name in uploaded_file.file_name
        assert radio_program_create_model.file_name in uploaded_file.file_url

    @mock.patch(S3_CLIENT_MOCK_PATCH)
    def test_upload_file_to_s3_raises_s3_client_error(
        self, upload_file: UploadFileModel, s3_client_mock: mock.patch
    ):
        """Test S3ClientError is raised if put_object raises ClientError."""
        # Given
        radio_program_create_model = S3CreateModel(**upload_file.dict())

        # When
        s3_client_mock.put_object.side_effect = ClientError(
            error_response={"Error": {"status": 500}},
            operation_name="test error.",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.put_object(radio_program_create_model)

    @mock.patch(S3_CLIENT_MOCK_PATCH)
    def test_upload_file_to_s3_raises_s3_persistence_error(
        self, upload_file: UploadFileModel, s3_client_mock: mock.patch
    ):
        """Test S3PersistenceError is raised if put_object returns an error code."""
        # Given
        radio_program_create_model = S3CreateModel(**upload_file.dict())

        # When
        s3_client_mock.put_object.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 500},
        }

        # Then
        with pytest.raises(S3PersistenceError):
            self._radio_program_files_repository.put_object(radio_program_create_model)
