"""AWS fixtures."""
import pytest

from tests.aws.testcontainers.localstack import LocalStackContainer
from tests.aws.testcontainers.localstack import (
    localstack_container as localstack_container_,
)


@pytest.fixture(scope="session")
def localstack_container(request) -> LocalStackContainer:
    """Run LocalStack Container in a test session."""
    with localstack_container_:
        yield localstack_container_
