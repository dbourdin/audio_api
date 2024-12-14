"""Test /programs endpoints."""
import unittest
from unittest import mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from audio_api.api.schemas import (
    RadioProgramCreateInSchema,
    RadioProgramCreateOutSchema,
    RadioProgramGetSchema,
    RadioProgramListSchema,
    RadioProgramUpdateInSchema,
    RadioProgramUpdateOutSchema,
)
from audio_api.aws.dynamodb.exceptions import (
    DynamoDbClientError,
    DynamoDbItemNotFoundError,
    DynamoDbStatusError,
)
from audio_api.aws.s3.exceptions import S3ClientError, S3PersistenceError
from tests.api.test_utils import create_temp_file, radio_program


@pytest.mark.usefixtures("test_client")
class TestRadioProgramsEndpoints(unittest.TestCase):
    """TestRadioProgramsEndpoints class."""

    client: TestClient

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_get_program(self, radio_programs_mock):
        """Get a program by id."""
        # Given
        get_program = radio_program(title="Test program get")
        radio_programs_mock.get.return_value = get_program
        expected = RadioProgramGetSchema.from_orm(get_program)

        # When
        response = self.client.get(f"/programs/{get_program.id}")
        received = RadioProgramListSchema.parse_obj(response.json())

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected
        radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_get_program_raises_404_if_not_found(self, radio_programs_mock):
        """Get RadioProgram should raise 404 if RadioProgram does not exist."""
        # Given
        get_program = radio_program("test program get not found")
        radio_programs_mock.get.side_effect = DynamoDbItemNotFoundError(
            f"RadioProgram with id {get_program.id} does not exist."
        )

        # When
        response = self.client.get(f"/programs/{get_program.id}")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_get_program_raises_500_if_dynamodb_client_error(self, radio_programs_mock):
        """Get RadioProgram should raise 500 if DynamoDbClientError."""
        # Given
        get_program = radio_program("test program")
        radio_programs_mock.get.side_effect = DynamoDbClientError(
            "Failed to get item from DynamoDB: test error"
        )

        # When
        response = self.client.get(f"/programs/{get_program.id}")

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_get_program_raises_500_if_dynamodb_status_error(self, radio_programs_mock):
        """Get RadioProgram should raise 500 if DynamoDbStatusError."""
        # Given
        get_program = radio_program("test program")
        radio_programs_mock.get.side_effect = DynamoDbStatusError(
            "Failed to get item from DynamoDB: test error"
        )

        # When
        response = self.client.get(f"/programs/{get_program.id}")

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_list_programs(self, radio_programs_mock):
        """Get a list of programs."""
        # Given
        radio_programs = [
            radio_program(title="Test program list #1"),
            radio_program(title="Test program list #2"),
        ]
        radio_programs_mock.get_all.return_value = radio_programs
        expected = [
            RadioProgramListSchema.from_orm(program) for program in radio_programs
        ]

        # When
        response = self.client.get("/programs")
        received = [
            RadioProgramListSchema.parse_obj(program) for program in response.json()
        ]

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected
        radio_programs_mock.get_all.assert_called_once()

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_list_radio_programs_empty(self, radio_programs_mock):
        """Get an empty list of programs if none created."""
        # Given
        radio_programs_mock.get_all.return_value = []

        # When
        response = self.client.get("/programs")

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert response.json() == []
        radio_programs_mock.get_all.assert_called_once()

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_list_programs_raises_500_if_dynamodb_client_error(
        self, radio_programs_mock
    ):
        """Get RadioPrograms list should raise 500 if DynamoDbClientError."""
        # Given
        radio_programs_mock.get_all.side_effect = DynamoDbClientError(
            "Failed to get items from DynamoDB: test error"
        )

        # When
        response = self.client.get("/programs")

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.get_all.assert_called_once()

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_list_programs_raises_500_if_dynamodb_status_error(
        self, radio_programs_mock
    ):
        """Get RadioPrograms list should raise 500 if DynamoDbStatusError."""
        # Given
        radio_programs_mock.get_all.side_effect = DynamoDbStatusError(
            "Failed to get items from DynamoDB: test error"
        )

        # When
        response = self.client.get("/programs")

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.get_all.assert_called_once()

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_create_program(self, radio_programs_mock):
        """Create a RadioProgram via POST."""
        # Given
        created_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
        radio_programs_mock.create.return_value = created_program
        expected = RadioProgramCreateOutSchema.parse_obj(created_program.dict())

        # When
        response = self.client.post(
            "/programs", data=radio_program_in.dict(), files=create_temp_file()
        )
        received = RadioProgramCreateOutSchema.parse_raw(response.text)

        # Then
        assert response.status_code == status.HTTP_201_CREATED, response.text
        assert received == expected
        radio_programs_mock.create.assert_called_once_with(
            radio_program=radio_program_in, program_file=mock.ANY
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_create_program_without_file_raises_error(self, radio_programs_mock):
        """Create a RadioProgram via POST."""
        # Given
        created_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**created_program.dict())

        # When
        response = self.client.post("/programs", data=radio_program_in.dict())

        # Then
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        ), response.text

    def test_create_program_without_radio_program_title_raises_error(self):
        """Cannot create a RadioProgram via POST without required title."""
        # Given
        data_to_send = {
            "description": "program_without_title",
        }

        # When
        response = self.client.post(
            "/programs", data=data_to_send, files=create_temp_file()
        )

        # Then
        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        ), response.text

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_create_program_raises_500_if_s3_client_error(self, radio_programs_mock):
        """Create RadioProgram should raise 500 if S3ClientError."""
        # Given
        created_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
        radio_programs_mock.create.side_effect = S3ClientError(
            "Failed to get response from S3: test error"
        )

        # When
        response = self.client.post(
            "/programs", data=radio_program_in.dict(), files=create_temp_file()
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.create.assert_called_once_with(
            radio_program=radio_program_in, program_file=mock.ANY
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_create_program_raises_500_if_s3_persistence_error(
        self, radio_programs_mock
    ):
        """Create RadioProgram should raise 500 if S3PersistenceError."""
        # Given
        created_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
        radio_programs_mock.create.side_effect = S3PersistenceError(
            "Unsuccessful S3 put_object response. Status: test error"
        )

        # When
        response = self.client.post(
            "/programs", data=radio_program_in.dict(), files=create_temp_file()
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.create.assert_called_once_with(
            radio_program=radio_program_in, program_file=mock.ANY
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_create_program_raises_500_if_dynamodb_client_error(
        self, radio_programs_mock
    ):
        """Create RadioProgram should raise 500 if DynamoDbClientError."""
        # Given
        created_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
        radio_programs_mock.create.side_effect = DynamoDbClientError(
            "Failed to store new item in DynamoDB: test error"
        )

        # When
        response = self.client.post(
            "/programs", data=radio_program_in.dict(), files=create_temp_file()
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.create.assert_called_once_with(
            radio_program=radio_program_in, program_file=mock.ANY
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_create_program_raises_500_if_dynamodb_status_error(
        self, radio_programs_mock
    ):
        """Create RadioProgram should raise 500 if DynamoDbStatusError."""
        # Given
        created_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
        radio_programs_mock.create.side_effect = DynamoDbStatusError(
            "Failed to store new item in DynamoDB: test error"
        )

        # When
        response = self.client.post(
            "/programs", data=radio_program_in.dict(), files=create_temp_file()
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.create.assert_called_once_with(
            radio_program=radio_program_in, program_file=mock.ANY
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program(self, radio_programs_mock):
        """Update RadioProgram via PUT."""
        # Given
        updated_program = radio_program(title="test_program_update")
        radio_programs_mock.update.return_value = updated_program
        data_to_send = RadioProgramUpdateInSchema(**updated_program.dict())
        expected = RadioProgramUpdateOutSchema.parse_obj(updated_program.dict())

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}",
            data=data_to_send.dict(),
            files=create_temp_file(),
        )
        received = RadioProgramUpdateOutSchema.parse_raw(response.text)

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=data_to_send,
            program_file=mock.ANY,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_without_file(self, radio_programs_mock):
        """Update RadioProgram via PUT without file."""
        # Given
        updated_program = radio_program(title="test_program_update")
        radio_programs_mock.update.return_value = updated_program
        data_to_send = RadioProgramUpdateInSchema(**updated_program.dict())
        expected = RadioProgramUpdateOutSchema.parse_obj(updated_program.dict())

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}", data=data_to_send.dict()
        )
        received = RadioProgramUpdateOutSchema.parse_raw(response.text)

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=data_to_send,
            program_file=None,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_file(self, radio_programs_mock):
        """Update RadioProgram file via PUT."""
        # Given
        updated_program = radio_program(title="test_program_update")
        radio_programs_mock.update.return_value = updated_program
        expected = RadioProgramUpdateOutSchema.parse_obj(updated_program.dict())

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}", files=create_temp_file()
        )
        received = RadioProgramUpdateOutSchema.parse_raw(response.text)

        # Then
        assert response.status_code == status.HTTP_200_OK, response.text
        assert received == expected
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=RadioProgramUpdateInSchema(),
            program_file=mock.ANY,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_raises_404_if_not_found(self, radio_programs_mock):
        """Update RadioProgram raises 404 if program is not found."""
        # Given
        updated_program = radio_program(title="test_program_update")
        data_to_send = RadioProgramUpdateInSchema(**updated_program.dict())
        radio_programs_mock.update.side_effect = DynamoDbItemNotFoundError(
            f"RadioProgram with id {updated_program.id} does not exist."
        )

        response = self.client.put(
            f"/programs/{updated_program.id}", data=data_to_send.dict()
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=data_to_send,
            program_file=None,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_raises_500_if_s3_client_error(self, radio_programs_mock):
        """Update RadioProgram should raise 500 if S3ClientError."""
        # Given
        updated_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
        radio_programs_mock.update.side_effect = S3ClientError(
            "Failed to get response from S3: test error"
        )

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}",
            data=radio_program_in.dict(),
            files=create_temp_file(),
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=radio_program_in,
            program_file=mock.ANY,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_raises_500_if_s3_persistence_error(
        self, radio_programs_mock
    ):
        """Update RadioProgram should raise 500 if S3PersistenceError."""
        # Given
        updated_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
        radio_programs_mock.update.side_effect = S3PersistenceError(
            "Unsuccessful S3 put_object response. Status: test error"
        )

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}",
            data=radio_program_in.dict(),
            files=create_temp_file(),
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=radio_program_in,
            program_file=mock.ANY,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_raises_500_if_dynamodb_client_error(
        self, radio_programs_mock
    ):
        """Update RadioProgram should raise 500 if DynamoDbClientError."""
        # Given
        updated_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
        radio_programs_mock.update.side_effect = DynamoDbClientError(
            "Failed to store new item in DynamoDB: test error"
        )

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}", data=radio_program_in.dict()
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=radio_program_in,
            program_file=None,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_update_program_raises_500_if_dynamodb_status_error(
        self, radio_programs_mock
    ):
        """Update RadioProgram should raise 500 if DynamoDbStatusError."""
        # Given
        updated_program = radio_program(title="Test program post")
        radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
        radio_programs_mock.update.side_effect = DynamoDbStatusError(
            "Failed to store new item in DynamoDB: test error"
        )

        # When
        response = self.client.put(
            f"/programs/{updated_program.id}", data=radio_program_in.dict()
        )

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.update.assert_called_once_with(
            program_id=updated_program.id,
            new_program=radio_program_in,
            program_file=None,
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_delete_program(self, radio_programs_mock):
        """Delete a RadioProgram."""
        # Given
        updated_program = radio_program(title="Test program post")
        radio_programs_mock.delete.return_value = updated_program

        response = self.client.delete(f"/programs/{updated_program.id}")

        # Then
        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
        radio_programs_mock.delete.assert_called_once_with(
            program_id=updated_program.id
        )

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_delete_program_raises_404_if_not_found(self, radio_programs_mock):
        """Delete RadioProgram should raise 404 if RadioProgram does not exist."""
        # Given
        delete_program = radio_program("test program get not found")
        radio_programs_mock.delete.side_effect = DynamoDbItemNotFoundError(
            f"RadioProgram with id {delete_program.id} does not exist."
        )

        # When
        response = self.client.delete(f"/programs/{delete_program.id}")

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        radio_programs_mock.delete.assert_called_once_with(program_id=delete_program.id)

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_delete_program_raises_500_dynamodb_client_error(self, radio_programs_mock):
        """Delete RadioProgram should raise 500 if DynamoDbClientError."""
        # Given
        delete_program = radio_program("test program get not found")
        radio_programs_mock.delete.side_effect = DynamoDbClientError(
            "Failed to delete item from DynamoDB: test error"
        )

        # When
        response = self.client.delete(f"/programs/{delete_program.id}")

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.delete.assert_called_once_with(program_id=delete_program.id)

    @mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
    def test_delete_program_raises_500_dynamodb_status_error(self, radio_programs_mock):
        """Delete RadioProgram should raise 500 if DynamoDbStatusError."""
        # Given
        delete_program = radio_program("test program get not found")
        radio_programs_mock.delete.side_effect = DynamoDbStatusError(
            "Failed to delete item from DynamoDB: test error"
        )

        # When
        response = self.client.delete(f"/programs/{delete_program.id}")

        # Then
        assert (
            response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ), response.text
        radio_programs_mock.delete.assert_called_once_with(program_id=delete_program.id)
