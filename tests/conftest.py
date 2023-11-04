"""Main pytest config file."""

import pytest
from fastapi.testclient import TestClient

from audio_api.app import app


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    return TestClient(app)
