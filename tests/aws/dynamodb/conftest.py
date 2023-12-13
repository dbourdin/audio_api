"""TestRadioProgramsRepository fixtures."""
import pytest

from audio_api.aws.dynamodb.models import (
    RadioProgramPutItemModel,
    RadioProgramUpdateItemModel,
)
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.dynamodb.repositories.radio_programs import (
    radio_programs_repository as db_repository,
)
from tests.api.test_utils import radio_program


@pytest.fixture(scope="class")
def create_program_model(request) -> RadioProgramPutItemModel:
    """Return an RadioProgramPutItemModel instance."""
    put_item_model = RadioProgramPutItemModel(
        **radio_program(title="test program").dict()
    )
    request.cls.create_program_model = put_item_model
    return put_item_model


@pytest.fixture(scope="class")
def update_program_model(request) -> RadioProgramUpdateItemModel:
    """Return an RadioProgramUpdateItemModel instance."""
    update_item_model = RadioProgramUpdateItemModel(title="updated program")
    request.cls.update_program_model = update_item_model
    return update_item_model


@pytest.fixture(scope="class")
def radio_programs_repository(request) -> RadioProgramsRepository:
    """Return a RadioProgramsRepository."""
    request.cls.radio_programs_repository = db_repository
    return db_repository
