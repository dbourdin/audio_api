"""Sanity check tests."""

from fastapi import status
from fastapi.testclient import TestClient

from audio_api import version


def test_version(client: TestClient):
    """Basic FastAPI version test."""
    response = client.get("/version")

    assert response.status_code == status.HTTP_200_OK
    assert "Audio API" in response.json()["title"]
    assert version.__version__ in response.json()["version"]


def test_settings(client: TestClient):
    """Basic FastAPI settings test."""
    response = client.get("/settings")

    assert response.status_code == status.HTTP_200_OK
