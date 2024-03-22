"""Test TestRadioProgramsDomain."""

import unittest

import pytest

from audio_api.api.schemas import RadioProgramCreateInSchema
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.s3.repositories.radio_program_files import (
    RadioProgramFilesRepository,
)
from audio_api.domain.radio_programs import RadioPrograms
from tests.api.test_utils import UploadFileModel


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
