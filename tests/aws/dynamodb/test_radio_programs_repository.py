"""Test TestRadioProgramsRepository."""
import pytest

from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from tests.aws.testcontainers.localstack import LocalStackContainerTest


@pytest.mark.usefixtures("radio_programs_repository")
@pytest.mark.usefixtures("create_program_model")
class TestRadioProgramsRepository(LocalStackContainerTest):
    """TestRadioProgramsRepository class."""

    radio_programs_repository: RadioProgramsRepository
    create_program_model: RadioProgramPutItemModel

    @pytest.fixture(autouse=True)
    def _empty_table(self):
        self.radio_programs_repository.delete_all()

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
