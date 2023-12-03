"""Test RadioProgramFilesRepository."""
import unittest
from pathlib import Path
from unittest import mock

import pytest
import requests
from botocore.exceptions import ClientError

from audio_api.aws.s3.exceptions import (
    S3ClientError,
    S3FileNotFoundError,
    S3PersistenceError,
)
from audio_api.aws.s3.models import S3CreateModel
from audio_api.aws.s3.repositories import radio_program_files_repository
from tests.api.test_utils import UploadFileModel, create_upload_file
from tests.aws.testcontainers.localstack import LocalStackContainerTest

TEST_AUDIO_FILE = Path(__file__).resolve().parent.joinpath("test_audio_file.mp3")
S3_CLIENT_PATH = (
    "audio_api.aws.s3.repositories.radio_program_files"
    ".radio_program_files_repository.s3_client"
)
S3_GET_OBJECT_MOCK_PATCH = f"{S3_CLIENT_PATH}.get_object"
S3_PUT_OBJECT_MOCK_PATCH = f"{S3_CLIENT_PATH}.put_object"


@pytest.fixture(scope="class")
def upload_file(request):
    """Return an UploadFileModel instance."""
    upload_file = create_upload_file(TEST_AUDIO_FILE)
    request.cls.upload_file = upload_file
    return upload_file


@pytest.mark.usefixtures("upload_file")
class TestRadioProgramFilesRepository(unittest.TestCase, LocalStackContainerTest):
    """TestRadioProgramFilesRepository class."""

    _radio_program_files_repository = radio_program_files_repository
    upload_file: UploadFileModel

    def test_upload_file_to_s3(self):
        """Test that we can upload a file successfully to S3."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())

        # When
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        downloaded_file_response = requests.get(uploaded_file.file_url)

        # Then
        assert (
            downloaded_file_response.content == self.upload_file.file_content
        ), "file content is different"
        assert radio_program_create_model.file_name in uploaded_file.file_name
        assert radio_program_create_model.file_name in uploaded_file.file_url

    @mock.patch(S3_PUT_OBJECT_MOCK_PATCH)
    def test_upload_file_to_s3_raises_s3_client_error(
        self, put_object_mock: mock.patch
    ):
        """Test S3ClientError is raised if put_object raises ClientError."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())

        # When
        put_object_mock.side_effect = ClientError(
            error_response={"Error": {"status": 500}},
            operation_name="test error.",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.put_object(radio_program_create_model)

    @mock.patch(S3_PUT_OBJECT_MOCK_PATCH)
    def test_upload_file_to_s3_raises_s3_persistence_error(
        self, put_object_mock: mock.patch
    ):
        """Test S3PersistenceError is raised if put_object returns an error code."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())

        # When
        put_object_mock.return_value = {"ResponseMetadata": {"HTTPStatusCode": 500}}

        # Then
        with pytest.raises(S3PersistenceError):
            self._radio_program_files_repository.put_object(radio_program_create_model)

    def test_get_file_from_s3(self):
        """Test that we can retrieve a file successfully from S3."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())

        # When
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        uploaded_object = self._radio_program_files_repository.get_object(
            uploaded_file.file_name
        )

        # Then
        assert uploaded_object.read() == self.upload_file.file_content

    @mock.patch(S3_GET_OBJECT_MOCK_PATCH)
    def test_get_file_from_s3_raises_s3_client_error(self, get_object_mock: mock.patch):
        """Test S3ClientError is raised if get_object raises ClientError."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )

        # When
        get_object_mock.side_effect = ClientError(
            error_response={"Error": {"status": 500}},
            operation_name="test error.",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.get_object(uploaded_file.file_name)

    @mock.patch(S3_GET_OBJECT_MOCK_PATCH)
    def test_get_file_from_s3_raises_s3_persistence_error(
        self, get_object_mock: mock.patch
    ):
        """Test S3PersistenceError is raised if get_object returns an error code."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )

        # When
        get_object_mock.return_value = {"ResponseMetadata": {"HTTPStatusCode": 500}}

        # Then
        with pytest.raises(S3PersistenceError):
            self._radio_program_files_repository.get_object(uploaded_file.file_name)

    def test_get_non_existent_file_from_s3_raises_s3_persistence_error(self):
        """Test S3ClientError is raised if object does not exist."""
        # Then
        with pytest.raises(S3FileNotFoundError):
            self._radio_program_files_repository.get_object("non_existent_file")
