"""Test RadioProgramFilesRepository."""
import unittest
from pathlib import Path
from tempfile import SpooledTemporaryFile

import requests
from starlette.datastructures import Headers, UploadFile

from audio_api.aws.s3.models import S3CreateModel
from audio_api.aws.s3.repositories import radio_program_files_repository
from tests.aws.testcontainers.localstack import localstack_container

TEST_AUDIO_FILE = "test_audio_file.mp3"


class TestRadioProgramFilesRepository(unittest.TestCase):
    """TestRadioProgramFilesRepository class."""

    _localstack_container = localstack_container
    _radio_program_files_repository = radio_program_files_repository
    _test_audio_file = Path(__file__).resolve().parent.joinpath(TEST_AUDIO_FILE)
    _max_file_size = 1024 * 1024

    def _get_upload_file(
        self, file: Path = _test_audio_file
    ) -> tuple[UploadFile, bytes]:
        """Open a file and creates an UploadFile object.

        Args:
            file: File to upload.

        Returns:
            UploadFile: File to upload wrapped in UploadFile model.
            bytes: File content to be uploaded.
        """
        file_name = file.name
        headers = {
            "content-disposition": (
                f'form-data; name="program_file"; filename="{file_name}'
            ),
            # TODO: Extract from file?
            "content-type": "audio/mpeg",
        }
        headers = Headers(headers=headers)
        tempfile = SpooledTemporaryFile(max_size=self._max_file_size)
        upload_file = UploadFile(
            file=tempfile, size=0, filename=file_name, headers=headers
        )
        with open(file, "rb") as f:
            file_content = f.read()
        upload_file.file.write(file_content)
        upload_file.file.seek(0)
        return upload_file, file_content

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
        # Given
        upload_file, content = self._get_upload_file()
        file_name = upload_file.filename.split(".")[0]
        radio_program_create_model = S3CreateModel(
            file_name=file_name,
            file=upload_file.file,
        )

        # When
        uploaded_file = self._radio_program_files_repository.put_object(
            radio_program_create_model
        )
        downloaded_file_response = requests.get(uploaded_file.file_url)

        # Then
        assert downloaded_file_response.content == content, "file content is different"
        assert file_name in uploaded_file.file_name
        assert file_name in uploaded_file.file_url
