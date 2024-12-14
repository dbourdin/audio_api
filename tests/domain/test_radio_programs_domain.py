"""Test RadioPrograms domain."""

import unittest
from unittest import mock

import pytest

from audio_api.api.schemas import RadioProgramCreateInSchema, RadioProgramUpdateInSchema
from audio_api.aws.dynamodb.exceptions import (
    DynamoDbClientError,
    DynamoDbItemNotFoundError,
)
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.s3.exceptions import (
    S3ClientError,
    S3FileNotFoundError,
    S3PersistenceError,
)
from audio_api.aws.s3.repositories.radio_program_files import (
    RadioProgramFilesRepository,
)
from audio_api.domain.radio_programs import RadioPrograms
from tests.api.test_utils import UploadFileModel

RADIO_PROGRAMS_PATH = "audio_api.domain.radio_programs.RadioPrograms"
RADIO_PROGRAMS_REPOSITORY_PATH = f"{RADIO_PROGRAMS_PATH}.radio_programs_repository"
RADIO_PROGRAMS_REPOSITORY_PUT_ITEM_MOCK_PATCH = (
    f"{RADIO_PROGRAMS_REPOSITORY_PATH}.put_item"
)
RADIO_PROGRAMS_REPOSITORY_UPDATE_ITEM_MOCK_PATCH = (
    f"{RADIO_PROGRAMS_REPOSITORY_PATH}.update_item"
)
RADIO_PROGRAM_FILES_REPOSITORY_PATH = (
    f"{RADIO_PROGRAMS_PATH}.radio_program_files_repository"
)
RADIO_PROGRAM_FILES_REPOSITORY_DELETE_S3_OBJECT_MOCK_PATCH = (
    f"{RADIO_PROGRAM_FILES_REPOSITORY_PATH}.delete_object"
)


@pytest.mark.usefixtures("localstack")
@pytest.mark.usefixtures("radio_programs")
@pytest.mark.usefixtures("radio_programs_repository")
@pytest.mark.usefixtures("radio_program_files_repository")
@pytest.mark.usefixtures("create_program_model")
@pytest.mark.usefixtures("upload_file")
@pytest.mark.usefixtures("new_upload_file")
class TestRadioProgramsDomain(unittest.TestCase):
    """TestRadioProgramsDomain class."""

    radio_programs: RadioPrograms
    radio_programs_repository: RadioProgramsRepository
    radio_program_files_repository: RadioProgramFilesRepository
    create_program_model: RadioProgramPutItemModel
    upload_file: UploadFileModel
    new_upload_file: UploadFileModel

    @pytest.fixture(autouse=True)
    def _empty_bucket(self):
        self.radio_program_files_repository.delete_all()

    @pytest.fixture(autouse=True)
    def _clear_db(self):
        self.radio_programs_repository.delete_all()

    def test_create_radio_program(self):
        """Should create a new RadioProgram."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file

        # When
        db_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )
        uploaded_object = self.radio_program_files_repository.get_object(
            db_radio_program.radio_program.file_name
        )

        # Then
        assert db_radio_program.title == radio_program_in.title
        assert db_radio_program.description == radio_program_in.description
        assert db_radio_program.air_date == radio_program_in.air_date
        assert db_radio_program.spotify_playlist == radio_program_in.spotify_playlist
        assert uploaded_object.read() == radio_program_file.file_content

    @mock.patch(RADIO_PROGRAMS_REPOSITORY_PUT_ITEM_MOCK_PATCH)
    def test_create_radio_program_raises_dynamo_db_client_error(
        self, put_item_mock: mock.patch
    ):
        """Should raise DynamoDbClientError if fails to store object in DynamoDB."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file

        # When
        put_item_mock.side_effect = DynamoDbClientError("Test error")

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs.create(
                radio_program=radio_program_in, program_file=radio_program_file.file
            )

    def test_get_radio_program(self):
        """Should retrieve an existing RadioProgram."""
        # Given
        created_radio_program = self.radio_programs_repository.put_item(
            self.create_program_model
        )

        # When
        db_radio_program = self.radio_programs.get(program_id=created_radio_program.id)

        # Then
        assert db_radio_program == created_radio_program

    def test_get_all_radio_programs(self):
        """Should retrieve all existing RadioPrograms."""
        # Given
        radio_program_1 = self.create_program_model.copy()
        radio_program_2 = self.create_program_model.copy()
        radio_program_2.title = "test program 2"
        radio_program_2.description = "test program 2"
        created_radio_program_1 = self.radio_programs_repository.put_item(
            radio_program_1
        )
        created_radio_program_2 = self.radio_programs_repository.put_item(
            radio_program_2
        )

        # When
        db_radio_programs = self.radio_programs.get_all()

        # Then
        assert created_radio_program_1 in db_radio_programs
        assert created_radio_program_2 in db_radio_programs

    def test_update_existing_radio_program(self):
        """Should update an existing RadioProgram."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        created_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )
        update_program = RadioProgramUpdateInSchema(title="Updated title")

        # When
        updated_program = self.radio_programs.update(
            program_id=created_radio_program.id, new_program=update_program
        )

        # Then
        assert updated_program.title == update_program.title
        assert updated_program.title != created_radio_program.title

    def test_update_existing_radio_program_file(self):
        """Should update an existing RadioProgram with a new radio_program_file."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        new_radio_program_file = self.new_upload_file
        created_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )
        update_program = RadioProgramUpdateInSchema(title="Updated_title")

        # When
        updated_program = self.radio_programs.update(
            program_id=created_radio_program.id,
            new_program=update_program,
            program_file=new_radio_program_file.file,
        )
        uploaded_object = self.radio_program_files_repository.get_object(
            updated_program.radio_program.file_name
        )

        # Then
        assert update_program.title in updated_program.radio_program.file_name
        assert uploaded_object.read() == new_radio_program_file.file_content
        with pytest.raises(S3FileNotFoundError):
            self.radio_program_files_repository.get_object(
                created_radio_program.radio_program.file_name
            )

    @mock.patch(RADIO_PROGRAMS_REPOSITORY_UPDATE_ITEM_MOCK_PATCH)
    def test_update_radio_program_raises_dynamo_db_client_error(
        self, update_item_mock: mock.patch
    ):
        """Should raise DynamoDbClientError if fails to store object in DynamoDB."""
        # Given
        created_radio_program = self.radio_programs_repository.put_item(
            self.create_program_model
        )
        update_program = RadioProgramUpdateInSchema(title="Updated title")

        # When
        update_item_mock.side_effect = DynamoDbClientError("Test error")

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs.update(
                program_id=created_radio_program.id, new_program=update_program
            )

    @mock.patch(RADIO_PROGRAMS_REPOSITORY_UPDATE_ITEM_MOCK_PATCH)
    def test_failed_update_radio_program_with_program_file_deletes_file(
        self, update_item_mock: mock.patch
    ):
        """Should raise DynamoDbClientError if fails to store object in DynamoDB."""
        # Given
        created_radio_program = self.radio_programs_repository.put_item(
            self.create_program_model
        )
        new_file = self.upload_file
        update_program = RadioProgramUpdateInSchema(title="Updated title")

        # When
        update_item_mock.side_effect = DynamoDbClientError("Test error")

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs.update(
                program_id=created_radio_program.id,
                new_program=update_program,
                program_file=new_file.file,
            )

        assert self.radio_program_files_repository.list_objects() == []

    def test_delete_radio_program(self):
        """Should delete an existing radio program."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        db_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )

        # When
        self.radio_programs.delete(program_id=db_radio_program.id)

        # Then
        with pytest.raises(DynamoDbItemNotFoundError):
            self.radio_programs.get(program_id=db_radio_program.id)
        with pytest.raises(S3FileNotFoundError):
            self.radio_program_files_repository.get_object(
                object_key=db_radio_program.radio_program.file_name
            )

    @mock.patch(RADIO_PROGRAM_FILES_REPOSITORY_DELETE_S3_OBJECT_MOCK_PATCH)
    def test_delete_radio_program_with_s3_client_error_removes_from_dynamo(
        self, delete_s3_object_mock: mock.patch
    ):
        """Should delete an existing radio program even if fails to delete from S3."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        db_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )

        # When
        delete_s3_object_mock.side_effect = S3ClientError("Test error")
        self.radio_programs.delete(program_id=db_radio_program.id)

        # Then
        with pytest.raises(DynamoDbItemNotFoundError):
            self.radio_programs.get(program_id=db_radio_program.id)
        uploaded_object = self.radio_program_files_repository.get_object(
            object_key=db_radio_program.radio_program.file_name
        )
        assert uploaded_object.read() == radio_program_file.file_content

    @mock.patch(RADIO_PROGRAM_FILES_REPOSITORY_DELETE_S3_OBJECT_MOCK_PATCH)
    def test_delete_radio_program_with_s3_persistence_error_removes_from_dynamo(
        self, delete_s3_object_mock: mock.patch
    ):
        """Should delete an existing radio program even if fails to delete from S3."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        db_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )

        # When
        delete_s3_object_mock.side_effect = S3PersistenceError("Test error")
        self.radio_programs.delete(program_id=db_radio_program.id)

        # Then
        with pytest.raises(DynamoDbItemNotFoundError):
            self.radio_programs.get(program_id=db_radio_program.id)
        uploaded_object = self.radio_program_files_repository.get_object(
            object_key=db_radio_program.radio_program.file_name
        )
        assert uploaded_object.read() == radio_program_file.file_content
