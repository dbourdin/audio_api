"""Test RadioProgramFilesRepository."""
import unittest
from tempfile import SpooledTemporaryFile

import requests

from audio_api.aws.s3.models import S3CreateModel
from audio_api.aws.s3.repositories import radio_program_files_repository
from tests.aws.testcontainers.localstack import localstack_container


class TestRadioProgramFilesRepository(unittest.TestCase):
    """TestRadioProgramFilesRepository class."""

    _localstack_container = localstack_container
    _radio_program_files_repository = radio_program_files_repository

    @classmethod
    def setUpClass(cls):
        """Set up method to start localstack container before running the tests."""
        cls._localstack_container.start()

    @classmethod
    def tearDownClass(cls):
        """Teardown method to stop localstack container after running the tests."""
        cls._localstack_container.stop()

    def test_upload_file(self):
        """Test that we can upload a file successfully to S3."""
        created_file = SpooledTemporaryFile()
        radio_program_create_model = S3CreateModel(
            file_name="test radio program file",
            file=created_file,
        )
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )

        downloaded_file_response = requests.get(uploaded_file.file_url)

        # Verify the content of 'created_file' and 'downloaded_file_response.content'
        created_file.seek(0)  # Reset the cursor to the beginning of the file
        created_content = created_file.read()

        assert (
            created_content == downloaded_file_response.content
        ), "file content is different"
