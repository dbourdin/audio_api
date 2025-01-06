"""Test cases for AWS S3 models."""
import unittest
from tempfile import SpooledTemporaryFile

from audio_api.aws.s3.models import S3CreateModel
from tests.api.test_utils import MAX_FILE_SIZE


class TestAwsS3Models(unittest.TestCase):
    """TestAwsS3Models class."""

    def test_s3_create_model_slugifies_file_name(self):
        """Test S3CreateModel slugifies file_name."""
        # Given
        file_name = "Test File Name #001"
        expected = "test-file-name-001"
        temp_file = SpooledTemporaryFile(max_size=MAX_FILE_SIZE)

        # When
        s3_base_model = S3CreateModel(file_name=file_name, file=temp_file)

        # Then
        assert s3_base_model.file_name == expected
