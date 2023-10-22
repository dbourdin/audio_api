"""RadioProgramFile Schemas."""

from audio_api.aws.s3.schemas import S3CreateSchema, S3FileSchema


class RadioProgramFile(S3FileSchema):
    """RadioProgramFile class."""


class RadioProgramFileCreate(S3CreateSchema):
    """RadioProgramFileCreate class."""
