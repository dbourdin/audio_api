"""S3BaseSchema class."""

from audio_api.schemas import APISchema


class S3BaseSchema(APISchema):
    """S3BaseSchema class."""

    file_name: str | None
    file_url: str | None
