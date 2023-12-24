"""TestRadioProgramsRepository fixtures."""
import pytest

from audio_api.aws.dynamodb.models import RadioProgramUpdateItemModel


@pytest.fixture(scope="class")
def update_program_model(request) -> RadioProgramUpdateItemModel:
    """Return an RadioProgramUpdateItemModel instance."""
    update_item_model = RadioProgramUpdateItemModel(title="updated program")
    request.cls.update_program_model = update_item_model
    return update_item_model
