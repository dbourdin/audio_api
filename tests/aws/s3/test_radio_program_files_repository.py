"""Test RadioProgramFilesRepository."""
import time
import unittest
from pathlib import Path
from unittest import mock

import pytest
import requests
from botocore.exceptions import ClientError

from audio_api.aws.s3.exceptions import (
    S3BucketNotImplementedError,
    S3ClientError,
    S3FileNotFoundError,
    S3PersistenceError,
)
from audio_api.aws.s3.models import S3CreateModel
from audio_api.aws.s3.repositories import radio_program_files_repository
from audio_api.settings import EnvironmentEnum
from tests.api.test_utils import UploadFileModel, create_upload_file

TEST_AUDIO_FILE = Path(__file__).resolve().parent.joinpath("test_audio_file.mp3")
S3_REPOSITORIES_PATH = "audio_api.aws.s3.repositories"
RADIO_PROGRAM_FILES_REPOSITORY_PATH = (
    f"{S3_REPOSITORIES_PATH}.radio_program_files.radio_program_files_repository"
)

S3_CLIENT_PATH = f"{RADIO_PROGRAM_FILES_REPOSITORY_PATH}.s3_client"
S3_BUCKET_PATH = f"{RADIO_PROGRAM_FILES_REPOSITORY_PATH}.s3_bucket"

REPOSITORY_MODEL_PATH = f"{RADIO_PROGRAM_FILES_REPOSITORY_PATH}.model"
S3_GET_OBJECT_MOCK_PATCH = f"{S3_CLIENT_PATH}.get_object"
S3_PUT_OBJECT_MOCK_PATCH = f"{S3_CLIENT_PATH}.put_object"
S3_LIST_OBJECTS_MOCK_PATCH = f"{S3_CLIENT_PATH}.list_objects_v2"
S3_DELETE_OBJECT_MOCK_PATCH = f"{S3_CLIENT_PATH}.delete_object"
S3_DELETE_ALL_MOCK_PATCH = f"{S3_BUCKET_PATH}.delete_all"
ENVIRONMENT_SETTINGS_PATH = (
    f"{S3_REPOSITORIES_PATH}.base_repository.settings.ENVIRONMENT"
)


@pytest.fixture(scope="class")
def upload_file(request):
    """Return an UploadFileModel instance."""
    upload_file = create_upload_file(TEST_AUDIO_FILE)
    request.cls.upload_file = upload_file
    return upload_file


@pytest.mark.usefixtures("localstack")
@pytest.mark.usefixtures("upload_file")
class TestRadioProgramFilesRepository(unittest.TestCase):
    """TestRadioProgramFilesRepository class."""

    _radio_program_files_repository = radio_program_files_repository
    upload_file: UploadFileModel

    @pytest.fixture(autouse=True)
    def _empty_bucket(self):
        self._radio_program_files_repository.delete_all()

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
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.put_object(radio_program_create_model)
        put_object_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name,
            Key=radio_program_create_model.file_name,
            Body=radio_program_create_model.file,
        )

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
        put_object_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name,
            Key=radio_program_create_model.file_name,
            Body=radio_program_create_model.file,
        )

    def test_get_file_from_s3(self):
        """Test that we can retrieve a file successfully from S3."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())
        expected_content = self.upload_file.file_content

        # When
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        uploaded_object = self._radio_program_files_repository.get_object(
            uploaded_file.file_name
        )

        # Then
        assert uploaded_object.read() == expected_content

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
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.get_object(uploaded_file.file_name)
        get_object_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name,
            Key=uploaded_file.file_name,
        )

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
        get_object_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name,
            Key=uploaded_file.file_name,
        )

    def test_get_non_existent_file_from_s3_raises_s3_persistence_error(self):
        """Test S3ClientError is raised if object does not exist."""
        # Then
        with pytest.raises(S3FileNotFoundError):
            self._radio_program_files_repository.get_object("non_existent_file")

    def test_list_objects_from_s3_returns_empty_list(self):
        """Test that list_objects returns an empty list if no files are found."""
        # Given
        expected_result = []

        # When
        objects_list = self._radio_program_files_repository.list_objects()

        # Then
        assert objects_list == expected_result

    def test_list_objects_from_s3(self):
        """Test that we can retrieve a file successfully from S3."""
        # Given
        uploaded_file_1 = self._radio_program_files_repository.put_object(
            S3CreateModel(**self.upload_file.dict())
        )
        # Wait 3 second to avoid name collision
        time.sleep(3)
        uploaded_file_2 = self._radio_program_files_repository.put_object(
            S3CreateModel(**self.upload_file.dict())
        )
        expected_results = [uploaded_file_1, uploaded_file_2]

        # When
        objects_list = self._radio_program_files_repository.list_objects()

        # Then
        assert objects_list == expected_results

    @mock.patch(S3_LIST_OBJECTS_MOCK_PATCH)
    def test_list_objects_from_s3_raises_s3_client_error(
        self, list_objects_mock: mock.patch
    ):
        """Test S3ClientError is raised if list_objects_v2 raises ClientError."""
        # When
        list_objects_mock.side_effect = ClientError(
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.list_objects()
        list_objects_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name,
        )

    def test_delete_object(self):
        """Test delete_object successfully removes an object from S3 bucket."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        downloaded_file_response = requests.get(uploaded_file.file_url)

        # When
        self._radio_program_files_repository.delete_object(uploaded_file.file_name)
        downloaded_deleted_file_response = requests.get(uploaded_file.file_url)

        # Then
        assert downloaded_file_response.status_code == 200
        assert downloaded_deleted_file_response.status_code == 404
        assert (
            downloaded_file_response.content != downloaded_deleted_file_response.content
        )
        with pytest.raises(S3FileNotFoundError):
            self._radio_program_files_repository.get_object(uploaded_file.file_name)

    @mock.patch(S3_DELETE_OBJECT_MOCK_PATCH)
    def test_delete_object_raises_s3_client_error(
        self, delete_objects_mock: mock.patch
    ):
        """Test delete_object raises S3ClientError if ClientError."""
        # Given
        delete_key = "non_existent_file"

        # When
        delete_objects_mock.side_effect = ClientError(
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.delete_object(delete_key)
        delete_objects_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name, Key=delete_key
        )

    @mock.patch(S3_DELETE_OBJECT_MOCK_PATCH)
    def test_delete_object_raises_s3_persistence_error(
        self, delete_objects_mock: mock.patch
    ):
        """Test S3PersistenceError is raised if delete_object returns an error code."""
        # Given
        delete_key = "non_existent_file"

        # When
        delete_objects_mock.return_value = {"ResponseMetadata": {"HTTPStatusCode": 500}}

        # Then
        with pytest.raises(S3PersistenceError):
            self._radio_program_files_repository.delete_object(delete_key)
        delete_objects_mock.assert_called_once_with(
            Bucket=self._radio_program_files_repository.bucket_name, Key=delete_key
        )

    def test_delete_all(self):
        """Test delete_all removes all objects from S3 bucket."""
        # Given
        radio_program_create_model = S3CreateModel(**self.upload_file.dict())
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        expected_deleted_response = [{"Key": uploaded_file.file_name}]

        # When
        response = self._radio_program_files_repository.delete_all()
        downloaded_deleted_file_response = requests.get(uploaded_file.file_url)

        # Then
        assert response[0].get("Deleted") == expected_deleted_response
        assert downloaded_deleted_file_response.status_code == 404
        with pytest.raises(S3FileNotFoundError):
            self._radio_program_files_repository.get_object(uploaded_file.file_name)

    @mock.patch(S3_DELETE_ALL_MOCK_PATCH)
    def test_delete_all_raises_s3_client_error(self, delete_objects_mock: mock.patch):
        """Test delete_all raises S3ClientError if Exception."""
        # When
        delete_objects_mock.side_effect = Exception("test_error")

        # Then
        with pytest.raises(S3ClientError):
            self._radio_program_files_repository.delete_all()
        delete_objects_mock.assert_called_once()

    @mock.patch(REPOSITORY_MODEL_PATH)
    def test_get_s3_bucket_name_raises_s3_bucket_not_implemented_error(
        self, repository_model_mock: mock.patch
    ):
        """Test _get_s3_bucket_name raises S3BucketNotImplementedError."""
        # When
        repository_model_mock.return_value = "NON-EXISTENT-BUCKET"

        # Then
        with pytest.raises(S3BucketNotImplementedError):
            self._radio_program_files_repository._get_s3_bucket_name()

    @mock.patch(ENVIRONMENT_SETTINGS_PATH)
    def test_build_object_url_returns_correct_production_url(
        self, environment_settings_mock: mock.patch
    ):
        """Test _build_object_url returns correct url if environment is production."""
        # Given
        object_key = "test_key"
        expected_url = (
            f"https://{self._radio_program_files_repository.bucket_name}"
            f".s3.amazonaws.com/{object_key}"
        )

        # When
        environment_settings_mock.return_value = EnvironmentEnum.production
        url = self._radio_program_files_repository._build_object_url(
            object_key=object_key
        )

        # Then
        assert url == expected_url
