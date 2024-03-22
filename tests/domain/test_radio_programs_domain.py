"""Test TestRadioProgramsDomain."""

import unittest
from unittest import mock

import pytest

from audio_api.api.schemas import RadioProgramCreateInSchema
from audio_api.aws.dynamodb.exceptions import DynamoDbClientError
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.s3.repositories.radio_program_files import (
    RadioProgramFilesRepository,
)
from audio_api.domain.radio_programs import RadioPrograms
from tests.api.test_utils import UploadFileModel

RADIO_PROGRAMS_REPOSITORY_PATH = (
    "audio_api.domain.radio_programs.RadioPrograms.radio_programs_repository"
)
RADIO_PROGRAMS_REPOSITORY_PUT_ITEM_MOCK_PATCH = (
    f"{RADIO_PROGRAMS_REPOSITORY_PATH}.put_item"
)


@pytest.mark.usefixtures("localstack")
@pytest.mark.usefixtures("radio_programs")
@pytest.mark.usefixtures("radio_programs_repository")
@pytest.mark.usefixtures("radio_program_files_repository")
@pytest.mark.usefixtures("create_program_model")
@pytest.mark.usefixtures("upload_file")
class TestRadioProgramsDomain(unittest.TestCase):
    """TestRadioProgramsDomain class."""

    radio_programs: RadioPrograms
    radio_programs_repository: RadioProgramsRepository
    radio_program_files_repository: RadioProgramFilesRepository
    create_program_model: RadioProgramPutItemModel
    upload_file: UploadFileModel

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
        """Should raise DynamoDbClientError if fails to store file in S3."""
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
