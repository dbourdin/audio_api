"""RadioProgramFile Models."""

from audio_api.aws.s3.models import S3CreateModel, S3FileModel


class RadioProgramFile(S3FileModel):
    """RadioProgramFile class."""


class RadioProgramFileCreate(S3CreateModel):
    """RadioProgramFileCreate class."""
