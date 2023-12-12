"""AWS fixtures."""
import pytest

from tests.aws.testcontainers.localstack import localstack_container


@pytest.fixture(scope="session")
def localstack(request):
    """Run LocalStack Container in a test session."""
    with localstack_container:
        yield localstack_container
