"""Main pytest config file."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from audio_api.app import app
from audio_api.aws.dynamodb.models import RadioProgramPutItemModel
from audio_api.aws.dynamodb.repositories.radio_programs import RadioProgramsRepository
from audio_api.aws.dynamodb.repositories.radio_programs import (
    radio_programs_repository as db_repository,
)
from audio_api.aws.s3.repositories import (
    radio_program_files_repository as program_files_repository,
)
from audio_api.aws.s3.repositories.radio_program_files import (
    RadioProgramFilesRepository,
)
from tests.api.test_utils import create_upload_file, radio_program
from tests.aws.testcontainers.localstack import localstack_container

TEST_AUDIO_FILE = (
    Path(__file__).resolve().parent.joinpath("utils", "test_audio_file.mp3")
)


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
def radio_program_files_repository(request) -> RadioProgramFilesRepository:
    """Return a RadioProgramsRepository."""
    request.cls.radio_program_files_repository = program_files_repository
    return db_repository


@pytest.fixture(scope="class")
def create_program_model(request) -> RadioProgramPutItemModel:
    """Return an RadioProgramPutItemModel instance."""
    put_item_model = RadioProgramPutItemModel(
        **radio_program(title="test program").dict()
    )
    request.cls.create_program_model = put_item_model
    return put_item_model


@pytest.fixture(scope="class")
def upload_file(request):
    """Return an UploadFileModel instance."""
    upload_file = create_upload_file(TEST_AUDIO_FILE)
    request.cls.upload_file = upload_file
    return upload_file


@pytest.fixture(scope="class")
def new_upload_file(request):
    """Return an UploadFileModel instance."""
    new_upload_file = create_upload_file(TEST_AUDIO_FILE)
    request.cls.new_upload_file = new_upload_file
    return new_upload_file
