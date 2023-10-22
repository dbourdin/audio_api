"""RadioProgramFile Schemas."""

from audio_api.aws.s3.schemas import S3BaseSchema


class RadioProgramFileSchema(S3BaseSchema):
    """RadioProgramFileSchema class."""

    program_length: int | None
