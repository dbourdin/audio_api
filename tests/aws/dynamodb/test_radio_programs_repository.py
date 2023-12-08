"""Test TestRadioProgramsRepository."""
import pytest

from audio_api.aws.dynamodb.models import (
    RadioProgramItemModel,
    RadioProgramPutItemModel,
)
from audio_api.aws.dynamodb.repositories import radio_programs_repository
from tests.api.test_utils import radio_program
from tests.aws.testcontainers.localstack import LocalStackContainerTest


@pytest.fixture(scope="class")
def create_program_model(request):
    """Return an RadioProgramPutItemModel instance."""
    put_item_model = RadioProgramPutItemModel(
        **radio_program(title="test program").dict()
    )
    request.cls.create_program_model = put_item_model
    return put_item_model


@pytest.mark.usefixtures("create_program_model")
class TestRadioProgramsRepository(LocalStackContainerTest):
    """TestRadioProgramsRepository class."""

    _radio_programs_repository = radio_programs_repository
    create_program_model: RadioProgramItemModel

    @pytest.fixture(autouse=True)
    def _empty_table(self):
        self._radio_programs_repository.delete_all()

    def test_get_item(self):
        """Should retrieve an item from dynamodb."""
        # Given
        expected_radio_program = radio_programs_repository.put_item(
            item=self.create_program_model
        )

        # When
        db_radio_program = self._radio_programs_repository.get_item(
            item_id=expected_radio_program.id
        )

        # Then
        assert db_radio_program == expected_radio_program
