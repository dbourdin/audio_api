"""Test cases for AWS S3 models."""
import unittest

from audio_api.aws.s3.models import S3BaseModel


class TestAwsS3Models(unittest.TestCase):
    """TestAwsS3Models class."""

    def test_s3_base_model_slugifies_file_name(self):
        """Test S3BaseModel slugifies file_name."""
        # Given
        file_name = "Test File Name #001.mp3"
        expected = "test-file-name-001.mp3"

        # When
        s3_base_model = S3BaseModel(file_name=file_name)

        # Then
        assert s3_base_model.file_name == expected
