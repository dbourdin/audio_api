"""Integration Tests for Radio Programs."""
import unittest

import pytest
from starlette import status
from starlette.testclient import TestClient

from audio_api.api.schemas import (
    RadioProgramCreateInSchema,
    RadioProgramCreateOutSchema,
    RadioProgramGetSchema,
    RadioProgramListSchema,
    RadioProgramUpdateInSchema,
)
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.s3.repositories.radio_program_files import (
    RadioProgramFilesRepository,
)
from audio_api.domain.radio_programs import RadioPrograms
from tests.api.test_utils import UploadFileModel, create_temp_file, radio_program


@pytest.mark.usefixtures("localstack")
@pytest.mark.usefixtures("test_client")
@pytest.mark.usefixtures("radio_programs")
@pytest.mark.usefixtures("radio_programs_repository")
@pytest.mark.usefixtures("radio_program_files_repository")
@pytest.mark.usefixtures("create_program_model")
@pytest.mark.usefixtures("upload_file")
@pytest.mark.usefixtures("new_upload_file")
class TestRadioPrograms(unittest.TestCase):
    """TestRadioPrograms class."""

    client: TestClient
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

    def test_get_program(self):
        """Get a program by id."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        get_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )
        expected = RadioProgramGetSchema.from_orm(get_program)

        # When
        response = self.client.get(f"/programs/{expected.id}")
        received = RadioProgramGetSchema.parse_obj(response.json())

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected

    def test_get_invalid_program_raises_404(self):
        """Get a program with invalid id raises 404."""
        # Given
        get_program = radio_program("test program get not found")

        # When
        response = self.client.get(f"/programs/{get_program.id}")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text

    def test_get_all_programs_returns_empty_list(self):
        """List programs returns an empty list if no program exists."""
        # When
        response = self.client.get("/programs")

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == []

    def test_get_all_programs_returns_existing_programs(self):
        """List programs returns all existing programs."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        new_radio_program_file = self.new_upload_file
        program_1 = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )
        program_2 = self.radio_programs.create(
            radio_program=radio_program_in, program_file=new_radio_program_file.file
        )
        expected = sorted(
            [
                RadioProgramListSchema.from_orm(program_1),
                RadioProgramListSchema.from_orm(program_2),
            ],
            key=lambda x: x.id,
        )

        # When
        response = self.client.get("/programs")
        received = sorted(
            [RadioProgramListSchema.parse_obj(program) for program in response.json()],
            key=lambda x: x.id,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected

    def test_create_a_program(self):
        """Create a new Radio Program."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )

        # When
        response = self.client.post(
            "/programs", data=radio_program_in.dict(), files=create_temp_file()
        )
        received = RadioProgramCreateOutSchema.parse_raw(response.text)

        # Then
        assert response.status_code == status.HTTP_201_CREATED, response.text
        assert received.title == radio_program_in.title

    def test_update_a_program(self):
        """Update an existing Radio Program."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        created_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )
        update_program = RadioProgramUpdateInSchema(title="Updated_title")

        # When
        response = self.client.put(
            f"/programs/{created_radio_program.id}",
            data=update_program.dict(),
            files=create_temp_file(),
        )
        received = RadioProgramCreateOutSchema.parse_raw(response.text)

        # Then
        assert update_program.title == received.title
        assert update_program.title in received.radio_program.file_name

    def test_update_non_existing_program_raises_404(self):
        """Update a non existing Radio Program raises 404."""
        # Given
        put_program = radio_program("test program put not found")

        # When
        response = self.client.put(
            f"/programs/{put_program.id}", data=put_program.dict()
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_radio_program(self):
        """Delete an existing Radio Program."""
        # Given
        radio_program_in = RadioProgramCreateInSchema(
            **self.create_program_model.dict()
        )
        radio_program_file = self.upload_file
        created_radio_program = self.radio_programs.create(
            radio_program=radio_program_in, program_file=radio_program_file.file
        )

        # When
        response = self.client.delete(f"/programs/{created_radio_program.id}")

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_non_existing_radio_program_raises_404(self):
        """Delete a non existing Radio Program raises 404."""
        # Given
        delete_program = radio_program("test program delete not found")

        # When
        response = self.client.delete(f"/programs/{delete_program.id}")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
