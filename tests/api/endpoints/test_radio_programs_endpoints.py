"""Test /programs endpoints."""
from unittest import mock

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
from audio_api.aws.dynamodb.exceptions import DynamoDbClientError
from audio_api.aws.s3.exceptions import S3ClientError, S3PersistenceError
from audio_api.domain.exceptions import RadioProgramNotFoundError
from tests.api.test_utils import create_temp_file, radio_program


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_get_program(
    radio_programs_mock,
    client: TestClient,
):
    """Get a program by id."""
    # Given
    get_program = radio_program(title="Test program get")
    radio_programs_mock.get.return_value = get_program
    expected = RadioProgramGetSchema.from_orm(get_program)

    # When
    response = client.get(f"/programs/{get_program.id}")
    received = RadioProgramListSchema.parse_obj(response.json())

    # Then
    assert response.status_code == status.HTTP_200_OK, response.text
    assert received == expected
    radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_get_program_raises_404_if_not_found(
    radio_programs_mock,
    client: TestClient,
):
    """Get an empty list of accounts if none created."""
    # Given
    get_program = radio_program("test program get not found")
    radio_programs_mock.get.side_effect = RadioProgramNotFoundError(
        f"RadioProgram with id {get_program.id} does not exist."
    )

    # When
    response = client.get(f"/programs/{get_program.id}")

    # Then
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_get_program_raises_500_if_dynamodb_client_error(
    radio_programs_mock,
    client: TestClient,
):
    """Get RadioProgram should raise 500 if DynamoDbClientError."""
    # Given
    get_program = radio_program("test program")
    radio_programs_mock.get.side_effect = DynamoDbClientError(
        "Failed to get item from DynamoDB: test error"
    )

    # When
    response = client.get(f"/programs/{get_program.id}")

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.get.assert_called_once_with(program_id=get_program.id)


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_list_programs(
    radio_programs_mock,
    client: TestClient,
):
    """Get a list of programs."""
    # Given
    radio_programs = [
        radio_program(title="Test program list #1"),
        radio_program(title="Test program list #2"),
    ]
    radio_programs_mock.get_all.return_value = radio_programs
    expected = [RadioProgramListSchema.from_orm(program) for program in radio_programs]

    # When
    response = client.get("/programs")
    received = [
        RadioProgramListSchema.parse_obj(program) for program in response.json()
    ]

    # Then
    assert response.status_code == status.HTTP_200_OK, response.text
    assert received == expected
    radio_programs_mock.get_all.assert_called_once()


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_list_radio_programs_empty(
    radio_programs_mock,
    client: TestClient,
):
    """Get an empty list of programs if none created."""
    # Given
    radio_programs_mock.get_all.return_value = []

    # When
    response = client.get("/programs")

    # Then
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == []
    radio_programs_mock.get_all.assert_called_once()


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_list_programs_raises_500_if_dynamodb_client_error(
    radio_programs_mock,
    client: TestClient,
):
    """Get RadioPrograms list should raise 500 if DynamoDbClientError."""
    # Given
    radio_programs_mock.get_all.side_effect = DynamoDbClientError(
        "Failed to get items from DynamoDB: test error"
    )

    # When
    response = client.get("/programs")

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.get_all.assert_called_once()


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_create_program(
    radio_programs_mock,
    client: TestClient,
):
    """Create a RadioProgram via POST."""
    # Given
    created_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
    radio_programs_mock.create.return_value = created_program
    expected = RadioProgramCreateOutSchema.parse_obj(created_program.dict())

    # When
    response = client.post(
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
def test_create_program_without_file_raises_error(
    radio_programs_mock,
    client: TestClient,
):
    """Create a RadioProgram via POST."""
    # Given
    created_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**created_program.dict())

    # When
    response = client.post("/programs", data=radio_program_in.dict())

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text


def test_create_program_without_radio_program_title_raises_error(
    client: TestClient,
):
    """Cannot create a RadioProgram via POST without required title."""
    # Given
    data_to_send = {
        "description": "program_without_title",
    }

    # When
    response = client.post("/programs", data=data_to_send, files=create_temp_file())

    # Then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_create_program_raises_500_if_s3_client_error(
    radio_programs_mock,
    client: TestClient,
):
    """Create RadioProgram should raise 500 if S3ClientError."""
    # Given
    created_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
    radio_programs_mock.create.side_effect = S3ClientError(
        "Failed to get response from S3: test error"
    )

    # When
    response = client.post(
        "/programs", data=radio_program_in.dict(), files=create_temp_file()
    )

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.create.assert_called_once_with(
        radio_program=radio_program_in, program_file=mock.ANY
    )


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_create_program_raises_500_if_s3_persistence_error(
    radio_programs_mock,
    client: TestClient,
):
    """Create RadioProgram should raise 500 if S3PersistenceError."""
    # Given
    created_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
    radio_programs_mock.create.side_effect = S3PersistenceError(
        "Unsuccessful S3 put_object response. Status: test error"
    )

    # When
    response = client.post(
        "/programs", data=radio_program_in.dict(), files=create_temp_file()
    )

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.create.assert_called_once_with(
        radio_program=radio_program_in, program_file=mock.ANY
    )


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_create_program_raises_500_if_dynamodb_client_error(
    radio_programs_mock,
    client: TestClient,
):
    """Create RadioProgram should raise 500 if DynamoDbClientError."""
    # Given
    created_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**created_program.dict())
    radio_programs_mock.create.side_effect = DynamoDbClientError(
        "Failed to store new item in DynamoDB: test error"
    )

    # When
    response = client.post(
        "/programs", data=radio_program_in.dict(), files=create_temp_file()
    )

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.create.assert_called_once_with(
        radio_program=radio_program_in, program_file=mock.ANY
    )


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_update_program(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram via PUT."""
    # Given
    updated_program = radio_program(title="test_program_update")
    radio_programs_mock.update.return_value = updated_program
    data_to_send = RadioProgramUpdateInSchema(**updated_program.dict())
    expected = RadioProgramUpdateOutSchema.parse_obj(updated_program.dict())

    # When
    response = client.put(
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
def test_update_program_without_file(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram via PUT without file."""
    # Given
    updated_program = radio_program(title="test_program_update")
    radio_programs_mock.update.return_value = updated_program
    data_to_send = RadioProgramUpdateInSchema(**updated_program.dict())
    expected = RadioProgramUpdateOutSchema.parse_obj(updated_program.dict())

    # When
    response = client.put(f"/programs/{updated_program.id}", data=data_to_send.dict())
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
def test_update_program_file(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram file via PUT."""
    # Given
    updated_program = radio_program(title="test_program_update")
    radio_programs_mock.update.return_value = updated_program
    expected = RadioProgramUpdateOutSchema.parse_obj(updated_program.dict())

    # When
    response = client.put(f"/programs/{updated_program.id}", files=create_temp_file())
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
def test_edit_account_raises_if_not_found(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram raises 404 if program is not found."""
    # Given
    updated_program = radio_program(title="test_program_update")
    data_to_send = RadioProgramUpdateInSchema(**updated_program.dict())
    radio_programs_mock.update.side_effect = RadioProgramNotFoundError(
        f"RadioProgram with id {updated_program.id} does not exist."
    )

    response = client.put(f"/programs/{updated_program.id}", data=data_to_send.dict())

    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    radio_programs_mock.update.assert_called_once_with(
        program_id=updated_program.id,
        new_program=data_to_send,
        program_file=None,
    )


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_update_program_raises_500_if_s3_client_error(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram should raise 500 if S3ClientError."""
    # Given
    updated_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
    radio_programs_mock.update.side_effect = S3ClientError(
        "Failed to get response from S3: test error"
    )

    # When
    response = client.put(
        f"/programs/{updated_program.id}",
        data=radio_program_in.dict(),
        files=create_temp_file(),
    )

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.update.assert_called_once_with(
        program_id=updated_program.id,
        new_program=radio_program_in,
        program_file=mock.ANY,
    )


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_update_program_raises_500_if_s3_persistence_error(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram should raise 500 if S3PersistenceError."""
    # Given
    updated_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
    radio_programs_mock.update.side_effect = S3PersistenceError(
        "Unsuccessful S3 put_object response. Status: test error"
    )

    # When
    response = client.put(
        f"/programs/{updated_program.id}",
        data=radio_program_in.dict(),
        files=create_temp_file(),
    )

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.update.assert_called_once_with(
        program_id=updated_program.id,
        new_program=radio_program_in,
        program_file=mock.ANY,
    )


@mock.patch("audio_api.api.endpoints.radio_programs.RadioPrograms")
def test_update_program_raises_500_if_dynamodb_client_error(
    radio_programs_mock,
    client: TestClient,
):
    """Update RadioProgram should raise 500 if DynamoDbClientError."""
    # Given
    updated_program = radio_program(title="Test program post")
    radio_program_in = RadioProgramCreateInSchema(**updated_program.dict())
    radio_programs_mock.update.side_effect = DynamoDbClientError(
        "Failed to store new item in DynamoDB: test error"
    )

    # When
    response = client.put(
        f"/programs/{updated_program.id}", data=radio_program_in.dict()
    )

    # Then
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    radio_programs_mock.update.assert_called_once_with(
        program_id=updated_program.id,
        new_program=radio_program_in,
        program_file=None,
    )
