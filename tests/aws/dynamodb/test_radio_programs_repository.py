"""Test TestRadioProgramsRepository."""
import unittest
from unittest import mock
from uuid import uuid4

import pytest
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from audio_api.aws.dynamodb.exceptions import (
    DynamoDbClientError,
    DynamoDbItemNotFoundError,
    DynamoDbStatusError,
)
from audio_api.aws.dynamodb.models import (
    RadioProgramPutItemModel,
    RadioProgramUpdateItemModel,
)
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

    def test_get_item(self):
        """Should retrieve a RadioProgram from dynamodb."""
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

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_get_item_raises_dynamodb_client_error(self, table_mock: mock.patch):
        """Should raise DynamoDbClientError if table.query raises ClientError."""
        # When
        item_id = uuid4()
        table_mock.query.side_effect = ClientError(
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs_repository.get_item(item_id=item_id)
        table_mock.query.assert_called_once_with(
            ScanIndexForward=False, KeyConditionExpression=Key("id").eq(str(item_id))
        )

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_get_item_raises_dynamodb_status_error(self, table_mock: mock.patch):
        """Should raise DynamoDbStatusError if table.query status code is not 200."""
        # Given
        item_id = uuid4()

        # When
        table_mock.query.return_value = {"ResponseMetadata": {"HTTPStatsCode": 500}}

        # Then
        with pytest.raises(DynamoDbStatusError):
            self.radio_programs_repository.get_item(item_id=item_id)
        table_mock.query.assert_called_once_with(
            ScanIndexForward=False, KeyConditionExpression=Key("id").eq(str(item_id))
        )

    def test_get_item_raises_dynamodb_item_not_found_error(self):
        """Should raise DynamoDbItemNotFoundError if item does not exist."""
        # Then
        with pytest.raises(DynamoDbItemNotFoundError):
            self.radio_programs_repository.get_item(item_id=uuid4())

    def test_get_items(self):
        """Should retrieve a list of RadioPrograms from dynamodb."""
        # Given
        radio_program_1 = self.radio_programs_repository.put_item(
            item=self.create_program_model
        )
        radio_program_2 = self.radio_programs_repository.put_item(
            item=self.create_program_model
        )
        expected_radio_programs = sorted(
            [radio_program_1, radio_program_2], key=lambda x: x.id
        )

        # When
        db_radio_programs = self.radio_programs_repository.get_items()

        # Then
        assert sorted(db_radio_programs, key=lambda x: x.id) == expected_radio_programs

    def test_get_items_returns_empty_list_if_no_radio_program(self):
        """Should retrieve a list of RadioPrograms from dynamodb."""
        # Given
        expected_radio_programs = []

        # When
        db_radio_programs = self.radio_programs_repository.get_items()

        # Then
        assert db_radio_programs == expected_radio_programs

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_get_items_raises_dynamodb_client_error(self, table_mock: mock.patch):
        """Should raise DynamoDbClientError if table.scan raises ClientError."""
        # When
        table_mock.scan.side_effect = ClientError(
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs_repository.get_items()
        table_mock.scan.assert_called_once()

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_get_items_raises_dynamodb_status_error(self, table_mock: mock.patch):
        """Should raise DynamoDbStatusError if table.scan status code is not 200."""
        # When
        table_mock.scan.return_value = {"ResponseMetadata": {"HTTPStatsCode": 500}}

        # Then
        with pytest.raises(DynamoDbStatusError):
            self.radio_programs_repository.get_items()
        table_mock.scan.assert_called_once()

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
        table_mock.put_item.assert_called_once()

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_put_item_raises_dynamodb_status_error(self, table_mock: mock.patch):
        """Should raise DynamoDbStatusError if put_item status code is not 200."""
        # When
        table_mock.put_item.return_value = {"ResponseMetadata": {"HTTPStatsCode": 500}}

        # Then
        with pytest.raises(DynamoDbStatusError):
            self.radio_programs_repository.put_item(item=self.create_program_model)
        table_mock.put_item.assert_called_once()

    def test_update_item(self):
        """Should successfully update an existing RadioProgram."""
        # Given
        created_program = self.radio_programs_repository.put_item(
            item=self.create_program_model
        )

        update_program_model = RadioProgramUpdateItemModel(**created_program.dict())
        update_program_model.title = "updated program"
        expected_program = created_program.copy(update=update_program_model.dict())

        # When
        updated_program = self.radio_programs_repository.update_item(
            item_id=created_program.id, item=update_program_model
        )

        # Then
        assert updated_program == expected_program
        assert updated_program != created_program

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_update_item_raises_dynamodb_client_error(self, table_mock: mock.patch):
        """Should raise DynamoDbClientError if update_item raises ClientError."""
        # Given
        item_id = uuid4()
        update_program_model = RadioProgramUpdateItemModel(
            **self.create_program_model.dict()
        )

        # When
        table_mock.update_item.side_effect = ClientError(
            error_response={"Error": {"Code": 500, "Message": "test_error"}},
            operation_name="test_error",
        )

        # Then
        with pytest.raises(DynamoDbClientError):
            self.radio_programs_repository.update_item(
                item_id=item_id, item=update_program_model
            )
        table_mock.update_item.assert_called_once()

    @mock.patch(DYNAMODB_TABLE_MOCK_PATH)
    def test_update_item_raises_dynamodb_status_error(self, table_mock: mock.patch):
        """Should raise DynamoDbStatusError if update_item status code is not 200."""
        # Given
        item_id = uuid4()
        update_program_model = RadioProgramUpdateItemModel(
            **self.create_program_model.dict()
        )

        # When
        table_mock.update_item.return_value = {
            "ResponseMetadata": {"HTTPStatsCode": 500}
        }

        # Then
        with pytest.raises(DynamoDbStatusError):
            self.radio_programs_repository.update_item(
                item_id=item_id, item=update_program_model
            )
        table_mock.update_item.assert_called_once()
