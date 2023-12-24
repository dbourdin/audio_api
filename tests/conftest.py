"""Main pytest config file."""

import pytest
from fastapi.testclient import TestClient

from audio_api.app import app
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.dynamodb.repositories.radio_programs import (
    radio_programs_repository as db_repository,
)
from tests.api.test_utils import radio_program
from tests.aws.testcontainers.localstack import localstack_container


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    return TestClient(app)


@pytest.fixture(scope="session")
def localstack(request):
    """Run LocalStack Container in a test session."""
    with localstack_container:
        yield localstack_container


@pytest.fixture(scope="class")
def radio_programs_repository(request) -> RadioProgramsRepository:
    """Return a RadioProgramsRepository."""
    request.cls.radio_programs_repository = db_repository
    return db_repository


@pytest.fixture(scope="class")
def create_program_model(request) -> RadioProgramPutItemModel:
    """Return an RadioProgramPutItemModel instance."""
    put_item_model = RadioProgramPutItemModel(
        # TODO: this should not be in tests/api
        **radio_program(title="test program").dict()
    )
    request.cls.create_program_model = put_item_model
    return put_item_model
