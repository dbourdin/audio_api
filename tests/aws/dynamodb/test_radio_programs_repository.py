"""Test TestRadioProgramsRepository."""
import unittest
from unittest import mock

import pytest
from botocore.exceptions import ClientError

from audio_api.aws.dynamodb.exceptions import (
    DynamoDbClientError,
    DynamoDbPersistenceError,
)
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository

DYNAMODB_TABLE_MOCK_PATH = (
    "audio_api.aws.dynamodb.repositories.radio_programs.radio_programs_repository.table"
)


@pytest.mark.usefixtures("localstack")
@pytest.mark.usefixtures("radio_programs_repository")
@pytest.mark.usefixtures("create_program_model")
class TestRadioProgramsRepository(unittest.TestCase):
    """TestRadioProgramsRepository class."""

    radio_programs_repository: RadioProgramsRepository
    create_program_model: RadioProgramPutItemModel

    @pytest.fixture(autouse=True)
    def _empty_table(self):
        self.radio_programs_repository.delete_all()

    def test_put_item(self):
        """Should successfully create a new RadioProgram."""
        # When
        created_program = self.radio_programs_repository.put_item(
            item=self.create_program_model
        )
        created_program_dict = created_program.dict()

        # Then
        assert created_program.id is not None
        assert all(
            key in created_program_dict and created_program_dict[key] == value
            for key, value in self.create_program_model.dict().items()
        )

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_put_item_raises_dynamodb_client_error(self, table_mock: mock.patch):
        """Should raise DynamoDbClientError if put_item raises ClientError."""
        # When
        table_mock.put_item.side_effect = ClientError(
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs_repository.put_item(item=self.create_program_model)

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_put_item_raises_dynamodb_persistence_error(self, table_mock: mock.patch):
        """Should raise DynamoDbPersistenceError if put_item status code is not 200."""
        # When
        table_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatsCode": 500}}

        # Then
        with pytest.raises(DynamoDbPersistenceError):
            self.radio_programs_repository.put_item(item=self.create_program_model)

    def test_get_item(self):
        """Should retrieve an item from dynamodb."""
        # Given
        expected_radio_program = self.radio_programs_repository.put_item(
            item=self.create_program_model
        )

        # When
        db_radio_program = self.radio_programs_repository.get_item(
            item_id=expected_radio_program.id
        )

        # Then
        assert db_radio_program == expected_radio_program
