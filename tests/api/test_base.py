"""Sanity check tests."""
import unittest

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from audio_api import version


@pytest.mark.usefixtures("test_client")
class TestApi(unittest.TestCase):
    """TestApi class."""

    client: TestClient

    def test_version(self):
        """Basic FastAPI version test."""
        response = self.client.get("/version")

        assert response.status_code == status.HTTP_200_OK
        assert "Audio API" in response.json()["title"]
        assert version.__version__ in response.json()["version"]

    def test_settings(self):
        """Basic FastAPI settings test."""
        response = self.client.get("/settings")

        assert response.status_code == status.HTTP_200_OK
